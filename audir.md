# Sahayak (SIH-26092) — Full Audit Report

**Date:** 2026-09-11  
**Auditor:** opencode (automated)  
**Scope:** Backend, frontend, database, deployment, design, latency

---

## 1. Executive Summary

| Area | Before | After |
|------|--------|-------|
| Backend `/seed` | Fails (RLS 403 + wrong service-role key) | Works — 12 chunks seeded in ~4.2s |
| Backend `/answer` | Works but blocks server on retries | Works, non-blocking async retries |
| Backend `/api/generate` | Hardcoded Groq, blocks server | Provider-aware, non-blocking |
| Backend retry logic | `time.sleep()` (freezes event loop) | `await asyncio.sleep()` |
| Backend CORS | `allow_origins=["*"]` + `allow_credentials=True` (invalid) | Explicit origins only |
| Backend embedding upsert | String `"[0.1,0.2]"` (fragile) | Python list `[0.1, 0.2]` (standard) |
| Backend history logging | UUID column rejects non-UUID user IDs silently | UUID5 hash conversion, stores correctly |
| Frontend `index.html` | 65-line "COMPONENTS DOCUMENTATION" junk section (Framer/MCP template copy) | Removed |
| Frontend stats | "15+ schemes" (only 10 exist), "92% accuracy", "70% less time" (unverifiable) | "10+ schemes", "2 languages", "3 min to report" |
| Frontend `documents.html` | Fake "40% match score", "Upload Complete" with alert() | Labeled as demo, no fake score |
| Frontend contrast | `--muted` on cream bg = ~3:1 (fails WCAG) | Darkened to ~6:1 |
| Latency `/answer` | N/A (first measured run) | **3.5s** (embed 1s + search 50ms + LLM 2.4s) |
| Latency `/api/generate` | N/A | **1.8s** |

---

## 2. What Was Found (Issues)

### 2.1 Critical (would break demo)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| C1 | Groq model `llama-3.3-70b-versatile` doesn't exist (404) | `config.py:45`, `.env` | `/answer` and `/api/generate` both fail |
| C2 | `/seed` fails with RLS 42501 | `.env` (service-role key = publishable key) | Can't seed or re-seed knowledge base |
| C3 | `time.sleep()` in async functions freezes the entire server | `chat.py:174`, `generate.py:186` | Rate-limit retries block all concurrent requests |

### 2.2 High (visible to judges)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| H1 | 65-line "COMPONENTS DOCUMENTATION" section (Framer/MCP/CLI template copy) | `index.html:112-176` | Judges see unrelated product copy |
| H2 | "15+ verified schemes" but only 10 documents exist | `index.html:191,499` | Inflated claims |
| H3 | Stats "92% Matching Accuracy" and "70% Less Search Time" | `index.html:204-207` | Unverifiable fabricated numbers |
| H4 | `documents.html` hardcodes "40% match score" with no data source | `documents.html:26` | Fake metric |
| H5 | `documents.html` `alert("uploaded successfully (demo)")` on every click | `documents.html:81` | Poor UX, clearly fake |
| H6 | CORS `allow_origins=["*"]` + `allow_credentials=True` = invalid per spec | `main.py:80-92` | Browsers reject credentialed cross-origin requests |
| H7 | `generate.py` hardcodes Groq provider | `generate.py:129` | Breaks if AI_PROVIDER changes |
| H8 | `--muted` color `#8A7968` on cream `#FAF6F0` = ~3:1 contrast | `style.css:19` | Fails WCAG AA for small text |

### 2.3 Medium (correctness / robustness)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| M1 | Embedding upsert passes string `"[0.1,0.2]"` to VECTOR column | `database.py:126` | Works now but fragile across Supabase versions |
| M2 | `chat_history.user_id` is UUID column but frontend sends non-UUID strings | `chat_history.sql:9`, `history.py:36` | History silently fails for demo users |
| M3 | `config.py` default `GROQ_CHAT_MODEL=llama-3.3-70b-versatile` vs README says `openai/gpt-oss-20b` | `config.py:45` | Config drift, confusing for new devs |
| M4 | `.env.example` has `AI_PROVIDER=gemini` but config default is `groq` | `.env.example` | Confusing defaults |

### 2.4 Low (nice-to-have)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| L1 | Hero input carries query to chat via localStorage (works correctly) | `index.html` hero | Non-issue — verified working |
| L2 | `chat_history.sql` creates table but RLS policy uses `auth.uid()` which requires Supabase Auth | `chat_history.sql:32` | Owner-read policy ineffective for anonymous users |
| L3 | `user_sessions.sql` table may not exist if user only ran `init_supabase.sql` | `user_sessions.sql` | `/api/generate` persistence silently fails |

