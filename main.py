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

@app.get("/")
def health_check():
    return {"status": "VeriDocs API is running", "version": "1.0.0"}
