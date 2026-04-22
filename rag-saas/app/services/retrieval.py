"""
Retrieval Service — Two-stage retrieval pipeline for RAG.

Pipeline:
  1. EMBED QUERY   — Convert user question to a vector via NVIDIA NIM
  2. VECTOR SEARCH — Find candidate chunks via pgvector cosine similarity
  3. RERANK        — Re-score candidates with NVIDIA Reranker for precision
  4. FORMAT        — Return the top-k most relevant chunks with metadata

The two-stage approach (vector search → reranker) gives us:
  - Speed: vector search narrows millions of chunks to ~15 candidates
  - Precision: reranker uses cross-attention to find the best ~4 results
"""

import httpx
from typing import Any

from app.core.config import settings
from app.core.logging import logger
from app.db.vector_store import similarity_search


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY EMBEDDING
# ═══════════════════════════════════════════════════════════════════════════════

async def get_query_embedding(query: str) -> list[float]:
    """
    Generate a vector embedding for the user's query.
    
    Uses input_type="query" (vs "passage" for document chunks).
    This asymmetric encoding is critical for the NVIDIA E5 model family —
    queries and passages are embedded differently for optimal retrieval.
    
    Args:
        query: The user's natural language question
    
    Returns:
        1024-dimensional embedding vector
    """
    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "input": [query],
        "model": settings.MODEL_EMBEDDING,
        "input_type": "query",        # asymmetric encoding for queries
        "encoding_format": "float",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.NVIDIA_BASE_URL}/embeddings",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]


# ═══════════════════════════════════════════════════════════════════════════════
# RERANKING
# ═══════════════════════════════════════════════════════════════════════════════

async def rerank_results(
    query: str,
    chunks: list[str],
    top_n: int = 4,
) -> list[dict[str, Any]]:
    """
    Re-score candidate chunks using NVIDIA's cross-encoder reranker.
    
    Cross-encoders are more accurate than bi-encoders (embeddings) because
    they process the query-chunk pair together, enabling deeper semantic
    understanding. However, they're slower — which is why we only rerank
    the top ~15 candidates from the vector search, not all chunks.
    
    Falls back to original ordering if the reranker API fails (graceful
    degradation — the system still works, just with slightly lower precision).
    
    Args:
        query: The user's question
        chunks: Candidate text chunks from vector search
        top_n: Number of top results to return after reranking
    
    Returns:
        List of dicts with 'content' and 'score' keys, ordered by relevance
    """
    logger.info(f"Reranking {len(chunks)} candidates → selecting top {top_n}")

    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.MODEL_RERANKER,
        "query": {"text": query},
        "documents": [{"text": chunk} for chunk in chunks],
        "top_n": top_n,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.NVIDIA_BASE_URL}/ranking",
            headers=headers,
            json=payload,
        )

        if response.status_code != 200:
            logger.warning(
                f"Reranker API failed (HTTP {response.status_code}) — "
                f"falling back to vector similarity ordering"
            )
            # Graceful degradation: return chunks in their original order
            return [
                {"content": chunk, "score": 1.0}
                for chunk in chunks[:top_n]
            ]

        rankings = response.json().get("rankings", [])

        results = []
        for rank in rankings:
            idx = rank["index"]
            results.append({
                "content": chunks[idx],
                "score": rank["logit"],
            })

        return results


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RETRIEVAL PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

async def retrieve_context(
    query: str,
    user_id: str,
    k: int = 15,
    final_k: int = 4,
) -> list[dict[str, Any]]:
    """
    Full two-stage retrieval: Vector Search → Rerank.
    
    All results are strictly scoped to the authenticated user's data.
    No user can ever retrieve another user's chunks — this is enforced
    both here (user_id filter) and in the SQL function (WHERE clause).
    
    Args:
        query: The user's natural language question
        user_id: Authenticated user's UUID (tenant isolation)
        k: Number of candidates from vector search (cast wide net)
        final_k: Number of results after reranking (precision)
    
    Returns:
        List of relevant context chunks with metadata and scores
    """
    logger.info(f"Retrieval pipeline started for user {user_id}")

    # Stage 1: Embed the query
    query_embedding = await get_query_embedding(query)

    # Stage 2: Vector search via pgvector (tenant-isolated)
    search_results = await similarity_search(
        query_embedding=query_embedding,
        user_id=user_id,
        match_count=k,
    )

    if not search_results:
        logger.warning(f"No vector search results for user {user_id}")
        return []

    # Extract chunks and metadata from search results
    found_chunks = [r["content"] for r in search_results]
    found_metadatas = [r["metadata"] for r in search_results]

    logger.info(
        f"Vector search returned {len(found_chunks)} candidates "
        f"(similarity range: {search_results[-1]['similarity']:.4f} – "
        f"{search_results[0]['similarity']:.4f})"
    )

    # Stage 3: Rerank for precision
    reranked = await rerank_results(query, found_chunks, top_n=final_k)

    # Stage 4: Re-attach metadata from the original search results
    final_results = []
    for item in reranked:
        content = item["content"]
        # Find the original metadata by matching content
        try:
            orig_idx = found_chunks.index(content)
            metadata = found_metadatas[orig_idx]
        except ValueError:
            metadata = {}

        final_results.append({
            "content": content,
            "metadata": metadata,
            "score": item["score"],
        })

    logger.info(
        f"Retrieval complete: {len(final_results)} chunks selected from "
        f"{len(found_chunks)} candidates"
    )
    return final_results