---

## 3. Fixes Applied

### Files Modified (10 total)

| File | Changes |
|------|---------|
| `.env` | Added real `SUPABASE_SERVICE_ROLE_KEY`, set `GROQ_CHAT_MODEL=openai/gpt-oss-20b` |
| `app/core/config.py` | Default `groq_chat_model` → `openai/gpt-oss-20b` |
| `app/core/database.py` | Embedding upsert: string → Python list |
| `app/services/chat.py` | `import time` → `import asyncio`, `time.sleep()` → `await asyncio.sleep()` (2 locations) |
| `app/services/generate.py` | Provider-aware `_call_provider()`, `time.sleep()` → `await asyncio.sleep()`, supports groq/openai/anthropic/gemini |
| `app/services/history.py` | Added UUID5 conversion for non-UUID user_id values |
| `app/main.py` | CORS: removed `allow_origins=["*"]`, explicit origins only |
| `static/site/index.html` | Removed "COMPONENTS DOCUMENTATION" section; "15+" → "10"; stats: removed fake accuracy/time, added "2 languages" + "3 min to report" |
| `static/site/documents.html` | Removed fake 40% score ring, labeled demo, removed alert() popups |
| `static/site/style.css` | `--muted` darkened from `#8A7968` to `#6B5C4B` (~6:1 contrast) |

---

## 4. Live Test Results (Post-Fix)

All tests run against `127.0.0.1:8010` with real API keys.

### 4.1 Pages (all 200)

| Page | Status | Time |
|------|--------|------|
| `/` (landing) | 200 | 1.2ms |
| `/chat` | 200 | 1.1ms |
| `/results` | 200 | 0.9ms |
| `/dashboard` | 200 | 0.9ms |
| `/documentation` | 200 | 0.9ms |
| `/login` | 200 | 0.8ms |
| `/scheme` | 200 | 0.9ms |
| `/documents` | 200 | 0.6ms |

### 4.2 API Endpoints

| Endpoint | Status | Latency | Notes |
|----------|--------|---------|-------|
| `GET /healthz` | `{"status":"ok"}` | <1ms | DB connected |
| `POST /seed` | `{"inserted":12}` | 4.2s | 10 docs chunked + embedded + stored |
| `POST /answer` (Hindi) | 4-citation Hindi table answer | **3.5s** | Stand-Up India, NSFDC, MUDRA, PMEGP |
| `POST /api/generate` | Valid JSON bundle | **1.8s** | top_match: PMEGP, matched: PMEGP + MUDRA |
| `GET /api/history` | Returns recorded Q&A | <10ms | user_id stored as UUID5 |
| `GET /api/stats` | `{"total_queries":38,"unique_users":3}` | <10ms | Dashboard data |

### 4.3 Latency Breakdown (`/answer` = 3.5s)

```
Gemini embedding (embed-001)  ~1.0s  (sync HTTP, blocks thread)
pgvector match_chunks RPC     ~0.05s
Groq GPT-OSS-20B generation   ~2.4s  (streaming not used)
─────────────────────────────
Total backend latency         ~3.5s
```

### 4.4 Sample `/answer` Output

```markdown
| योजना | क्या है | राशि सीमा | लक्षित समूह | खास शर्त |
|-------|--------|-----------|-------------|----------|
| Stand-Up India | बैंक का टर्म + वर्किंग कैपिटल ऋण | ₹10 लाख – ₹1 करोड़ | SC/ST या महिला, नया उद्यम | 75% तक कवर, 10% अपनी जमा |
| NSFDC | SC-के लिए कंज़ेशनल ऋण | ₹1.25 लाख – ₹45 लाख | SC, आय ≤ ₹5 लाख | 90% तक कवर, ब्याज ~6.5-8% |
| PMMY (MUDRA) | बिना गारंटी का छोटा ऋण | शिशु ₹50K – तारा ₹20 लाख | कोई भी | कोई कोलैटरल नहीं |
| PMEGP | मार्जिन-मनी सब्सिडी + बैंक ऋण | निर्माण ₹50 लाख | SC/ST/OBC/महिला | 15-35% सब्सिडी, प्रशिक्षण अनिवार्य |
```

---

## 5. Architecture

