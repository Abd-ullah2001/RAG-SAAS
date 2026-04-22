"""
Main Application — Entry point for the FastAPI RAG SaaS backend.

Handles:
  - Router registration (Auth, Ingestion, Query, User)
  - CORS configuration
  - Startup/Shutdown events
  - Global health check
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import upload, query, auth, user_routes
from app.core.config import settings
from app.core.logging import logger

# Initialize FastAPI with metadata from config
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Scalable RAG SaaS powered by NVIDIA NIM and Supabase"
)

# ─── CORS Configuration ──────────────────────────────────────────────────────
# Ensures the frontend (React/Next.js/Streamlit) can communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Router Registration ─────────────────────────────────────────────────────
app.include_router(auth.router)           # Signup, Login, OAuth
app.include_router(user_routes.router)    # User profile, history, docs
app.include_router(upload.router)         # Document ingestion
app.include_router(query.router)          # RAG querying

@app.on_event("startup")
async def startup_event():
    """ Log application startup details for monitoring """
    logger.info(f"🚀 Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"NVIDIA LLM: {settings.MODEL_LLM}")
    logger.info(f"NVIDIA Embedding: {settings.MODEL_EMBEDDING}")
    logger.info(f"Supabase Project URL: {settings.SUPABASE_URL}")

@app.get("/", tags=["General"])
async def root():
    """ Health check endpoint """
    return {
        "status": "online",
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "supabase_connected": True if settings.SUPABASE_URL else False
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)