# VeriDocs

Intelligent document analysis platform. Upload contracts, research papers, or any documents — ask questions across all of them, compare differences, and generate structured reports.

## Stack
- **Backend:** FastAPI + Python 3.11
- **LLM:** Groq (Llama-3.1-8b-instant)
- **Embeddings:** `all-MiniLM-L6-v2` (Local Sentence-Transformers)
- **Vector Search:** FAISS (Semantic) + BM25 (Keyword) Hybrid
- **Frontend:** React (Integrated & served by FastAPI)

## Setup & Running
1. **Prepare Environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   cp .env.example .env
   # Add your GROQ_API_KEY to .env
   ```

2. **Build Frontend (Required once):**
   ```powershell
   cd frontend
   npm install
   npm run build
   cd ..
   ```

3. **Start Application:**
   ```powershell
   uvicorn main:app --reload
   ```

The application will be available at: **http://localhost:8000**

## Project Structure
| Module | Responsibility |
|---|---|
| `main.py` | Entry point & Static file serving |
| `modules/ingestor.py` | PDF/DOCX parsing & chunking |
| `modules/chat.py` | Groq-powered Q&A |
| `modules/insights.py` | Comparison & Report logic |
| `frontend/` | React source code |
| `render.yaml` | Deployment config for Render.com |


