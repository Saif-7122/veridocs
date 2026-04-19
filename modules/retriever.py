"""
Retriever module — hybrid FAISS (semantic) + BM25 (keyword) search.
Combines both scores with weighted fusion for better retrieval quality.
"""

import math
import numpy as np
from typing import Any
import faiss
from rank_bm25 import BM25Okapi


def build_faiss_index(embeddings: np.ndarray) -> Any:
    """
    Build a FAISS flat L2 index from embedding matrix.
    
    Args:
        embeddings: Float32 numpy array of shape (N, D).
        
    Returns:
        A populated faiss.IndexFlatL2 object.
    """
    if len(embeddings.shape) != 2:
        raise ValueError("Embeddings must be a 2D numpy array.")
    if embeddings.shape[0] == 0:
        raise ValueError("Cannot build index for empty embeddings.")
        
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    # Ensure it's float32 and C-contiguous as required by FAISS
    embeddings_f32 = np.ascontiguousarray(embeddings, dtype=np.float32)
    index.add(embeddings_f32)
    return index


def build_bm25_index(chunks: list[dict]) -> Any:
    """
    Build a BM25 index from chunk texts.
    
    Args:
        chunks: List of chunk dictionaries containing 'text' keys.
        
    Returns:
        A populated BM25Okapi object.
    """
    if not chunks:
        raise ValueError("Cannot build BM25 index for empty chunks.")
        
    tokenized_corpus = []
    for c in chunks:
        text = c.get("text", "")
        # Basic whitespace tokenization and lowercasing
        tokens = text.lower().split()
        tokenized_corpus.append(tokens)
        
    return BM25Okapi(tokenized_corpus)


def hybrid_search(
    query: str,
    query_embedding: np.ndarray,
    faiss_index: Any,
    bm25_index: Any,
    chunks: list[dict],
    top_k: int = 6,
    semantic_weight: float = 0.6,
    keyword_weight: float = 0.4,
) -> list[dict]:
    """
    Run both searches, normalize scores, combine with weights, return top_k chunks.
    
    Returns list of chunk dicts (shallow copies) with an added "score" field, 
    sorted descending.
    """
    n_chunks = len(chunks)
    if n_chunks == 0:
        return []
    
    search_k = min(n_chunks, top_k)
    
    # ── 1. FAISS (Semantic) Search ──
    # query_embedding shape is (D,), make it (1, D) for FAISS
    q_emb = np.ascontiguousarray(query_embedding.reshape(1, -1), dtype=np.float32)
    distances, indices = faiss_index.search(q_emb, n_chunks)  # get distances to all for fusion
    
    faiss_scores = np.zeros(n_chunks, dtype=np.float32)
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            dist = distances[0][i]
            # Convert L2 distance to similarity score: 1 / (1 + dist)
            faiss_scores[idx] = 1.0 / (1.0 + float(dist))
            
    # Normalize FAISS scores to [0, 1] across the corpus
    f_min, f_max = faiss_scores.min(), faiss_scores.max()
    if f_max > f_min:
        faiss_norm = (faiss_scores - f_min) / (f_max - f_min)
    else:
        faiss_norm = faiss_scores  # avoid division by zero if all scores are identical
        
    # ── 2. BM25 (Keyword) Search ──
    query_tokens = query.lower().split()
    bm25_scores = bm25_index.get_scores(query_tokens)
    
    # Normalize BM25 scores to [0, 1] across the corpus
    b_min, b_max = bm25_scores.min(), bm25_scores.max()
    if b_max > b_min:
        bm25_norm = (bm25_scores - b_min) / (b_max - b_min)
    else:
        # If no keywords matched anywhere, all scores will be 0.0
        bm25_norm = np.zeros(n_chunks, dtype=np.float32) if b_max == 0 else bm25_scores
        
    # ── 3. Weighted Fusion ──
    combined_scores = semantic_weight * faiss_norm + keyword_weight * bm25_norm
    
    # ── 4. Build Results and Sort ──
    # Pair indices with combined_scores, sort by score descending
    scored_indices = [
        (i, float(combined_scores[i])) 
        for i in range(n_chunks)
    ]
    scored_indices.sort(key=lambda x: x[1], reverse=True)
    
    # Get top_k
    results = []
    for i, score in scored_indices[:search_k]:
        # Shallow copy to avoid mutating the original session chunks
        chunk_copy = chunks[i].copy()
        chunk_copy["score"] = score
        results.append(chunk_copy)
        
    return results
