"""
User Routes — Endpoints for managing user-specific data.

Endpoints:
  GET /me/profile      — Get user statistics and profile info
  GET /me/documents    — List all documents uploaded by the user
  GET /me/queries      — List recent query history
"""

from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.services.metadata import get_user_stats, get_user_documents, get_user_query_history
from app.models.schemas import UserProfile, DocumentRecord, QueryHistoryRecord

router = APIRouter(prefix="/me", tags=["User Profile"])

@router.get("/profile", response_model=UserProfile)
async def get_profile(user: dict = Depends(get_current_user)):
    """
    Fetch user statistics (document count, query count) and profile info.
    """
    user_id = user["user_id"]
    email = user["email"]
    
    stats = await get_user_stats(user_id)
    
    return UserProfile(
        user_id=user_id,
        email=email,
        documents_count=stats["documents_count"],
        queries_count=stats["queries_count"]
    )

@router.get("/documents", response_model=list[DocumentRecord])
async def list_documents(user: dict = Depends(get_current_user)):
    """
    List all documents uploaded by the authenticated user.
    """
    user_id = user["user_id"]
    documents = await get_user_documents(user_id)
    return documents

@router.get("/queries", response_model=list[QueryHistoryRecord])
async def list_queries(user: dict = Depends(get_current_user)):
    """
    List the recent query history for the authenticated user.
    """
    user_id = user["user_id"]
    history = await get_user_query_history(user_id)
    return history
