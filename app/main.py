"""
FastAPI application entry point.

Initializes the FastAPI app with routes, middleware, and configuration.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting LLM AI Basket Builder service")
    settings = get_settings()
    logger.info(f"Using model: {settings.openai_model}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down LLM AI Basket Builder service")


# Initialize FastAPI app
app = FastAPI(
    title="LLM AI Basket Builder",
    description="Production-grade LLM-powered shopping basket builder API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, tags=["basket"])

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information.
    
    Returns:
        dict: API metadata
    """
    return {
        "service": "LLM AI Basket Builder",
        "version": "1.0.0",
        "description": "Production-grade LLM-powered shopping basket builder",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
