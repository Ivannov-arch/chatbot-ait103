-- placeholder_schema.sql
-- database/schema.sql
--
-- Run this in: Supabase Dashboard → SQL Editor
-- Creates all tables needed for the XMUM Campus Chatbot knowledge base.
--
-- Tables:
--   knowledge_items     — Q&A pairs per module (main knowledge base)
--   conversation_logs   — Optional: store chat history persistently
--
-- TODO: finalise column types and add tsvector index for full-text search.
-- TODO: add Row Level Security (RLS) policies before production deployment.

-- ============================================================
-- 1. knowledge_items
-- ============================================================
CREATE TABLE IF NOT EXISTS knowledge_items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module      TEXT NOT NULL CHECK (module IN (
                    'admin_directory',
                    'campus_life',
                    'academic_navigation'
                )),
    question    TEXT NOT NULL,
    answer      TEXT NOT NULL,
    keywords    TEXT[] DEFAULT '{}',
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Full-text search index (optional, improves search performance)
-- ALTER TABLE knowledge_items ADD COLUMN fts tsvector
--     GENERATED ALWAYS AS (to_tsvector('english', question || ' ' || answer)) STORED;
-- CREATE INDEX knowledge_items_fts_idx ON knowledge_items USING GIN (fts);

-- ============================================================
-- 2. conversation_logs  (optional — for persistent context)
-- ============================================================
CREATE TABLE IF NOT EXISTS conversation_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  TEXT NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('user', 'bot')),
    message     TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS conversation_logs_session_idx
    ON conversation_logs (session_id, created_at);

-- ============================================================
-- Row Level Security (enable before production!)
-- ============================================================
-- ALTER TABLE knowledge_items ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Public read access" ON knowledge_items
--     FOR SELECT USING (true);

-- ALTER TABLE conversation_logs ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Session owner only" ON conversation_logs
--     FOR ALL USING (session_id = current_setting('app.session_id'));
