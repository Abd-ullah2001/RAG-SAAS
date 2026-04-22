"""
Application Configuration — Single source of truth for all settings.

All sensitive values are loaded from environment variables via pydantic-settings.
Local dev uses .env file; production uses Railway environment variables.
"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    Centralized configuration for the RAG SaaS application.
    
    Hierarchy: Environment Variables > .env file > defaults defined here.
    pydantic-settings automatically reads from env vars matching the field names.
    """

    # ─── API Information ───────────────────────────────────────────────
    API_TITLE: str = "Enterprise RAG SaaS"
    API_VERSION: str = "1.0.0"

    # ─── NVIDIA AI Foundation Endpoints ────────────────────────────────
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"

    # ─── NVIDIA Models ─────────────────────────────────────────────────
    MODEL_LLM: str = "meta/llama-3.1-8b-instruct"
    MODEL_EMBEDDING: str = "nvidia/nv-embedqa-e5-v5"
    MODEL_RERANKER: str = "nvidia/nv-rerankqa-mistral-4b-v3"
    
    # Embedding dimension — must match the vector(N) in our SQL migration
    EMBEDDING_DIMENSION: int = 1024

    # ─── Supabase ──────────────────────────────────────────────────────
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")

    # ─── Supabase Storage ──────────────────────────────────────────────
    STORAGE_BUCKET: str = "documents"

    # ─── Security ──────────────────────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-for-jwt")
    JWT_ALGORITHM: str = "HS256"
    
    # ─── CORS (allowed frontend origins — add your frontend URL here) ─
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        case_sensitive = True


# Singleton instance — import this everywhere
settings = Settings()
