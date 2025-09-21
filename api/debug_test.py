"""
Debug test to see if Vercel is picking up ANY changes
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/debug")
async def debug_test():
    return {
        "status": "🚨 SUCCESS! Vercel IS deploying our changes!",
        "timestamp": "2024-12-19 TEST",
        "message": "Now let's switch back to the full app.py with RAG functionality"
    }

@app.get("/api/health") 
async def health():
    return {"status": "Debug version working"}

# Import and mount the main app
try:
    from app import app as main_app
    # Mount main app endpoints
    for route in main_app.routes:
        app.routes.append(route)
except Exception as e:
    @app.get("/api/import-error")
    async def import_error():
        return {"error": f"Could not import main app: {str(e)}", "status": "debug_mode"}
