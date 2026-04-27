"""
LLM Service — Generative AI logic using NVIDIA NIM with Agentic Tool Calling.
"""

import httpx
import json
from typing import List, Dict, Any, Tuple
from app.core.config import settings
from app.core.logging import logger
from app.services.agent_tools import TOOLS, execute_tool

async def generate_response(query: str, context: List[Dict[str, Any]], user_id: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Generate an answer grounded in context.
    Returns a tuple of (answer_text, list_of_tool_sources).
    """
    logger.info("Generating agentic response from NVIDIA LLM")
    
    context_text = "\n\n".join([
        f"--- Source: {c['metadata'].get('source', 'Unknown Document')} (Chunk {c['metadata'].get('chunk_index', 0)}) ---\n{c['content']}"
        for c in context
    ])
    
    system_prompt = """
    You are an expert AI assistant providing answers based on the provided context excerpts and available tools.
    
    Guidelines:
    1. If the context contains the answer, provide it and cite sources (e.g., "[Source: file.pdf, Chunk 1]").
    2. If the user asks to read, list, or modify Google Sheets, use the provided tools.
    3. IMPORTANT: When you use a Google Sheet tool, always mention the Spreadsheet ID and Range in your response so the user knows where the data came from.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context Excerpts:\n{context_text}\n\nUser Question: {query}"}
    ]

    tool_sources = []
    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        for _ in range(5):
            payload = {
                "model": settings.MODEL_LLM,
                "messages": messages,
                "tools": TOOLS,
                "temperature": 0.1,
                "max_tokens": 1024,
                "stream": False
            }

            try:
                response = await client.post(
                    f"{settings.NVIDIA_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    logger.error(f"NVIDIA LLM Error: {response.text}")
                    return "I apologize, but the AI service is currently unavailable.", []

                data = response.json()
                message = data["choices"][0]["message"]
                
                # Fix: Ensure content is never None for the next turn
                if message.get("content") is None:
                    message["content"] = ""

                # If no tools called, return result
                if "tool_calls" not in message or not message["tool_calls"]:
                    return message["content"], tool_sources
                
                messages.append(message)
                
                for tool_call in message["tool_calls"]:
                    tool_result = await execute_tool(user_id, tool_call)
                    
                    # Capture tool result as a "source" for deep citation
                    args = json.loads(tool_call["function"]["arguments"])
                    if "spreadsheet_id" in args:
                        sheet_url = f"https://docs.google.com/spreadsheets/d/{args['spreadsheet_id']}"
                        tool_sources.append({
                            "content": f"Tool Result: {tool_result}",
                            "metadata": {
                                "source": sheet_url,
                                "page_label": args.get("range_name", "Sheet1")
                            }
                        })

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_call["function"]["name"],
                        "content": tool_result
                    })
                    
            except Exception as e:
                logger.error(f"Unexpected error in Agentic LLM generation: {str(e)}")
                return "An internal error occurred.", []
                
        return "Agent timed out.", []
