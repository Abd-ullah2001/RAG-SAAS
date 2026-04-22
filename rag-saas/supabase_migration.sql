-- ============================================================================
-- RAG SaaS — Supabase Database Migration
-- Run this ENTIRE script in Supabase SQL Editor (Dashboard → SQL Editor → New Query)
-- ============================================================================

-- 1. Enable the pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- 2. DOCUMENTS TABLE — tracks every uploaded file
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_size_bytes BIGINT DEFAULT 0,
    file_type TEXT NOT NULL DEFAULT 'text/plain',
    chunks_count INTEGER NOT NULL DEFAULT 0,
    storage_path TEXT,                          -- path in Supabase Storage bucket
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS: each user can only see/manage their own documents
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own documents"
    ON documents FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Service role bypass (our backend uses service_role key)
CREATE POLICY "Service role full access on documents"
    ON documents FOR ALL
    USING (auth.role() = 'service_role');

CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);

-- ============================================================================
-- 3. DOCUMENT_CHUNKS TABLE — stores text chunks + vector embeddings
--    NVIDIA nv-embedqa-e5-v5 produces 1024-dimensional embeddings
-- ============================================================================
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1024),                    -- NVIDIA embedding dimension
    chunk_index INTEGER NOT NULL DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- RLS for chunks
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own chunks"
    ON document_chunks FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Service role full access on chunks"
    ON document_chunks FOR ALL
    USING (auth.role() = 'service_role');

-- Index for user-scoped queries
CREATE INDEX IF NOT EXISTS idx_chunks_user_id ON document_chunks(user_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON document_chunks(document_id);

-- ============================================================================
-- 4. HNSW INDEX for fast approximate nearest neighbor search
--    HNSW is preferred over IVFFlat for dynamic data (no training needed)
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
    ON document_chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ============================================================================
-- 5. SIMILARITY SEARCH FUNCTION — called from the backend
--    Uses cosine similarity: 1 - cosine_distance = similarity score
-- ============================================================================
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1024),
    match_count INT DEFAULT 10,
    filter_user_id UUID DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
SECURITY DEFINER                               -- runs with owner privileges for RLS bypass
SET search_path = public
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.content,
        dc.metadata,
        (1 - (dc.embedding <=> query_embedding))::FLOAT AS similarity
    FROM document_chunks dc
    WHERE dc.user_id = filter_user_id
    ORDER BY dc.embedding <=> query_embedding  -- cosine distance (ascending = most similar)
    LIMIT match_count;
END;
$$;

-- ============================================================================
-- 6. QUERY HISTORY TABLE — for analytics, billing, and audit trails
-- ============================================================================
CREATE TABLE IF NOT EXISTS query_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT,
    chunks_used INTEGER DEFAULT 0,
    processing_time_ms FLOAT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- RLS for query history
ALTER TABLE query_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users view own queries"
    ON query_history FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Service role full access on query_history"
    ON query_history FOR ALL
    USING (auth.role() = 'service_role');

CREATE INDEX IF NOT EXISTS idx_query_history_user_id ON query_history(user_id);
CREATE INDEX IF NOT EXISTS idx_query_history_created_at ON query_history(created_at DESC);

-- ============================================================================
-- 7. UPDATED_AT TRIGGER — auto-update the updated_at column on documents
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trigger_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
