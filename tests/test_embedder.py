"""
Tests for embedder module (Layer 2).
Run with: pytest tests/test_embedder.py -v
"""
import pytest
import numpy as np

from modules.embedder import (
    get_model,
    embed_chunks,
    embed_query,
    embedding_dim,
    MODEL_NAME,
    EMBED_DIM
)


class TestEmbedder:

    def test_embedding_dim(self):
        assert embedding_dim() == EMBED_DIM
        assert EMBED_DIM == 384

    def test_get_model_returns_sentence_transformer(self):
        model = get_model()
        # Ensure it's a SentenceTransformer type
        from sentence_transformers import SentenceTransformer
        assert isinstance(model, SentenceTransformer)
        
        # Verify it has the correct properties rather than unreliable internal names
        assert model.get_sentence_embedding_dimension() == EMBED_DIM

    def test_get_model_is_singleton(self):
        # The model should be instantiated only once
        model1 = get_model()
        model2 = get_model()
        assert model1 is model2  # Same object in memory

    def test_embed_chunks_returns_correct_shape(self):
        chunks = [
            {"text": "First chunk text here."},
            {"text": "Second chunk is a bit different."}
        ]
        embeddings = embed_chunks(chunks, show_progress=False)
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (2, EMBED_DIM)
        # Should be float32 for FAISS compatibility
        assert embeddings.dtype == np.float32
        
        # Verify normalization (L2 norm should be ~1.0)
        norms = np.linalg.norm(embeddings, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-5), f"Embeddings not normalized: norms = {norms}"

    def test_embed_chunks_empty_raises_value_error(self):
        with pytest.raises(ValueError, match="empty chunks list"):
            embed_chunks([])

    def test_embed_chunks_missing_text_raises_key_error(self):
        chunks = [{"wrong_key": "hello"}]
        with pytest.raises(KeyError):
            embed_chunks(chunks)

    def test_embed_query_returns_correct_shape(self):
        query = "What is the capital of France?"
        embedding = embed_query(query)
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (EMBED_DIM,)
        assert embedding.dtype == np.float32

        # Verify normalization
        norm = np.linalg.norm(embedding)
        assert np.isclose(norm, 1.0, atol=1e-5)

    def test_embed_query_empty_raises_value_error(self):
        with pytest.raises(ValueError, match="empty query string"):
            embed_query("")
        with pytest.raises(ValueError, match="empty query string"):
            embed_query("   ")
        with pytest.raises(ValueError, match="empty query string"):
            embed_query(None)  # type: ignore
