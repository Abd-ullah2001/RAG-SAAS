"""
Vector Store — pgvector operations via Supabase PostgreSQL.

Replaces ChromaDB with Supabase's pgvector extension for:
  - Zero infrastructure overhead (no separate vector DB to manage)
  - Native PostgreSQL RLS for tenant isolation
  - Scales with Supabase's managed Postgres

Key operations:
  - store_embeddings(): batch insert chunks + embeddings
  - similarity_search(): find relevant chunks via cosine similarity
  - delete_document_chunks(): cleanup when a document is deleted
"""

from typing import Any
from app.db.supabase_client import supabase
from app.core.logging import logger


async def store_embeddings(
    user_id: str,
    document_id: str,
    chunks: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict[str, Any]],
) -> int:
    """
    Batch insert text chunks and their vector embeddings into pgvector.
    
    Args:
        user_id: Authenticated user's UUID (tenant isolation)
        document_id: UUID of the parent document record
        chunks: List of text chunks
        embeddings: Corresponding embedding vectors (1024-dim)
        metadatas: Per-chunk metadata (e.g., source filename)
    
    Returns:
        Number of chunks successfully stored
    """
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings"
        )

    # Build batch insert payload
    records = [
        {
            "user_id": user_id,
            "document_id": document_id,
            "content": chunk,
            "embedding": embedding,
            "chunk_index": idx,
            "metadata": meta,
        }
        for idx, (chunk, embedding, meta) in enumerate(
            zip(chunks, embeddings, metadatas)
        )
    ]

    # Supabase insert supports batch — much faster than individual inserts
    # We chunk into batches of 100 to avoid payload size limits
    batch_size = 100
    total_inserted = 0

    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        result = supabase.table("document_chunks").insert(batch).execute()
        total_inserted += len(result.data) if result.data else 0

    logger.info(
        f"Stored {total_inserted} chunks for document {document_id} "
        f"(user: {user_id})"
    )
    return total_inserted


async def similarity_search(
    query_embedding: list[float],
    user_id: str,
    match_count: int = 15,
) -> list[dict[str, Any]]:
    """
    Find the most similar document chunks for a query using cosine similarity.
    
    Calls the `match_documents` SQL function (defined in supabase_migration.sql)
    which uses pgvector's HNSW index for fast approximate nearest neighbor search.
    
    Args:
        query_embedding: 1024-dim embedding of the user's query
        user_id: Authenticated user's UUID (ensures tenant isolation)
        match_count: Number of top results to return
    
    Returns:
        List of dicts with keys: id, document_id, content, metadata, similarity
    """
    # Call the stored function via Supabase RPC
    result = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_count": match_count,
            "filter_user_id": user_id,
        },
    ).execute()

    if not result.data:
        logger.info(f"No matching chunks found for user {user_id}")
        return []

    logger.info(
        f"Found {len(result.data)} matching chunks for user {user_id} "
        f"(top similarity: {result.data[0]['similarity']:.4f})"
    )
    return result.data


async def delete_document_chunks(document_id: str) -> int:
    """
    Delete all chunks belonging to a specific document.
    Called when a user deletes a document to free up storage and vector space.
    
    Args:
        document_id: UUID of the document whose chunks should be removed
    
    Returns:
        Number of chunks deleted
    """
    result = (
        supabase.table("document_chunks")
        .delete()
        .eq("document_id", document_id)
        .execute()
    )

    deleted_count = len(result.data) if result.data else 0
    logger.info(f"Deleted {deleted_count} chunks for document {document_id}")
    return deleted_count
