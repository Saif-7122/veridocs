from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/")
def root():
    return {"message": "VeriDocs API is active. Use /health or /api/v1 endpoints."}
