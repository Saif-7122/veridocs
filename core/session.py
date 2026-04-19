"""
In-memory session store.
Each session holds: uploaded file paths, FAISS index, BM25 index, 
chunk list, and doc metadata. Cleared after SESSION_EXPIRY_MINUTES.
"""
import time
import os
from typing import Any

SESSION_EXPIRY = int(os.getenv("SESSION_EXPIRY_MINUTES", 60)) * 60

# Structure:
# sessions[session_id] = {
#     "created_at": float,
#     "files": list[str],            # file paths on disk
#     "chunks": list[dict],          # {"text": str, "source": str, "page": int}
#     "faiss_index": Any,            # FAISSIndex object
#     "bm25_index": Any,             # BM25Okapi object
#     "embeddings": Any,             # numpy array
#     "doc_outlines": dict,          # {filename: [headings]}
# }
sessions: dict[str, dict[str, Any]] = {}


def create_session(session_id: str) -> dict:
    sessions[session_id] = {
        "created_at": time.time(),
        "files": [],
        "chunks": [],
        "faiss_index": None,
        "bm25_index": None,
        "embeddings": None,
        "doc_outlines": {},
    }
    return sessions[session_id]


def get_session(session_id: str) -> dict | None:
    session = sessions.get(session_id)
    if not session:
        return None
    if time.time() - session["created_at"] > SESSION_EXPIRY:
        del sessions[session_id]
        return None
    return session


def delete_session(session_id: str):
    sessions.pop(session_id, None)


def list_sessions() -> list[str]:
    return list(sessions.keys())
