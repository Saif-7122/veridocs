"""
Tests for chat module.
Run with: pytest tests/test_chat.py
"""
import pytest
from unittest.mock import patch, MagicMock

from modules.chat import build_context_prompt, ask


@pytest.fixture
def mock_chunks():
    return [
        {"source": "docA.pdf", "page": 4, "text": "The payment is due within 30 days."},
        {"source": "docB.docx", "page": 1, "text": "Net 30 payment terms apply."}
    ]


def test_build_context_prompt_with_chunks(mock_chunks):
    query = "What are the payment terms?"
    prompt = build_context_prompt(query, mock_chunks)
    
    assert "CONTEXT:" in prompt
    assert "QUESTION:" in prompt
    assert query in prompt
    assert "[Source: docA.pdf, Page: 4]" in prompt
    assert "The payment is due within 30 days." in prompt
    assert "[Source: docB.docx, Page: 1]" in prompt


def test_build_context_prompt_empty():
    prompt = build_context_prompt("Hello", [])
    assert "No documents have been indexed" in prompt
    assert "Hello" in prompt


@patch("modules.chat._get_model")
def test_ask_returns_structured_dict(mock_get_model, mock_chunks):
    # Setup mock Gemini response
    mock_response = MagicMock()
    mock_response.text = "Based on the documents, payment is net 30 days."
    
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_get_model.return_value = mock_model
    
    # Call the actual function
    result = ask("What is the payment rule?", mock_chunks)
    
    # Assert correct calls
    mock_model.generate_content.assert_called_once()
    assert "CONTEXT:" in mock_model.generate_content.call_args[0][0]
    
    # Assert result structure
    assert isinstance(result, dict)
    assert result["answer"] == "Based on the documents, payment is net 30 days."
    assert result["model"] == "gemini-1.5-flash"
    
    # Citations should be deduped correctly
    assert len(result["citations"]) == 2
    assert result["citations"][0] == {"source": "docA.pdf", "page": 4}
    assert result["citations"][1] == {"source": "docB.docx", "page": 1}


@patch("modules.chat._get_model")
def test_ask_handles_duplicate_citations(mock_get_model):
    chunks = [
        {"source": "file.pdf", "page": 1, "text": "Duplicate 1"},
        {"source": "file.pdf", "page": 1, "text": "Duplicate 2"},
    ]
    
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "Response"
    mock_get_model.return_value = mock_model
    
    result = ask("query", chunks)
    
    assert len(result["citations"]) == 1
    assert result["citations"][0] == {"source": "file.pdf", "page": 1}
