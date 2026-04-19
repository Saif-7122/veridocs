import pytest
from fastapi.testclient import TestClient
from main import app
import os
import shutil

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "VeriDocs API is running"

def test_upload_missing_files():
    response = client.post("/api/v1/upload")
    assert response.status_code == 422

# To perform an actual local upload integration test without testing the full 
# embeddings and models suite in an API test, we mock them.
from unittest.mock import patch

@patch("api.routes.load_and_chunk")
@patch("api.routes.embed_chunks")
@patch("api.routes.build_faiss_index")
@patch("api.routes.build_bm25_index")
def test_upload_documents(mock_bm25, mock_faiss, mock_embed, mock_load):
    mock_load.return_value = ([{"text": "mock chunk", "source": "test.pdf"}], ["Outline"])
    mock_embed.return_value = [[0.1, 0.2]]
    mock_faiss.return_value = "faiss_mock"
    mock_bm25.return_value = "bm25_mock"

    # Create dummy pdf
    dummy_path = "test_upload_api.pdf"
    with open(dummy_path, "wb") as f:
        f.write(b"%PDF-1.4\n")

    with open(dummy_path, "rb") as f:
         response = client.post(
             "/api/v1/upload", 
             files=[("files", ("test_upload_api.pdf", f, "application/pdf"))]
         )
    
    os.remove(dummy_path)
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["files"] == ["test_upload_api.pdf"]
    assert data["status"] == "ready"
    assert "test_upload_api.pdf" in data["outlines"]
    
    # Cleanup session dir
    session_id = data["session_id"]
    if os.path.exists(f"uploads/{session_id}"):
        shutil.rmtree(f"uploads/{session_id}")

def test_chat_no_session():
    response = client.post("/api/v1/chat", json={"session_id": "invalid", "query": "hello"})
    assert response.status_code == 404
