"""
Minimal FastAPI app to test Vercel deployment
"""
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Minimal Test API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/test")
async def test_endpoint():
    """Minimal test endpoint"""
    return {
        "status": "working",
        "message": "FastAPI is working on Vercel!",
        "python_version": sys.version,
        "environment": {
            "vercel_env": os.getenv("VERCEL_ENV", "unknown"),
            "has_gemini_key": bool(os.getenv("GEMINI_API_KEY")),
        }
    }

@app.get("/api/health")  
async def health_check():
    """Simple health check"""
    return {"status": "ok", "service": "Minimal Test"}
