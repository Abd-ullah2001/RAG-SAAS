"""
Query Route — Handles RAG queries with authenticated user context and history logging.

Flow:
  1. Authenticate user via JWT
  2. Retrieve context from pgvector (tenant-isolated)
  3. Generate response using LLM (NVIDIA NIM)
  4. Log the query and answer to history
  5. Return query results
"""

import time
from fastapi import APIRouter, HTTPException, Depends
from app.services.retrieval import retrieve_context
from app.services.llm import generate_response
from app.services.metadata import save_query_record
from app.models.schemas import QueryRequest, QueryResponse, ContextChunk
from app.core.auth import get_current_user
from app.core.logging import logger

router = APIRouter(tags=["Query"])

@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    user: dict = Depends(get_current_user)
):
    """
    SaaS Query Endpoint:
    Two-stage retrieval + LLM Generation.
    Strictly scoped to the user's data.
    Logs interaction to Supabase for history/analytics.
    """
    user_id = user["user_id"]
    logger.info(f"Processing query for user: {user_id}")
    start_time = time.time()
    
    try:
        # 1. Retrieve most relevant context (includes vector search + reranking)
        context_data = await retrieve_context(
            query=request.question, 
            user_id=user_id,
            final_k=request.top_k
        )
        
        if not context_data:
            answer = "I could not find any relevant information in your documents to answer this question."
            formatted_context = []
        else:
            # 2. Generate final answer using context
            answer = await generate_response(request.question, context_data)
            
            # 3. Format response context
            formatted_context = [
                ContextChunk(
                    content=c["content"],
                    metadata=c["metadata"],
                    score=c["score"]
                ) for c in context_data
            ]

        processing_duration = time.time() - start_time
        
        # 4. Log query history to Supabase
        await save_query_record(
            user_id=user_id,
            question=request.question,
            answer=answer,
            chunks_used=len(formatted_context),
            processing_time_ms=processing_duration * 1000
        )

        logger.info(f"Query resolved for user {user_id} in {processing_duration:.2f}s")

        return QueryResponse(
            question=request.question,
            answer=answer,
            context=formatted_context,
            processing_time=processing_duration
        )

    except Exception as e:
        logger.error(f"Query error for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your query")