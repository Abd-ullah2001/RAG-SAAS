"""
Ingestion Service — Document processing pipeline.

Pipeline stages:
  1. PARSE   — Extract text from PDF, DOCX, CSV, XLSX, or TXT files
  2. CHUNK   — Split text into semantically meaningful segments
  3. EMBED   — Generate vector embeddings via NVIDIA NIM API (batched)
  4. STORE   — Persist chunks + embeddings into Supabase pgvector

Designed for:
  - Multi-tenant isolation (user_id scoping on every record)
  - Batch processing (NVIDIA API supports batched embedding calls)
  - Error resilience (detailed logging at every stage)
"""

import httpx
import fitz           # PyMuPDF — fast PDF text extraction
import pandas as pd
from io import BytesIO
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.core.logging import logger
from app.db.vector_store import store_embeddings

# ─── Text Splitter Configuration ──────────────────────────────────────────────
# RecursiveCharacterTextSplitter tries to split at natural boundaries:
# paragraphs → sentences → words → characters
# This preserves semantic meaning within each chunk.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,           # ~150 words per chunk (good for RAG precision)
    chunk_overlap=50,         # overlap to maintain context across chunk boundaries
    separators=["\n\n", "\n", ". ", " ", ""],
)


# ═══════════════════════════════════════════════════════════════════════════════
# FILE PARSING
# ═══════════════════════════════════════════════════════════════════════════════

async def parse_file(filename: str, content: bytes) -> str:
    """
    Extract plain text from various file formats.
    
    Supported formats:
      - PDF  (.pdf)  — via PyMuPDF, extracts text from all pages
      - DOCX (.docx) — via python-docx, extracts paragraph text
      - CSV  (.csv)  — via pandas, converts to string representation
      - XLSX (.xlsx) — via pandas + openpyxl, converts to string
      - TXT  (*)     — decoded as UTF-8 plaintext (fallback for all others)
    
    Args:
        filename: Original filename (used to determine format)
        content: Raw file bytes
    
    Returns:
        Extracted text as a single string
    
    Raises:
        ValueError: If the file cannot be parsed
    """
    logger.info(f"Parsing file: {filename} ({len(content)} bytes)")

    try:
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

        if ext == "pdf":
            doc = fitz.open(stream=content, filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            return text

        elif ext == "docx":
            doc = DocxDocument(BytesIO(content))
            return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

        elif ext == "csv":
            df = pd.read_csv(BytesIO(content))
            return df.to_string()

        elif ext == "xlsx":
            df = pd.read_excel(BytesIO(content), engine="openpyxl")
            return df.to_string()

        else:
            # Fallback: treat as plain text
            return content.decode("utf-8")

    except Exception as e:
        logger.error(f"Error parsing file {filename}: {str(e)}")
        raise ValueError(f"Failed to parse {filename}: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# NVIDIA EMBEDDING GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

async def get_nvidia_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate vector embeddings for a batch of texts using NVIDIA NIM API.
    
    The NVIDIA nv-embedqa-e5-v5 model produces 1024-dimensional embeddings
    optimized for retrieval tasks. We use input_type="passage" for document
    chunks (vs "query" for user queries — see retrieval.py).
    
    For large documents with many chunks, we split into sub-batches of 50
    to stay within NVIDIA's API payload limits.
    
    Args:
        texts: List of text chunks to embed
    
    Returns:
        List of embedding vectors (each 1024 floats)
    
    Raises:
        RuntimeError: If the NVIDIA API returns an error
    """
    headers = {
        "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
        "Content-Type": "application/json",
    }

    all_embeddings: list[list[float]] = []
    batch_size = 50  # NVIDIA API batch limit

    async with httpx.AsyncClient(timeout=60.0) as client:
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            payload = {
                "input": batch,
                "model": settings.MODEL_EMBEDDING,
                "input_type": "passage",       # "passage" for document chunks
                "encoding_format": "float",
            }

            response = await client.post(
                f"{settings.NVIDIA_BASE_URL}/embeddings",
                headers=headers,
                json=payload,
            )

            if response.status_code != 200:
                logger.error(f"NVIDIA Embedding API error: {response.text}")
                raise RuntimeError(
                    f"NVIDIA Embedding API failed (HTTP {response.status_code})"
                )

            data = response.json()
            batch_embeddings = [item["embedding"] for item in data["data"]]
            all_embeddings.extend(batch_embeddings)

            logger.info(
                f"Embedded batch {i // batch_size + 1}: "
                f"{len(batch)} chunks → {len(batch_embeddings)} vectors"
            )

    return all_embeddings


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN INGESTION PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

async def ingest_document(
    filename: str,
    content: bytes,
    user_id: str,
    document_id: str,
) -> int:
    """
    Full ingestion pipeline: Parse → Chunk → Embed → Store in pgvector.
    
    This is the core of the RAG system's write path. Each stage is logged
    for observability and debugging.
    
    Args:
        filename: Original filename
        content: Raw file bytes
        user_id: Authenticated user's UUID (tenant isolation)
        document_id: UUID of the document record (from metadata service)
    
    Returns:
        Number of chunks successfully processed and stored
    """
    # Stage 1: Parse text from file
    text = await parse_file(filename, content)
    logger.info(f"Parsed {filename}: {len(text)} characters extracted")

    # Stage 2: Chunk text into semantic segments
    chunks = text_splitter.split_text(text)
    logger.info(f"Chunked {filename}: {len(chunks)} chunks created")

    if not chunks:
        logger.warning(f"No text chunks produced from {filename} — file may be empty")
        return 0

    # Stage 3: Generate embeddings in batches via NVIDIA API
    embeddings = await get_nvidia_embeddings(chunks)

    # Stage 4: Build per-chunk metadata
    metadatas = [
        {"source": filename, "chunk_index": idx}
        for idx in range(len(chunks))
    ]

    # Stage 5: Store in Supabase pgvector
    stored_count = await store_embeddings(
        user_id=user_id,
        document_id=document_id,
        chunks=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    logger.info(
        f"Ingestion complete: {filename} → {stored_count} chunks stored "
        f"for user {user_id}"
    )
    return stored_count