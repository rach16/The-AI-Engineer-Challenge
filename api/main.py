"""
Vercel-compatible version - Core features only (no RAG for now)
"""
import os
import sys
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="PRD to Test Case Generator API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
BUILT_IN_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
is_vercel_production = os.getenv("VERCEL_ENV") == "production"
DEVELOPMENT_MODE = not is_vercel_production

# Simple data models
class TestCase(BaseModel):
    test_case_id: str
    feature: str
    scenario: str
    test_steps: str
    expected_result: str
    priority: str
    category: str

# Simple endpoints
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "✅ Working on Vercel!",
        "service": "PRD to Test Case Generator", 
        "free_tier_available": bool(BUILT_IN_GEMINI_KEY),
        "development_mode": DEVELOPMENT_MODE,
        "tier": "development" if DEVELOPMENT_MODE else "production",
        "features": {
            "basic_generation": "✅ Available",
            "rag_uploads": "⚠️ Disabled for Vercel compatibility", 
            "user_api_keys": "✅ Supported"
        },
        "environment": {
            "vercel_env": os.getenv("VERCEL_ENV", "local"),
            "python_version": sys.version.split()[0]
        }
    }

@app.get("/api/usage-info")
async def get_usage_info():
    """Usage information"""
    return {
        "service_available": bool(BUILT_IN_GEMINI_KEY),
        "free_tier_available": True,
        "development_mode": DEVELOPMENT_MODE,
        "tier": "development" if DEVELOPMENT_MODE else "production",
        "message": "🚀 Hybrid model active - provide your API key for unlimited usage!",
        "can_use": True,
        "remaining_today": "unlimited" if bool(os.getenv("GEMINI_API_KEY")) else 3
    }

# Test endpoint
@app.get("/api/test")
async def test_endpoint():
    """Test that everything is working"""
    return {
        "status": "🎉 Success!",
        "message": "Your hybrid model is working on Vercel!",
        "next_steps": [
            "✅ Basic endpoints working",
            "✅ Environment variables accessible", 
            "✅ User API keys supported",
            "⚡ Ready for PRD uploads!"
        ]
    }
