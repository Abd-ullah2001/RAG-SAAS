"""
LLM Service — Generative AI logic using NVIDIA NIM.

Uses NVIDIA's Llama 3.1 endpoint to generate grounded responses based on
retrieved context. Implements strict system prompting to minimize hallucinations.
"""

import httpx
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger

async def generate_response(query: str, context: List[Dict[str, Any]]) -> str:
    """
    Generate an answer grounded in the provided context using NVIDIA NIM.
    
    Args:
        query: User's question
        context: List of retrieved chunks with 'content' and 'metadata'
        
    Returns:
        Generated answer text
    """
    logger.info("Generating response from NVIDIA LLM")
    
    # 1. Format context for the prompt with source attribution
    context_text = "\n\n".join([
        f"--- Source: {c['metadata'].get('source', 'Unknown Document')} ---\n{c['content']}"
        for c in context
    ])
    
    # 2. Define the system behavior
    system_prompt = """
    You are an expert AI assistant providing answers based ONLY on the provided context excerpts.
    
    Guidelines:
    1. If the context does not contain enough information, state: "I don't have enough information in your documents to answer this."
    2. Maintain a professional tone.
    3. Be concise but thorough.
    4. Cite sources (e.g., "[Source: file.pdf]") when quoting or referencing specific information.
    5. Do NOT use any pre-existing knowledge that contradicts the provided excerpts.
    """

    user_prompt = f"""
    Context Excerpts:
    {context_text}

    User Question: {query}
    
    Answer the question precisely using the excerpts above:
    """

    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.MODEL_LLM,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,    # High precision, low creativity
        "top_p": 0.7,
        "max_tokens": 1024,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.NVIDIA_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"NVIDIA LLM Error: {response.text}")
                return "I apologize, but the AI service is currently unavailable. Please try again later."

            data = response.json()
            return data["choices"][0]["message"]["content"]
            
    except Exception as e:
        logger.error(f"Unexpected error in LLM generation: {str(e)}")
        return "An internal error occurred while generating the answer."