-- 1. pgvector uzantısını aktif et (eğer yoksa)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. long_term_memory tablosu (Uzun Süreli Hafıza)
CREATE TABLE IF NOT EXISTS long_term_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadatas JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Performans için embedding sütununa ivfflat indeksi (İlk önce tablo dolu olmalı)
-- CREATE INDEX IF NOT EXISTS idx_long_term_memory_embedding ON long_term_memory USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- 3. short_term_memory tablosu (Kısa Süreli Hafıza)
CREATE TABLE IF NOT EXISTS short_term_memory (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. users tablosu (Opsiyonel kullanıcı bilgileri)
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 5. interactions tablosu (İsteğe bağlı, tüm konuşma kayıtları)
CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    message TEXT,
    response TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Örnek indeks: metadata içindeki user_id'ye göre sorgu yaparken hız için GIN indeks
CREATE INDEX IF NOT EXISTS idx_long_term_memory_metadata_gin ON long_term_memory USING gin (metadatas);
