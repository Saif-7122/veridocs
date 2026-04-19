# VeriDocs

Intelligent document analysis platform. Upload contracts, research papers, or any documents — ask questions across all of them, compare differences, and generate structured reports.

## Stack
- **Backend:** FastAPI + Python 3.11
- **LLM:** Google Gemini Flash (free tier)
- **Embeddings:** sentence-transformers `all-MiniLM-L6-v2` (local, no API cost)
- **Vector Search:** FAISS (semantic) + BM25 (keyword) hybrid
- **Frontend:** React (separate repo)

## Setup
```bash
git clone <repo>
cd veridocs
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
uvicorn main:app --reload
```

API docs: http://localhost:8000/docs

## Module Responsibilities
| Module | What it does |
|---|---|
| `modules/ingestor.py` | Parse PDFs/DOCX, extract outline, chunk text |
| `modules/embedder.py` | Local embeddings via sentence-transformers |
| `modules/retriever.py` | FAISS + BM25 hybrid search |
| `modules/chat.py` | Gemini Flash Q&A with citations |
| `modules/insights.py` | Doc comparison, themes, report generation |
| `api/routes.py` | FastAPI endpoints |
| `core/session.py` | In-memory session management |


