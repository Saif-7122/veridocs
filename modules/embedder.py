"""
Embedder module — local sentence-transformers embeddings, zero API cost.

Model : all-MiniLM-L6-v2
  • 384-dimensional output
  • ~80 MB footprint, loads in ~1 s on CPU
  • Fast enough for real-time query embedding; batch encode for documents

Design decisions:
  • Singleton pattern — model is loaded once per process and reused.
  • Thread-safety — a threading.Lock guards the first-load critical section.
  • Batch size is tunable (default 64) to balance memory vs. throughput.
  • normalize_embeddings=True so cosine similarity == dot product,
    which makes FAISS scoring consistent and distances meaningful.
"""

import logging
import threading
from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singleton state
# ---------------------------------------------------------------------------

MODEL_NAME  = "all-MiniLM-L6-v2"
EMBED_DIM   = 384          # fixed output dimension for this model
BATCH_SIZE  = 64           # number of texts to encode per forward pass

_model: Optional[SentenceTransformer] = None
_lock  = threading.Lock()  # guards first-load


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_model() -> SentenceTransformer:
    """
    Return the shared SentenceTransformer singleton.

    Thread-safe double-checked locking: the model is downloaded/loaded only
    once even when multiple requests arrive concurrently at cold start.
    Subsequent calls return in microseconds (no lock contention).
    """
    global _model

    if _model is not None:          # fast path — already loaded
        return _model

    with _lock:                     # slow path — first caller loads the model
        if _model is None:          # re-check inside lock (double-checked)
            logger.info("Loading sentence-transformer model: %s", MODEL_NAME)
            _model = SentenceTransformer(MODEL_NAME)
            logger.info(
                "Model loaded — embedding dim: %d", _model.get_embedding_dimension()
            )

    return _model


def embed_chunks(
    chunks: list[dict],
    batch_size: int = BATCH_SIZE,
    show_progress: bool = False,
) -> np.ndarray:
    """
    Encode a list of chunk dicts into a float32 embedding matrix.

    Args:
        chunks:        List of chunk dicts; each must have a ``"text"`` key.
        batch_size:    Texts per forward pass (tune for available RAM).
        show_progress: Show a tqdm progress bar (useful for large corpora).

    Returns:
        numpy array of shape ``(len(chunks), EMBED_DIM)`` in float32.

    Raises:
        ValueError: If ``chunks`` is empty.
        KeyError:   If any chunk dict lacks a ``"text"`` key.
    """
    if not chunks:
        raise ValueError("embed_chunks received an empty chunks list.")

    texts = [c["text"] for c in chunks]   # raises KeyError if "text" missing

    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        normalize_embeddings=True,         # unit-norm → cosine ≡ dot product
        convert_to_numpy=True,
    )

    return embeddings.astype(np.float32)


def embed_query(query: str) -> np.ndarray:
    """
    Encode a single query string into a 1-D float32 embedding vector.

    Args:
        query: Raw query string (not tokenised — model handles that).

    Returns:
        numpy array of shape ``(EMBED_DIM,)`` in float32.

    Raises:
        ValueError: If query is empty or whitespace-only.
    """
    if not query or not query.strip():
        raise ValueError("embed_query received an empty query string.")

    model = get_model()
    vector = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return vector[0].astype(np.float32)   # shape: (EMBED_DIM,)


def embedding_dim() -> int:
    """Return the output dimension of the current model (384 for MiniLM-L6-v2)."""
    return EMBED_DIM
