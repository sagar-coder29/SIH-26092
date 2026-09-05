-- =====================================================================
-- Sahayak — user_sessions (AI auto-generated Results/Dashboard/Docs)
-- ---------------------------------------------------------------------
-- Run this in your Supabase SQL Editor (only the project owner can run
-- DDL; the service-role key cannot execute DDL over the REST API).
--
-- Optional persistence for the POST /api/generate endpoint. If this table
-- does not exist, generation still works and returns the data live — the
-- backend just logs a warning.
-- =====================================================================

create table if not exists public.user_sessions (
  id bigint generated always as identity primary key,
  user_id text,
  user_email text,
  query text not null,
  profile jsonb default '{}'::jsonb,
  generated jsonb default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- One auto-generated session per distinct user query is enough for the demo.
alter table public.user_sessions
  add constraint user_sessions_query_key unique (query);

create index if not exists user_sessions_user_id_idx
  on public.user_sessions (user_id);
create index if not exists user_sessions_user_email_idx
  on public.user_sessions (user_email);

-- Row Level Security: users can only read their own generated sessions.
alter table public.user_sessions enable row level security;

drop policy if exists "user_sessions_select_own" on public.user_sessions;
create policy "user_sessions_select_own"
  on public.user_sessions for select
  using (auth.uid()::text = user_id);

drop policy if exists "user_sessions_insert_own" on public.user_sessions;
create policy "user_sessions_insert_own"
  on public.user_sessions for insert
  with check (auth.uid()::text = user_id);

-- Refresh the PostgREST schema cache so new tables/columns appear instantly.
notify pgrst, 'reload schema';
