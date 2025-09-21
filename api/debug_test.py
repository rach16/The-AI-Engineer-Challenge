"""
Debug test to see if Vercel is picking up ANY changes
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/debug")
async def debug_test():
    return {
        "status": "🚨 DEBUG TEST - If you see this, Vercel is using the updated code!",
        "timestamp": "2024-12-19 TEST",
        "message": "This endpoint was added to test if Vercel deploys new changes"
    }

# Re-export the main app as well
try:
    from app import app as main_app
    app.mount("/main", main_app)
except:
    pass
