# 🇮🇳 Sahayak — AI-Driven Scheme Matching for Marginalized Entrepreneurs

> **Smart India Hackathon 2026 · Problem Statement SIH26092**
> **Sponsor:** Ministry of Social Justice & Empowerment (MoSJE)

Sahayak is an AI-powered platform that helps marginalized entrepreneurs (SC, OBC, ST,
DNT, Safai Karamcharis, transgender persons, PwD, and women from marginalized communities)
discover and understand government business-support schemes.

Users describe their business goal in **Hindi, English, or Hinglish** — and the system:

1. Retrieves the most relevant schemes from official source documents (RAG).
2. Explains **why each scheme may fit** their goal, with short **citations**.
3. Auto-generates a personalized **Results / Dashboard / Documentation** bundle with a
   document checklist and next steps.

**Key design principle:** *The AI explains and cites — it never decides eligibility.*
Deterministic rules (a separate engine) are the single source of truth for whether someone
is eligible. This keeps the AI factual and auditable.

---

## ✨ Features

- 💬 **Bilingual chatbot** — ask in Hindi, English, or Hinglish; answers in the same language.
- 🧠 **RAG pipeline** — Gemini embeddings (768-dim) + Supabase pgvector similarity search over
  10 pre-seeded official scheme documents, answered by a cited Groq LLM.
- 📝 **Auto profile extraction** — the chat picks out category, business, stage, amount and
  location from plain-text answers and updates the profile panel live.
- 📊 **One-click report generation** — "Finish" turns the conversation into a personalized
  Results, Dashboard and Documentation bundle.
- 🔐 **Login / Sign up** with demo accounts (Supabase Auth).
- 🌐 **Language toggle** (हिन्दी / EN) across every page.
- 📄 **Live scheme catalog** — official portals, document checklists, eligibility notes.

---

## 🗂️ Folder Structure — What Each Part Does

```
Sahayak/
├── app/                          # FastAPI backend (Python 3.11)
│   ├── main.py                   # Routes, CORS, static site mounting, lifecycle
│   ├── core/
│   │   ├── config.py             # Env-driven settings (Supabase, AI providers, RAG params)
│   │   └── database.py           # Supabase client + vector search + chunk upsert
│   ├── models/
│   │   ├── requests.py           # Pydantic request schemas (/answer, /seed, /fetch-scheme, /api/generate)
│   │   ├── responses.py          # Pydantic response schemas
│   │   └── entities.py           # DB entity models (RagChunk, SearchResult)
│   ├── services/
│   │   ├── rag.py                # RAG pipeline orchestration (build query → embed → search → cite)
│   │   ├── chat.py               # Groq/Gemini/OpenAI/Anthropic chat completion + Sahayak prompt
│   │   ├── embedding.py          # Gemini (default) / OpenAI embedding abstraction
│   │   ├── chunker.py            # Word-based text chunking with overlap
│   │   ├── questions.py          # Prerequisite (pre-requesting) questions
│   │   ├── generate.py           # Auto-generates Results/Dashboard/Docs JSON bundle
│   │   ├── history.py            # Q&A history logging (supabase chat_history)
│   │   ├── govt_source.py        # Fetch + ingest official govt scheme portals
│   │   └── tools.py              # AI function-calling definitions (Gemini /docs)
│   └── data/
│       └── default_documents.py  # 10 verified scheme documents seeded into the KB
│
├── static/site/                  # Frontend (vanilla HTML/CSS/JS, no build step)
│   ├── index.html                # Landing page (animated hero, bilingual)
│   ├── chat.html                 # RAG chatbot + editable profile panel
│   ├── results.html              # AI-generated matched schemes + checklist + next steps
│   ├── dashboard.html            # Personalized goal summary + Q&A history
│   ├── documentation.html        # Printable scheme documentation
│   ├── documents.html            # Scheme catalog (knowledge-base editor view)
│   ├── scheme.html               # Single-scheme detail page
│   ├── login.html                # Sign in / Sign up + demo accounts
│   ├── style.css                 # Main design system
│   ├── pages.css                 # Page-specific styles
│   ├── app.js                    # Shared header/nav/language/auth logic
│   ├── chat-logic.js             # Chat engine (RAG calls, profile, demo commands)
│   ├── site-config.js            # Supabase client + auth + profile localStorage
│   ├── scheme-catalog.js         # Scheme display metadata + document loader
│   └── images/                   # Site illustrations
│
├── sql/                          # Supabase / Postgres database scripts
│   ├── init_supabase.sql         # Tables, indexes, match_chunks() vector search function
│   ├── chat_history.sql          # Q&A history table
│   └── user_sessions.sql         # Auto-generated result bundles table
│
├── venv/                         # Python virtual environment (created during install)
├── main.py                       # Entry point → imports app.main:app
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container build (Cloud Run ready)
├── .env.example                  # Template for environment config
├── .env                          # Live config (Supabase + AI keys) — gitignored
└── .gitignore
```

---

## 🚀 Installation (macOS / Linux)

### Prerequisites
- **Python 3.11+**
- A **Supabase** project (free tier works) — create tables first (see "Database Setup")
- A **Groq** API key (free tier works) for chat + generation
- A **Gemini** API key via Google AI Studio for embeddings