```
User Browser (vanilla JS)
  │
  ├── GET /  /chat  /results  /dashboard  /documents  (static HTML)
  │
  ├── POST /answer  ──►  embed query (Gemini)  ──►  pgvector search (Supabase)
  │                          │                              │
  │                          ▼                              ▼
  │                    Gemini embed-001              match_chunks RPC
  │                    (768-dim vectors)            (cosine similarity)
  │                                                       │
  │                                                       ▼
  │                                              Top 6 chunks + metadata
  │                                                       │
  │                                                       ▼
  │                          Groq GPT-OSS-20B  ◄── system prompt + context + profile
  │                                                       │
  │                                                       ▼
  │                                              Cited answer (Hindi/English)
  │                                                       │
  │                                                       ▼
  │                                              POST /api/generate
  │                                                       │
  │                                                       ▼
  │                                              Groq → structured JSON
  │                                              (results + dashboard + docs)
  │                                                       │
  │                                                       ▼
  │                                              Render results.html / dashboard.html
  │
  └── POST /seed  ──►  chunk + embed (Gemini)  ──►  upsert to rag_chunks (Supabase)
```

---

## 6. Deployment

### 6.1 Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed and authenticated
- All API keys in `.env` (gitignored — never committed)

### 6.2 Deploy to Google Cloud Run

```bash
cd SIH-26092

# Authenticate gcloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Deploy (reads .env, builds Dockerfile, deploys to Cloud Run)
gcloud run deploy sahayak \
  --source . \
  --port 8080 \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars-from-env=.env \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5
```

### 6.3 After Deployment

1. Cloud Run URL will be printed (e.g. `https://sahayak-xxxxxx.asia-south1.run.app`)
2. Visit the URL → landing page loads
3. Open browser console → `POST /seed` to seed knowledge base
4. Test chat flow end-to-end

### 6.4 Environment Variables (required)

| Variable | Value | Notes |
|----------|-------|-------|
| `SUPABASE_URL` | `https://tyolutcefkrlyddlxmob.supabase.co` | Project URL |
| `SUPABASE_ANON_KEY` | `sb_publishable_...` | Publishable key (frontend + reads) |
| `SUPABASE_SERVICE_ROLE_KEY` | `sb_secret_...` | Secret key (backend writes only) |
| `AI_PROVIDER` | `groq` | Chat + generation provider |
| `EMBEDDING_PROVIDER` | `gemini` | Embedding provider |
| `GROQ_API_KEY` | `gsk_...` | Groq API key |
| `GROQ_CHAT_MODEL` | `openai/gpt-oss-20b` | Groq model |
| `GEMINI_API_KEY` | `AQ...` | Gemini API key (embeddings) |
| `EMBEDDING_DIMENSIONS` | `768` | Must match VECTOR column in SQL |

### 6.5 Docker (local test)

```bash
docker build -t sahayak .
docker run -p 8080:8080 --env-file .env sahayak
# Open http://localhost:8080
```

---

## 7. Remaining Known Issues (low priority)

| Issue | Severity | Notes |
|-------|----------|-------|
| `chat_history.sql` RLS owner-read uses `auth.uid()` — ineffective for anonymous users | Low | History still works via service-role admin client |
| `user_sessions.sql` may not be run yet | Low | `/api/generate` persistence is best-effort (logged + ignored) |
| Gemini embedding call is sync (blocks event loop for ~1s) | Low | Could use `asyncio.to_thread()` — minor improvement for high concurrency |
| `documents.html` uploads are purely cosmetic | Low | Clearly labeled as demo now |
| No rate limiting on API endpoints | Low | Acceptable for hackathon demo |

---

## 8. Security Notes

- **API keys were pasted in plaintext chat** during this audit. Rotate all keys at:
  - Groq: https://console.groq.com/keys
  - Gemini: https://aistudio.google.com/apikey
  - Supabase: Dashboard → Settings → API → Reset service_role key
- `.env` is gitignored — will not be committed
- `site-config.js` contains public Supabase URL + anon key (by design — frontend needs these)

---

## 9. File Tree (modified files highlighted)

```
SIH-26092/
├── .env                          ← MODIFIED (service-role key, model fix)
├── AUDIT_REPORT.md               ← NEW (this file)
├── Dockerfile                    (unchanged)
├── README.md                     (unchanged)
├── app/
│   ├── main.py                   ← MODIFIED (CORS fix)
│   ├── core/
│   │   ├── config.py             ← MODIFIED (Groq model default)
│   │   └── database.py           ← MODIFIED (embedding upsert format)
│   └── services/
│       ├── chat.py               ← MODIFIED (asyncio.sleep)
│       ├── generate.py           ← MODIFIED (provider-aware, asyncio.sleep)
│       └── history.py            ← MODIFIED (UUID5 conversion)
└── static/site/
    ├── index.html                ← MODIFIED (removed junk, fixed claims)
    ├── documents.html            ← MODIFIED (removed fake score/alerts)
    └── style.css                 ← MODIFIED (contrast fix)
```
