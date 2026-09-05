-- =============================================================================
-- chat_history table for Sahayak Q&A monitoring dashboard
-- Run this in Supabase SQL Editor (idempotent - safe to re-run).
-- =============================================================================

-- Table storing every user question + backend answer for the dashboard.
CREATE TABLE IF NOT EXISTS chat_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID,                          -- supabase auth.users.id (null for anonymous)
    user_email TEXT,
    query TEXT NOT NULL,
    answer TEXT NOT NULL,
    citations JSONB DEFAULT '[]'::jsonb,
    profile JSONB DEFAULT '{}'::jsonb,
    needs_prerequisites BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Index for dashboard listing (per user, newest first)
CREATE INDEX IF NOT EXISTS chat_history_user_idx ON chat_history (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS chat_history_email_idx ON chat_history (user_email, created_at DESC);

-- RLS: only the service role can write; owners can read their own rows.
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "chat_history service role full access"
  ON chat_history FOR ALL
  USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "chat_history owner read"
  ON chat_history FOR SELECT
  USING (user_id = auth.uid());

-- Helper function: record a Q&A (used by the backend with the service role).
CREATE OR REPLACE FUNCTION record_chat(
  p_user_id UUID,
  p_user_email TEXT,
  p_query TEXT,
  p_answer TEXT,
  p_citations JSONB DEFAULT '[]'::jsonb,
  p_profile JSONB DEFAULT '{}'::jsonb,
  p_needs_prerequisites BOOLEAN DEFAULT false
) RETURNS bigint
LANGUAGE sql
SECURITY DEFINER
AS $$
  INSERT INTO chat_history (user_id, user_email, query, answer, citations, profile, needs_prerequisites)
  VALUES (p_user_id, p_user_email, p_query, p_answer, p_citations, p_profile, p_needs_prerequisites)
  RETURNING id;
$$;

-- =============================================================================
-- VERIFICATION / SUMMARY
-- =============================================================================
SELECT 'chat_history table ready' AS test_result
WHERE EXISTS (
  SELECT 1 FROM information_schema.tables
  WHERE table_schema = 'public' AND table_name = 'chat_history'
);