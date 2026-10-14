# 🧑‍💻 Sahayak — Team Understanding Guide (What We Built & How)

> This file is for **the team** — so everyone understands *what* we made and *how* it works,
> end to end. If you're new, read this first. No fluff, just the real architecture.

---

## 🗺️ The Big Picture (One Mental Model)

```
 USER (browser)                    BACKEND (FastAPI)                    DATA / AI
 ───────────────                  ──────────────────                   ─────────────
 landing/chat/results   ──HTTP──▶  app/main.py (routes)               
      │ chats → /answer            ├─ rag_service  ──embedding──▶  Gemini (768-dim)
      │ profile extract (JS)       │     │                          │
      │ login/register              │     └──vector search──────▶  Supabase pgvector
      │      │ (Supabase Auth)     ├─ chat_service ──LLM──────▶  Groq (OpenAI-compat)
      │ generate → /api/generate   ├─ generate_service ──LLM──▶  Groq
      │                            └─ history_service ────────▶  Supabase chat_history
```

**In one sentence:** A vanilla-JS website talks to a FastAPI backend. The backend turns a
user's Hinglish question into a *cited explanation* by (1) embedding it, (2) finding similar
chunks in a Supabase vector DB, and (3) asking Groq to answer **only from those chunks**,
with citation markers.

---

## 📁 What Each Folder/File Is For (Team Mental Map)

### Root (`Sahayak/`)
- `app/` — the whole Python backend
- `static/site/` — the whole frontend (no build step, served by FastAPI)
- `sql/` — every Supabase table/function script
- `requirements.txt` — Python dependencies
- `.env` — **secret config** (Supabase + Groq + Gemini keys) — gitignored
- `.env.example` — template (dummy values)
- `Dockerfile` — turns it into a container (Cloud Run ready)
- `main.py` — legacy one-liner that just re-exports `app.main:app`
- `server-run-commands.md`, `pitch-tech-details.md` — docs (this + those)

> ⚠️ **Two venvs exist:** `venv` (Python 3.11 — use this) and `.venv` (3.14 — ignore).
> Don't mix them up.

---

## 🔧 Backend — How It's Built (`app/`)

### `app/main.py` — The Router
Everything the outside world touches lives here:
- **Lifecycle** (`lifespan`): on startup it connects to Supabase, checks the schema,
  and logs DB stats. On shutdown it cleans up.
- **CORS** middleware — allows localhost + the production frontend.
- **Routes** (the API surface):
  - `POST /answer` — the heart of RAG (question → cited answer)
  - `GET /questions` — pull the prerequisite questions
  - `POST /seed` — load the knowledge base
  - `POST /fetch-scheme` — pull a live govt page into the DB
  - `POST /api/generate` — build Results/Dashboard/Docs bundle
  - `GET /api/history`, `/api/stats`, `/healthz` — dashboard + health
  - `GET /tools`, `/tools/gemini` — AI function-calling definitions
- **Static site mount** — serves `static/site/` for all pages.

### `app/core/config.py` — The Settings
- Uses `pydantic-settings` to read `.env`.
- Holds Supabase URL/keys, AI provider choice (`AI_PROVIDER`), embedding provider
  (`EMBEDDING_PROVIDER`), chunk sizes, top-k, temperature, model names, retries.
- **Important:** `embedding_dimensions` (768) must match the SQL `VECTOR(768)` column.

### `app/core/database.py` — The Supabase Layer
- Creates **two clients**: anon (frontend) + service-role (backend, admin).
- `upsert_chunks()` — stores chunk text + embedding into `rag_chunks`.
- `vector_search()` — calls the `match_chunks()` Postgres RPC for similarity search.
- `health_check()` — a simple query to test connectivity.

### `app/services/` — The Brain (each = one responsibility)
| Service | Job |
|---------|-----|
| `rag.py` | **Orchestrates everything** for `/answer` and `/seed` |
| `chat.py` | Sends the prompt to the LLM. Contains the **SAHAYAK system prompt** (the "rules") |
| `embedding.py` | Calls Gemini (or OpenAI) to turn text into numbers |
| `chunker.py` | Splits long documents into smaller overlapping chunks |
| `questions.py` | The bilingual prerequisite questions list |
| `generate.py` | Auto-builds Results/Dashboard/Docs bundle via Groq |
| `history.py` | Logs each Q&A to `chat_history` for the dashboard |
| `govt_source.py` | Fetches + ingests a live official govt page |
| `tools.py` | Declares the function-calling tools for AI agents |

