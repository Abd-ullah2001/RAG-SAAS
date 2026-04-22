"""
Pydantic Schemas — Request/Response models for the entire API.

Organized by domain:
  1. Auth — signup, login, token responses
  2. Ingestion — file upload responses
  3. Query — RAG query request/response
  4. User — profile, document list, query history
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class SignUpRequest(BaseModel):
    """Email + password registration request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")


class LoginRequest(BaseModel):
    """Email + password login request."""
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="Account password")


class RefreshRequest(BaseModel):
    """Token refresh request — exchange a refresh_token for a new access_token."""
    refresh_token: str = Field(..., description="Refresh token from previous login")


class AuthResponse(BaseModel):
    """Standardized response for all auth operations (signup, login, refresh)."""
    access_token: str = Field(..., description="JWT access token for API authorization")
    refresh_token: str = Field(..., description="Refresh token to obtain new access tokens")
    token_type: str = Field(default="bearer", description="Token type — always 'bearer'")
    user_id: str = Field(..., description="Unique user identifier (UUID)")
    email: str = Field(..., description="User's email address")


class GoogleOAuthResponse(BaseModel):
    """Response containing the Google OAuth URL for the client to redirect to."""
    url: str = Field(..., description="Google OAuth consent screen URL")


# ═══════════════════════════════════════════════════════════════════════════════
# INGESTION SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class IngestionResponse(BaseModel):
    """Confirmation after successful document ingestion."""
    status: str = Field(default="success", description="Operation result")
    filename: str = Field(..., description="Original filename")
    document_id: str = Field(..., description="UUID of the stored document record")
    chunks_processed: int = Field(..., description="Number of text chunks created")
    storage_path: str = Field(..., description="File path in Supabase Storage")


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class QueryRequest(BaseModel):
    """
    RAG query request.
    
    The tenant_id is NO LONGER in the request body — it's extracted from
    the JWT token automatically. This prevents tenant spoofing.
    """
    question: str = Field(..., description="The user's question to the RAG system")
    top_k: int = Field(
        default=4, ge=1, le=10,
        description="Number of context chunks to use after reranking"
    )


class ContextChunk(BaseModel):
    """A single retrieved context chunk with its relevance score."""
    content: str = Field(..., description="Text content of the chunk")
    metadata: dict = Field(default_factory=dict, description="Chunk metadata (source, etc.)")
    score: Optional[float] = Field(None, description="Similarity/relevance score")


class QueryResponse(BaseModel):
    """Complete RAG query response with answer and supporting context."""
    question: str
    answer: str
    context: list[ContextChunk]
    processing_time: float = Field(..., description="Total processing time in seconds")


# ═══════════════════════════════════════════════════════════════════════════════
# USER / PROFILE SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class UserProfile(BaseModel):
    """Basic user profile information."""
    user_id: str
    email: str
    documents_count: int = Field(default=0, description="Total documents uploaded")
    queries_count: int = Field(default=0, description="Total queries made")


class DocumentRecord(BaseModel):
    """A stored document's metadata (not the content itself)."""
    id: str
    filename: str
    file_size_bytes: int = 0
    file_type: str = ""
    chunks_count: int = 0
    storage_path: Optional[str] = None
    created_at: Optional[datetime] = None


class QueryHistoryRecord(BaseModel):
    """A single entry from the user's query history."""
    id: str
    question: str
    answer: Optional[str] = None
    chunks_used: int = 0
    processing_time_ms: float = 0
    created_at: Optional[datetime] = None