### Step 1 — Clone / open the project

```bash
cd Sahayak
```

### Step 2 — Create the virtual environment & install dependencies

```bash
python3.11 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3 — Configure environment

```bash
cp .env.example .env
# Edit .env with your real keys:
#   SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
#   GROQ_API_KEY, GEMINI_API_KEY
```

Minimal working `.env`:

```ini
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_publishable_key
SUPABASE_SERVICE_ROLE_KEY=your_secret_key
AI_PROVIDER=groq
EMBEDDING_PROVIDER=gemini
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AI...
EMBEDDING_DIMENSIONS=768
```

> ⚠️ `EMBEDDING_DIMENSIONS` **must** match the `VECTOR(...)` column created in
> `sql/init_supabase.sql` (768 = Gemini default). If you switch to OpenAI embeddings,
> change both to `1536` and re-run the SQL + re-seed.

### Step 4 — Set up the database (Supabase)

1. Open your Supabase project dashboard.
2. Go to **SQL Editor**.
3. Run `sql/init_supabase.sql`, then `sql/chat_history.sql`, then `sql/user_sessions.sql`.

### Step 5 — Start the server

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or run from the repo root with the one-liner entry point:

```bash
./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 6 — Open the website

**http://localhost:8000** 🎉

### Step 7 — Seed the knowledge base (first run only)

```bash
curl -X POST http://localhost:8000/seed
```

This chunks, embeds and stores the 10 default scheme documents in Supabase. Already done on
your project, but re-run after switching embedding providers.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Landing page |
| `GET` | `/chat` `results` `dashboard` `documentation` `documents` `scheme` `login` | Frontend pages |
| `POST` | `/answer` | 💬 RAG: ask a question → cited answer |
| `GET` | `/questions` | Prerequisite questions for scheme matching |
| `POST` | `/api/generate` | 🤖 Auto-generate Results/Dashboard/Docs bundle |
| `POST` | `/seed` | Seed knowledge base with scheme documents |
| `GET` | `/documents` | Default documents used for seeding |
| `GET` | `/schemes` | List official govt source portals |
| `POST` | `/fetch-scheme` | Fetch + ingest a page from an official govt portal |
| `GET` | `/tools` `/tools/gemini` | AI function-calling definitions |
| `GET` | `/api/history` `/api/stats` | Dashboard Q&A history + usage stats |
| `GET` | `/healthz` | Health check (DB connectivity) |
| `GET` | `/docs` | Interactive API documentation (Swagger) |

### Example: ask a question

```bash
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{"query":"मुझे सिलाई मशीन के लिए 2 लाख चाहिए","profile":{"category":"SC","business_type":"Tailoring","business_stage":"New / first venture","loan_amount":"2 lakh","location":"Rural"}}'
```

### Example: auto-generate a results bundle

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"query":"test","answer":"test","citations":["a"],"profile":{},"user_email":"test@test.com","full_name":"Test User"}'
```

---

## 🤖 AI Providers

| Setting | Default | Description |
|---------|---------|-------------|
| `AI_PROVIDER` | `groq` | Chat + generation provider (`groq` \| `gemini` \| `openai` \| `anthropic`) |
| `GROQ_CHAT_MODEL` | `openai/gpt-oss-20b` | Groq model used for answers |
| `EMBEDDING_PROVIDER` | `gemini` | Embeddings (`gemini` \| `openai`) |
| `GEMINI_EMBED_MODEL` | `gemini-embedding-001` | Gemini embedding model (native Hindi) |
| `EMBEDDING_DIMENSIONS` | `768` | Vector size — must match the SQL `VECTOR()` column |

---

## 🧪 Quick Test

```bash
# Health check
curl http://localhost:8000/healthz

# All pages return 200
for p in "" chat results dashboard documentation login scheme documents; do
  printf "/%-14s %s\n" "${p:-index}" "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/$p)"
done
```

In the chat, try the demo commands: `/demo1` (tailor needing ₹2L, SC, rural) and
`/demo2` (street vendor needing ₹10K, OBC, urban).

---

## 🛡️ Design Principles

1. **AI Explains, Rules Decide** — the LLM retrieves + cites; eligibility is a separate deterministic engine.
2. **Never Hallucinate Schemes** — answers are grounded in official source documents only.
3. **Hedged Language** — "you may be eligible", "check with the bank" — never definitive claims.
4. **Bilingual by Default** — Hindi + English, natural Hinglish support.
5. **Best-Effort Persistence** — the backend never fails if history/session logging errors out.
6. **Profile-Aware Retrieval** — category, business, stage, amount, location enrich vector search.

---

## 🚢 Deployment

### Docker

```bash
docker build -t sahayakai .
docker run -p 8000:8000 --env-file .env sahayakai
```

### Google Cloud Run

```bash
gcloud run deploy sahayakai --source . --port 8000
```

---

## 🙏 Credits

- **Smart India Hackathon 2026** — Problem Statement SIH26092
- **Ministry of Social Justice & Empowerment** — Sponsor
- **Supabase** — Database + pgvector + Auth
- **Groq** — Fast AI inference
- **Google Gemini** — Embeddings (native Hindi support)

Built for Smart India Hackathon 2026. Not for commercial use.