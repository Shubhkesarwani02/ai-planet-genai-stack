"""
Simplified main.py for testing without async dependencies
"""
from fastapi import FastAPI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GenAI Stack API",
    description="No-Code/Low-Code Workflow Builder with Document Intelligence",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "GenAI Stack API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api": "operational",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )