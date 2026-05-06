"""
Tests for insights module.
Run with: pytest tests/test_insights.py
"""
import pytest
import json
from unittest.mock import patch, MagicMock

from modules.insights import extract_themes, compare_documents, generate_report


@pytest.fixture
def sample_chunks():
    return [
        {"source": "f1.pdf", "text": "This is related to AI and machine learning."},
        {"source": "f1.pdf", "text": "Deep learning models are scaling up."},
        {"source": "f2.docx", "text": "Electric vehicles are the future of transport."},
        {"source": "f2.docx", "text": "Battery tech is improving rapidly."}
    ]


@patch("modules.insights._get_model")
def test_extract_themes_success(mock_get_model, sample_chunks):
    mock_response = MagicMock()
    mock_response.text = '["AI", "Machine Learning", "Deep Learning", "Scaling", "Models"]'
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_get_model.return_value = mock_model
    
    themes = extract_themes(sample_chunks, "f1.pdf")
    
    assert len(themes) == 5
    assert "AI" in themes
    assert mock_model.generate_content.called


@patch("modules.insights._get_model")
def test_extract_themes_handles_bad_json(mock_get_model, sample_chunks):
    mock_response = MagicMock()
    mock_response.text = 'This is not json'
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_get_model.return_value = mock_model
    
    themes = extract_themes(sample_chunks, "f1.pdf")
    assert themes == ["Error extracting themes"]


@patch("modules.insights._get_model")
def test_compare_documents_success(mock_get_model, sample_chunks):
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "agreements": ["Both are about tech."],
        "contradictions": [],
        "unique_to": {"f1.pdf": ["AI"], "f2.docx": ["EVs"]},
        "summary": "A comparison of tech."
    })
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_get_model.return_value = mock_model
    
    result = compare_documents(sample_chunks)
    
    assert "agreements" in result
    assert result["agreements"] == ["Both are about tech."]
    assert "summary" in result


def test_compare_documents_needs_two_docs():
    chunks = [{"source": "single.pdf", "text": "Alone."}]
    result = compare_documents(chunks)
    
    assert result["agreements"] == []
    assert "Need at least 2 documents" in result["summary"]


def test_generate_report():
    query_history = [
        {
            "query": "What is AI?", 
            "answer": "Artificial Intelligence is cool.",
            "citations": [{"source": "f1.pdf", "page": 1}]
        }
    ]
    comparison = {
        "agreements": ["Both agree on X"],
        "contradictions": ["Conflict on Y"],
        "unique_to": {"f1.pdf": ["Unique Z"]},
        "summary": "Overall good."
    }
    themes = {"f1.pdf": ["AI", "ML"]}
    
    report = generate_report(query_history, comparison, themes)
    
    assert "# VeriDocs Session Report" in report
    assert "Overall good." in report
    assert "Both agree on X" in report
    assert "Conflict on Y" in report
    assert "AI" in report
    assert "**Q1:** What is AI?" in report
    assert "*f1.pdf (p.1)*" in report