### `app/data/default_documents.py` — The Knowledge Base
- **10 verified scheme documents** (Stand-Up, PMEGP, MUDRA, NSFDC, ASIIM, Nai Roshni,
  DDU-GKY, PM SVANidhi, CGTMSE, PM Vishwakarma).
- Each has facts verified against official portals + a `verified_on` date.
- This is **what the AI is allowed to answer from**.

### `app/models/` — Requests & Responses
- Pydantic schemas that define the exact JSON shape accepted (`/requests.py`) and
  returned (`/responses.py`) by every endpoint. This is what makes FastAPI's `/docs`
  self-documenting.

---

## 🧠 How the RAG Pipeline Actually Runs (Step by Step)

When a user asks something in the chat, this happens:

```
 1. USER types  "मुझे सिलाई मशीन के लिए 2 लाख चाहिए"
 2. frontend extractProfile()   → pulls SC, Tailoring, 2 lakh, Rural from the text (keywords)
 3. frontend buildProfilePayload() → sends {query + profile} to POST /answer
 4. rag.answer_query():
    a. _build_retrieval_query()  → "query + profile facts" (better retrieval)
    b. embed_query()             → Gemini turns it into a 768-number vector
       💡 KEY FIX: uses task_type="RETRIEVAL_DOCUMENT" (same as stored chunks)
          so the query and document vectors are in the SAME space.
    c. vector_search()           → match_chunks() RPC returns top-6 similar chunks
    d. _prepare_context()        → dedup by chunk prefix (MMR-lite)
    e. _should_ask_prerequisites() → if a scheme question with no profile, flag it
    f. chat.generate_answer()    → sends context + SAHAYAK prompt to Groq
    g. _extract_citations()      → parses [chunk_id] markers from the answer
 5. returns { text, citations, profile_used, needs_prerequisites, debug }
 6. history.record() → saves Q&A to chat_history (best-effort)
 7. frontend renders the answer; [chunk_id] chips show as "Sources"
```

### The SAHAYAK System Prompt (why we won't hallucinate)
The prompt in `chat.py` has **hard rules**:
- Answer **only** from the provided context, cite every claim with `[chunk_id]`.
- If context doesn't have it, **say so** — never invent schemes, amounts, or rates.
- **Never** say "you are eligible / approved" — hedge instead. Eligibility stays with the
  rules engine (a separate component).
- Reply in **the same language** the user used.

---

## 🌐 Frontend — How It's Built (`static/site/`)

### Page flow (the "journey")
```
 index.html ─▶ chat.html ─▶ (answer + profile) ─▶ /api/generate ─▶ results.html
                                                       │
                                                       ├─▶ dashboard.html
                                                       └─▶ documentation.html
```

### Key files
| File | Job |
|------|-----|
| `index.html` | Landing / hero + animated orbs |
| `chat.html` + `chat-logic.js` | The chatbot UI + logic (below) |
| `results.html` | Renders matched schemes from generated bundle |
| `dashboard.html` | Goal summary + Q&A history |
| `documentation.html` | Printable document checklist |
| `login.html` | Supabase Auth sign-in/sign-up + demo accounts |
| `site-config.js` | **Supabase client** + session + profile (localStorage) |
| `app.js` | Shared header/nav/language-toggle + scheme data + page render |
| `scheme-catalog.js` | Scheme display metadata + doc loader |

### `chat-logic.js` — The Chat Engine (important!)
- `extractProfile(text)` — scans the user's Hinglish message with **regex keywords**
  to auto-fill the profile (SC/OBC, tailoring/vendor, 2 lakh/10 thousand, rural/urban…).
- `buildProfilePayload()` — turns the profile into the `/answer` request body.
- `ask(query)` — `fetch('/answer')`, renders returned text, turns `[chunk_id]` into
  little **Source chips**, shows smart follow-up suggestions.
- `finish()` — calls `POST /api/generate`, then redirects to `results.html`.
- **Demo commands:** `/demo1` (tailor, ₹2L, SC, rural) and `/demo2` (street vendor,
  ₹10K, OBC, urban) — pre-wired profiles + questions, perfect for demos.

