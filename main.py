from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from api.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="VeriDocs API",
    description="Document intelligence backend — upload, search, compare, chat.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://veridocs.vercel.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "VeriDocs API is running", "version": "1.0.0"}

# ── Serve Frontend Static Files ──
# This assumes the frontend has been built into frontend/dist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
frontend_dist = os.path.join(BASE_DIR, "frontend", "dist")

if os.path.exists(frontend_dist):
    # Mount static files (JS, CSS, etc.)
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    # Serve index.html for the root and all non-API/non-asset routes (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Exclude API routes from being swallowed by the catch-all
        if full_path.startswith("api/v1") or full_path.startswith("health"):
            return None # Let FastAPI handle it normally
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def root():
        return {"message": "VeriDocs API is active. Frontend build not found at frontend/dist."}
