# 🚀 Sahayak — Local Server Run Commands

> Complete command reference to set up and run the Sahayak RAG backend & website on your own machine.
> Tech: **FastAPI** + **Supabase (pgvector)** + **Gemini embeddings** + **Groq LLM**.

---

## 0. Prerequisites (one-time)

- **Python 3.11+** installed (`python3.11 --version`)
- A **Supabase** project (create tables first — see Step 4)
- A **Groq** API key (chat + generation)
- A **Gemini** API key via Google AI Studio (embeddings)

---

## 1. Open the project

```bash
cd /Users/sagarkumarjha/Desktop/hackthon/Sahayak
```

---

## 2. Create the virtual environment & install dependencies

> ⚠️ There are **two venvs** in this folder: `venv` (Python 3.11) and `.venv` (Python 3.14).
> **Always use `venv` (3.11)** — it matches the project requirement and has the correct packages.

```bash
# Create ONLY if it doesn't exist yet
python3.11 -m venv venv

# Activate it
source venv/bin/activate          # Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

`requirements.txt` contents:
```
fastapi>=0.104.0
uvicorn>=0.24.0
python-dotenv>=1.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
supabase>=2.0.0
openai>=1.0.0
anthropic>=0.18.0
google-genai>=1.0.0
rich>=13.0.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
```

---

## 3. Configure environment (.env)

> ⚠️ **CRITICAL:** Do **NOT** run `cp .env.example .env` if a real `.env` already exists —
> it will **overwrite** your real API keys with dummy placeholders and break the server
> (known `openai.OpenAIError` / startup failure). The real `.env` is gitignored.

If a real `.env` **doesn't** exist, create it:

```bash
cp .env.example .env
# then edit .env and fill in your real keys
```

The keys required by the app:

| Variable | Purpose |
|----------|---------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase publishable key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase secret key |
| `AI_PROVIDER` | `groq` (default) \| `gemini` \| `openai` \| `anthropic` |
| `EMBEDDING_PROVIDER` | `gemini` (default) \| `openai` |
| `GROQ_API_KEY` | Groq key (used by chat + generate) |
| `GROQ_CHAT_MODEL` | e.g. `openai/gpt-oss-20b` |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` |
| `GEMINI_API_KEY` | Gemini key (embeddings) |
| `GEMINI_EMBED_MODEL` | `gemini-embedding-001` |
| `EMBEDDING_DIMENSIONS` | `768` — must match SQL `VECTOR()` column |

> ⚠️ `EMBEDDING_DIMENSIONS` **must** match `sql/init_supabase.sql`'s `VECTOR(768)` column.
> If you switch embeddings to OpenAI, change both to `1536` and re-run SQL + re-seed.

---

## 4. Set up the database (Supabase, one-time)

1. Open your Supabase project dashboard → **SQL Editor**.
2. Run these scripts **in order**:
   - `sql/init_supabase.sql` — `rag_chunks` table, pgvector extension, `match_chunks()` + `get_chunk_stats()` functions, indexes, RLS
   - `sql/chat_history.sql` — `chat_history` table (dashboard Q&A log)
   - `sql/user_sessions.sql` — `user_sessions` table (auto-generated Results/Dashboard/Docs bundles)

---

## 5. Start the server

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or with the wheel entry point (no `activate` needed):

```bash
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or run `app/main.py` directly (it has a `__main__` block that runs uvicorn):

```bash
source venv/bin/activate
python app/main.py
```

### Run in background (detached)

```bash
cd /Users/sagarkumarjha/Desktop/hackthon/Sahayak
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/sahayak_server.log 2>&1 &
echo "Server started (PID: $!)"
# watch logs:
tail -f /tmp/sahayak_server.log
```

### Stop the server

```bash
pkill -f "uvicorn app.main:app"
```

---

## 6. Open the website

🌐 **http://localhost:8000**

| Page | URL |
|------|-----|
| Landing | `http://localhost:8000/` |
| Chat (RAG) | `http://localhost:8000/chat` |
| Login / Signup | `http://localhost:8000/login` |
| Dashboard | `http://localhost:8000/dashboard` |
| Results | `http://localhost:8000/results` |
| Scheme catalog | `http://localhost:8000/documents` |
| API docs (Swagger) | `http://localhost:8000/docs` |

---

## 7. Seed the knowledge base (first run only)

```bash
curl -X POST http://localhost:8000/seed
```

Chunks, embeds, and stores the **10 default scheme documents** in Supabase.
Already done on the live project, but re-run after **switching embedding providers** or
after re-creating the DB.

---

## 8. Test the API

### Health check

```bash
curl http://localhost:8000/healthz
```

### Ask a question (RAG)

```bash
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{"query":"मुझे सिलाई मशीन के लिए 2 लाख चाहिए","profile":{"category":"SC","business_type":"Tailoring","business_stage":"New / first venture","loan_amount":"2 lakh","location":"Rural"}}'
```

### Get prerequisite questions

```bash
curl http://localhost:8000/questions
```

### Auto-generate Results/Dashboard/Docs bundle

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"query":"test","answer":"test","citations":["a"],"profile":{},"user_email":"test@test.com","full_name":"Test User"}'
```

### Fetch + ingest a live official govt scheme page

```bash
curl -X POST http://localhost:8000/fetch-scheme \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.kviconline.gov.in/pmegp","scheme":"PMEGP"}'
```

### Verify all pages return 200

```bash
for p in "" chat results dashboard documentation login scheme documents; do
  printf "/%-14s %s\n" "${p:-index}" "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/$p)"
done
```

### Chat demo commands

In the chat UI try `/demo1` (tailor needing ₹2L, SC, rural) and `/demo2`
(street vendor needing ₹10K, OBC, urban).

---

## 9. All API endpoints at a glance

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` `/chat` `/results` `/dashboard` `/documentation` `/documents` `/scheme` `/login` | Frontend pages |
| `POST` | `/answer` | RAG: question → cited answer |
| `GET` | `/questions` | Prerequisite questions |
| `POST` | `/api/generate` | Auto-generate Results/Dashboard/Docs bundle |
| `POST` | `/seed` | Seed knowledge base |
| `GET` | `/documents` | Default documents used for seeding |
| `GET` | `/schemes` | List official govt source portals |
| `POST` | `/fetch-scheme` | Fetch + ingest official govt page |
| `GET` | `/tools` `/tools/gemini` | AI function-calling definitions |
| `GET` | `/api/history` `/api/stats` | Dashboard Q&A history + stats |
| `GET` | `/healthz` | Health check (DB connectivity) |
| `GET` | `/docs` | Swagger interactive docs |

---

## 10. Troubleshooting

**`openai.OpenAIError: Missing credentials`**
→ Your `.env` has a dummy/empty Groq or OpenAI key. Restore the real keys
(`GROQ_API_KEY` is used even though it says "openai" in the traceback).

**Server starts but Supabase shows "schema not initialized"**
→ Run `sql/init_supabase.sql` in your Supabase SQL Editor.

**Empty `/answer` results**
→ DB not seeded. Run `curl -X POST http://localhost:8000/seed`, or re-verify
`EMBEDDING_DIMENSIONS` matches `VECTOR()` (768 for Gemini).

**Port 8000 already in use**
→ Either kill the old process (`pkill -f uvicorn`) or use another port,
e.g. `--port 8001`.