### `site-config.js` — Auth + state
- Creates the Supabase browser client (anon key).
- Stores session, profile, and history in **localStorage** (`sa_*` keys).
- Exposes a global `window.Sahayak` object the pages share.

---

## 🗄️ Database (Supabase) — What We Created

### `sql/init_supabase.sql` (run first)
- `CREATE EXTENSION vector;` — enables pgvector.
- `rag_chunks` table: `id`, `chunk_id` (unique), `source`, `text`, `embedding VECTOR(768)`.
- **IVFFlat index** on the vector column (fast cosine search).
- `match_chunks(query_embedding, match_count)` — the similarity-search function
  (returns chunk + similarity score).
- `get_chunk_stats()` — KB stats.
- **RLS policies** — service role has full access; authenticated/anonymous can read
  (for development).

### `sql/chat_history.sql`
- `chat_history` table — every Q&A logged (dashboard feed).
- `record_chat()` helper function.
- Owner-read + service-role-write policies.

### `sql/user_sessions.sql`
- `user_sessions` table — auto-generated Results/Dashboard/Docs bundles, one per query.

---

## 🔐 Configuration — The `.env` File (CRITICAL)

The whole app is driven by environment variables. **The real `.env` is already
configured** in this project. Never commit it (it's gitignored).

| Variable | What it does | Our value |
|----------|--------------|-----------|
| `SUPABASE_URL` | Project URL | `https://tyolutcefkrlyddlxmob.supabase.co` |
| `SUPABASE_ANON_KEY` | Publishable key (frontend) | `sb_publishable_...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Secret key (backend) | `sb_secret_...` |
| `AI_PROVIDER` | Which LLM for chat | `groq` |
| `EMBEDDING_PROVIDER` | Which for embeddings | `gemini` |
| `GROQ_API_KEY` | Groq key (chat) | `gsk_...` |
| `GROQ_CHAT_MODEL` | Groq model | `openai/gpt-oss-20b` |
| `GROQ_BASE_URL` | Groq OpenAI-compat endpoint | `https://api.groq.com/openai/v1` |
| `GEMINI_API_KEY` | Gemini key (embeddings) | `AQ.Ab...` |
| `GEMINI_EMBED_MODEL` | Embedding model | `gemini-embedding-001` |
| `EMBEDDING_DIMENSIONS` | Vector size | `768` |

> ⚠️ **Never** run `cp .env.example .env` if a real `.env` already exists — it overwrites
> the real keys with dummy placeholders and the server breaks with
> `openai.OpenAIError`. We hit this once — don't repeat it.

---

## 🚀 How to Run It (Quick Cheat Sheet)
```bash
cd /Users/sagarkumarjha/Desktop/hackthon/Sahayak
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# open http://localhost:8000
```
Full step-by-step (setup, DB, seeding, tests, troubleshooting) → **`server-run-commands.md`**.

---

## ✅ What "Done" Looks Like (Verify Your Work)
- Server starts with logs: *"Database stats: 12 chunks, 10 sources"*.
- `curl http://localhost:8000/healthz` → `{"status":"ok","database_connected":true}`.
- Open Chat → type `हिंदी में कुछ पूछो` → get a cited answer with Source chips.
- Click **Finish** → redirected to `results.html` with matched schemes + checklist.
- Toggle **हिन्दी/EN** works on every page.
- `/demo1` and `/demo2` render clean demos.

---

## 🐞 Common Issues & Fixes
| Symptom | Cause | Fix |
|---------|-------|-----|
| `openai.OpenAIError: Missing credentials` | `.env` overwritten with dummies | Restore real `.env` keys |
| Server up but "schema not initialized" | SQL not run | Run `sql/init_supabase.sql` |
| `/answer` returns nothing | DB not seeded / dim mismatch | `POST /seed`; check `VECTOR(768)` |
| Port 8000 busy | old uvicorn running | `pkill -f "uvicorn app.main:app"` |
| "Network error — backend चालू है?" | frontend can't reach server | Confirm server on localhost:8000 |

---

## 🧭 Where to Learn More
- **How to run + troubleshoot:** `server-run-commands.md`
- **Pitch + judges + tech + counter-questions:** `pitch-tech-details.md`
- **Live API reference:** open `http://localhost:8000/docs` while the server runs
