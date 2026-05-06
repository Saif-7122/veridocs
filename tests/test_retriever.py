"""
Tests for retriever module.
Run with: pytest tests/test_retriever.py
"""
import pytest
import numpy as np

from modules.retriever import build_faiss_index, build_bm25_index, hybrid_search


@pytest.fixture
def sample_chunks():
    return [
        {"text": "The quick brown fox jumps over the lazy dog.", "source": "f1.pdf", "page": 1},
        {"text": "Fast brown foxes leap across sleeping dogs.", "source": "f1.pdf", "page": 2},
        {"text": "Artificial intelligence is transforming document analysis.", "source": "f2.docx", "page": 1},
        {"text": "Machine learning models like FAISS handle vector search well.", "source": "f2.docx", "page": 2},
    ]


@pytest.fixture
def sample_embeddings():
    # 4 chunks, 3 dimensions
    return np.array([
        [0.1, 0.2, 0.3],
        [0.1, 0.2, 0.4],
        [0.9, 0.8, 0.7],
        [0.8, 0.7, 0.6],
    ], dtype=np.float32)


def test_faiss_index_builds_without_error(sample_embeddings):
    index = build_faiss_index(sample_embeddings)
    assert index is not None
    assert index.ntotal == 4
    assert index.d == 3


def test_faiss_index_empty_raises_value_error():
    with pytest.raises(ValueError):
         build_faiss_index(np.array([], dtype=np.float32).reshape(0, 3))


def test_bm25_index_builds_without_error(sample_chunks):
    index = build_bm25_index(sample_chunks)
    assert index is not None
    # 'corpus_size' checks the number of indexed documents
    assert getattr(index, "corpus_size", len(sample_chunks)) == 4


def test_bm25_index_empty_raises_value_error():
    with pytest.raises(ValueError):
        build_bm25_index([])


def test_hybrid_search_returns_top_k(sample_chunks, sample_embeddings):
    faiss_index = build_faiss_index(sample_embeddings)
    bm25_index = build_bm25_index(sample_chunks)
    
    query = "artificial intelligence"
    query_emb = np.array([0.9, 0.9, 0.8], dtype=np.float32)
    
    # Request top 2 out of 4 chunks
    results = hybrid_search(
        query=query,
        query_embedding=query_emb,
        faiss_index=faiss_index,
        bm25_index=bm25_index,
        chunks=sample_chunks,
        top_k=2,
        semantic_weight=0.5,
        keyword_weight=0.5
    )
    
    assert isinstance(results, list)
    assert len(results) == 2
    
    # Check that score is injected
    assert "score" in results[0]
    assert "score" in results[1]
    
    # Result should be sorted descending
    assert results[0]["score"] >= results[1]["score"]
    
    # The chunk talking about AI should realistically be first 
    # since it shares words and has similar vector (0.9, 0.8, 0.7)
    assert "Artificial intelligence" in results[0]["text"]


def test_hybrid_search_empty_chunks():
    results = hybrid_search(
        query="test",
        query_embedding=np.array([0.1, 0.2]),
        faiss_index=None,
        bm25_index=None,
        chunks=[],
        top_k=3
    )
    assert results == []


def test_hybrid_search_k_larger_than_corpus(sample_chunks, sample_embeddings):
    faiss_index = build_faiss_index(sample_embeddings)
    bm25_index = build_bm25_index(sample_chunks)
    
    query = "fox"
    query_emb = np.array([0.1, 0.2, 0.35], dtype=np.float32)
    
    # Request top 100, but corpus only has 4 chunks
    results = hybrid_search(
        query=query,
        query_embedding=query_emb,
        faiss_index=faiss_index,
        bm25_index=bm25_index,
        chunks=sample_chunks,
        top_k=100
    )
    
    assert len(results) == 4
