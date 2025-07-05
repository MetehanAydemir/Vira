-- Enable the pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the long-term memory table
CREATE TABLE IF NOT EXISTS long_term_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    content TEXT
);

-- Add vector column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'long_term_memory' AND column_name = 'embedding'
    ) THEN
        ALTER TABLE long_term_memory ADD COLUMN embedding vector(1536);
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        -- If the above fails, try without dimensions
        ALTER TABLE long_term_memory ADD COLUMN embedding vector;
END
$$;

-- Create an index for faster similarity searches if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'long_term_memory_embedding_idx'
    ) THEN
        CREATE INDEX long_term_memory_embedding_idx ON long_term_memory USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        -- If the above fails, try a simpler index
        CREATE INDEX long_term_memory_embedding_idx ON long_term_memory USING ivfflat (embedding vector_cosine_ops);
END
$$;