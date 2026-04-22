from app.api.routes import upload, query
from app.core.config import settings
from app.db.chroma_client import get_chroma_client
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    logger.info("Starting up RAG SaaS application...")
    
    # Initialize Chroma client on startup
    try:
        client = get_chroma_client()
        client.heartbeat()
        logger.info("Successfully connected to ChromaDB")
    except Exception as e:
        logger.error(f"Failed to connect to ChromaDB: {e}")
        # Depending on your needs, you might want to raise the exception
        # raise e
    
    yield
    
    logger.info("Shutting down RAG SaaS application...")

app = FastAPI(
    title="RAG SaaS API",
    description="AI-powered Document Analysis Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(upload.router)
app.include_router(query.router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        client = get_chroma_client()
        client.heartbeat()
        return {"status": "ok", "service": "rag-saas", "db": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "degraded", "service": "rag-saas", "db": "disconnected"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the RAG SaaS API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
