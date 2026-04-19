"""
FastAPI route handlers — the contract between backend and React frontend.
All endpoints use session_id to identify a user's document workspace.
"""
import uuid
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel

from core.session import create_session, get_session, delete_session
from modules.ingestor import load_and_chunk
from modules.embedder import embed_chunks, embed_query
from modules.retriever import build_faiss_index, build_bm25_index, hybrid_search
from modules.chat import ask
from modules.insights import extract_themes, compare_documents, generate_report

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Request / Response models ────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    query: str

class CompareRequest(BaseModel):
    session_id: str


# ── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    """
    Accept documents, save to disk, parse + index them.
    Returns a session_id the frontend stores for all subsequent calls.
    """
    if not files:
        raise HTTPException(status_code=422, detail="No files uploaded")
        
    session_id = str(uuid.uuid4())
    session = create_session(session_id)
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    all_chunks = []
    outlines = {}
    saved_files = []
    
    for f in files:
        # Validate extension
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in [".pdf", ".docx", ".doc"]:
            raise HTTPException(status_code=415, detail=f"Unsupported file type: {ext}")
            
        file_path = os.path.join(session_dir, f.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
            
        saved_files.append(f.filename)
        session["files"].append(file_path)
        
        # Ingest
        chunks, outline = load_and_chunk(file_path)
        all_chunks.extend(chunks)
        outlines[f.filename] = outline
        
    session["doc_outlines"] = outlines
    session["chunks"] = all_chunks
    
    if all_chunks:
        # Embed and index
        embeddings = embed_chunks(all_chunks)
        session["embeddings"] = embeddings
        session["faiss_index"] = build_faiss_index(embeddings)
        session["bm25_index"]  = build_bm25_index(all_chunks)
        
    session["query_history"] = []
        
    return {
        "session_id": session_id,
        "files": saved_files,
        "outlines": outlines,
        "status": "ready"
    }


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Answer a question using the session's indexed documents.
    """
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
        
    if not session["chunks"] or session["faiss_index"] is None:
        return {"answer": "No documents indexed.", "citations": [], "session_id": request.session_id}
        
    query_emb = embed_query(request.query)
    retrieved = hybrid_search(
        query=request.query,
        query_embedding=query_emb,
        faiss_index=session["faiss_index"],
        bm25_index=session["bm25_index"],
        chunks=session["chunks"],
        top_k=6,
        semantic_weight=0.6,
        keyword_weight=0.4
    )
    
    response_dict = ask(request.query, retrieved)
    
    # Save history
    session.setdefault("query_history", []).append({
        "query": request.query,
        "answer": response_dict["answer"],
        "citations": response_dict["citations"]
    })
    
    response_dict["session_id"] = request.session_id
    return response_dict


@router.post("/compare")
async def compare(request: CompareRequest):
    """
    Compare all documents in the session.
    """
    session = get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
        
    comparison = compare_documents(session.get("chunks", []))
    session["comparison"] = comparison
    return comparison


@router.get("/insights/{session_id}")
async def get_insights(session_id: str):
    """
    Return key themes for each document in the session.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
        
    themes_map = {}
    chunks = session.get("chunks", [])
    
    # We want unique bare filenames
    filenames = {os.path.basename(f) for f in session.get("files", [])}
    for fname in filenames:
        themes = extract_themes(chunks, fname)
        themes_map[fname] = themes
        
    session["themes"] = themes_map
    return {"themes": themes_map}


@router.get("/report/{session_id}")
async def download_report(session_id: str):
    """
    Generate and return a Markdown report as plain text download.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
        
    qhist = session.get("query_history", [])
    comp = session.get("comparison", {})
    themes = session.get("themes", {})
    
    report_md = generate_report(qhist, comp, themes)
    
    headers = {
        "Content-Disposition": f"attachment; filename=veridocs_report_{session_id}.md"
    }
    return PlainTextResponse(report_md, headers=headers)


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """
    Clean up session data and uploaded files.
    """
    delete_session(session_id)
    
    # Optionally delete files from disk
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    if os.path.exists(session_dir):
         shutil.rmtree(session_dir)
         
    return {"status": "session deleted", "session_id": session_id}
