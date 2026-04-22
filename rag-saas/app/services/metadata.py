"""
Metadata Service — CRUD operations for document and query records.

Stores structured metadata in Supabase PostgreSQL for:
  - Document tracking (what files a user has uploaded)
  - Query history (analytics, billing, audit trails)
  - User statistics (counts for profile display)

All operations use the service_role client (bypasses RLS) because
authorization is already handled by the JWT middleware.
"""

from typing import Optional
from app.db.supabase_client import supabase
from app.core.logging import logger


# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENT METADATA
# ═══════════════════════════════════════════════════════════════════════════════

async def create_document_record(
    user_id: str,
    filename: str,
    file_size_bytes: int,
    file_type: str,
    chunks_count: int,
    storage_path: str,
) -> dict:
    """
    Create a document metadata record after successful ingestion.
    
    This record links the user → file → chunks together and stores
    metadata that's useful for display (file size, type, chunk count).
    
    Returns:
        The created document record as a dict (includes generated UUID)
    """
    record = {
        "user_id": user_id,
        "filename": filename,
        "file_size_bytes": file_size_bytes,
        "file_type": file_type,
        "chunks_count": chunks_count,
        "storage_path": storage_path,
    }

    result = supabase.table("documents").insert(record).execute()

    if not result.data:
        logger.error(f"Failed to create document record for {filename}")
        raise RuntimeError(f"Database insert failed for document: {filename}")

    doc = result.data[0]
    logger.info(f"Document record created: {doc['id']} ({filename})")
    return doc


async def get_user_documents(user_id: str) -> list[dict]:
    """
    Fetch all documents for a specific user, ordered by most recent first.
    
    Used by the /me/documents endpoint to show the user's file library.
    """
    result = (
        supabase.table("documents")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return result.data or []


async def get_document_by_id(document_id: str, user_id: str) -> Optional[dict]:
    """
    Fetch a single document by ID, scoped to the user for security.
    
    Returns None if the document doesn't exist or doesn't belong to the user.
    """
    result = (
        supabase.table("documents")
        .select("*")
        .eq("id", document_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    return result.data


async def delete_document_record(document_id: str, user_id: str) -> bool:
    """
    Delete a document metadata record.
    
    Note: This ONLY deletes the metadata row. The caller is responsible
    for also deleting chunks (vector_store) and files (storage).
    """
    result = (
        supabase.table("documents")
        .delete()
        .eq("id", document_id)
        .eq("user_id", user_id)
        .execute()
    )

    deleted = bool(result.data)
    if deleted:
        logger.info(f"Document record deleted: {document_id}")
    return deleted


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY HISTORY
# ═══════════════════════════════════════════════════════════════════════════════

async def save_query_record(
    user_id: str,
    question: str,
    answer: str,
    chunks_used: int,
    processing_time_ms: float,
) -> dict:
    """
    Log a completed query to the history table.
    
    Purposes:
      - Analytics: what questions are users asking?
      - Billing: track API usage per user
      - Audit: full trail of what was asked and answered
    """
    record = {
        "user_id": user_id,
        "question": question,
        "answer": answer,
        "chunks_used": chunks_used,
        "processing_time_ms": processing_time_ms,
    }

    result = supabase.table("query_history").insert(record).execute()

    if result.data:
        logger.info(f"Query logged for user {user_id}")
    return result.data[0] if result.data else {}


async def get_user_query_history(
    user_id: str,
    limit: int = 50,
) -> list[dict]:
    """
    Fetch recent query history for a user, ordered by most recent first.
    
    Args:
        user_id: The user whose history to retrieve
        limit: Maximum number of records to return (default 50)
    """
    result = (
        supabase.table("query_history")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return result.data or []


# ═══════════════════════════════════════════════════════════════════════════════
# USER STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

async def get_user_stats(user_id: str) -> dict:
    """
    Get aggregate counts for a user's profile display.
    
    Returns:
        dict with documents_count and queries_count
    """
    # Count documents
    docs_result = (
        supabase.table("documents")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .execute()
    )

    # Count queries
    queries_result = (
        supabase.table("query_history")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .execute()
    )

    return {
        "documents_count": docs_result.count or 0,
        "queries_count": queries_result.count or 0,
    }
