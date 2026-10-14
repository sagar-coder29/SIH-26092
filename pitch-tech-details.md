# 🎤 Sahayak — SIH Pitches, Tech-Deep-Dive & Counter-Questions

> **Smart India Hackathon 2026 · Problem Statement SIH26092**
> **Sponsor:** Ministry of Social Justice & Empowerment (MoSJE)

---

# 🟢 PART 1 — THE PITCH (Present This First)

> Say this out loud, with energy, in ~90 seconds. Keep it warm, human, and confident.

## 🗣️ 30-Second Elevator Pitch

> "Namaste, judges! Meet **Sahayak** — Hindi mein 'saathi' bhi, 'help' bhi. 🧡
>
> Crores of marginalized entrepreneurs — SC, OBC, ST, Safai Karamcharis,
> transgender persons, women — **deserve government schemes** that were made for
> them. Par problem ye hai: inhe pata hi nahi hota kis scheme se fayda milega,
> portal scattered hain, aur language aadhi angrezi, aadhi jargon. 📚
>
> Sahayak ek **AI copilot** hai jo Hinglish mein poochhne par — *"मैं सिलाई का काम
> करता हूँ, मशीन के लिए 2 लाख चाहिए"* — karke sahi schemes **dhunde, samjhay, aur
> citations ke saath bataya** ki kyun wo fit ho sakti hain. Aur ek click mein
> Results, Dashboard aur Document Checklist ready! ✅
>
> Aur sabse **khaas baat**: Sahayak sirf explain karta hai, kabhi eligibility fix
> nahi karta — wo decision ek **deterministic rules engine** ke paas hai. Isliye
> factual, auditable aur bhagwan bharose nahi! 🎯"

---

## 🎯 The Problem (Why It Matters)

> Pahle **problem** batao — judge ko empathy chahiye, feature-list nahi.

### The Human Story
- Rani ek **tailor** hai, Kaushalya ek **street vendor**. Inhe loan/subsidy chahiye
  business badhane ke liye.
- Problem: **inhe kya mil sakta hai — pata hi nahi.** ❓
- Government portals **scattered, jargon-heavy** hain — income ceiling, margin money,
  greenfield, collateral-free... ye sab bureaucratic words unke liye ghatna hain. 🏛️
- Schemes jo **inhi ke liye design** ki gayi hain wo **under-utilized** reh jaati
  hain. Aakhri aadmi tak pohonchna fail ho jaata hai.

> **"Ek achi scheme bhi tab tak kaam nahi karti, jab tak user use samjhe na."**

### The Stats to Quote (if challenged)
- 10 se zyada schemes kaam karti hain is user-group ke liye (Stand-Up, PMEGP, MUDRA,
  NSFDC, PM Vishwakarma...). 🗂️
- Ye users **low digital literacy** hain — unhe Hindi/Hinglish mein chahiye.
- Adoption ghisaata hai jab user ko bharosa nahi hota ki wo "eligible" hai.

---

## 💡 The Solution — What Sahayak Does

### The Flow (Demo These Live!)
| Step | What Happens | Where |
|------|--------------|-------|
| 1️⃣ | User apna business goal **Hindi/English/Hinglish** mein likhta hai | `/chat` |
| 2️⃣ | Sahayak **prerequisite questions** poochhta hai (category, stage, amount, location) | `/questions` |
| 3️⃣ | **RAG pipeline** official docs mein se **relevant schemes dhundhta hai** | backend |
| 4️⃣ | **Citations ke saath** batata hai *why each scheme may fit* | `/answer` |
| 5️⃣ | **Results / Dashboard / Documentation** bundle + document checklist | `/api/generate` |
| 6️⃣ | Bilingual **हिन्दी/EN** toggle, Supabase login | every page |

### ✨ Feature Highlights (show these)
- 💬 **Bilingual chatbot** — Hinglish mein poochho, usi bhasha mein jawab.
- 🧠 **RAG over verified official documents** — no hallucination.
- 📊 **One-click report** — Results, Dashboard, Docs, checklist, next steps.
- 🔐 **Login/Signup** with demo accounts (Supabase Auth).
- 🌐 **Language toggle** (हिन्दी / EN) across every page.
- 📄 **Live scheme catalog** — official portals + document checklists.

---

## 🔑 The Core Design Principle (Say This Clearly — It Impresses Judges)

> **"The AI explains and cites — it never decides eligibility."**

- 🧠 **LLM** = *Explainer* — retrieves + cites + hedges.
- ⚖️ **Deterministic rules engine** = *Decision-maker* — the single source of truth
  for ELIGIBLE / UNCERTAIN / NOT_ELIGIBLE.
- ✅ Isse system **auditable, factual, hallucination-free** aur legally-saaf rehta hai.

> Judges se bolo: *"Ye design principle hi hamara differentiator hai — hamne AI ko
> sirf wo kaam diya jo AI achha karta hai (samjhna), aur bharosemand decision ek
> deterministic engine ko."*

---

## 👨‍💼 How to Present to the JUDGES (SIH Internal Round)

### Do / Don't
| ✅ DO | ❌ DON'T |
|-------|----------|
| Pehle **human story** batao (Rani the tailor) | Feature-list mat padho |
| **Live demo karo** — real question type karo | Sirf slides dikhao |
| Design principle pe zor do (AI explains, rules decide) | AI ko "eligibility decider" bolo |
| **Bilingual** dikhao (Hindi type karke) | Sirf English demo |
| Alag-alag profiles dikhao (SC tailor, OBC vendor) | Ek hi scenario baar-baar |
| "No hallucination" prove karo — citations dikhao | Fake claims mat karo |
| Last mein **next steps** (apply kaise) dikhao | Report par ruk jao |

### 5-Minute Pitch Structure
1. **0:00–0:30** — Hook + human story (Rani the tailor). 💬
2. **0:30–1:00** — Problem (scattered, jargon, low adoption).
3. **1:00–2:30** — **LIVE demo**: type Hinglish question → show cited answer →
   show Results/Dashboard/Docs bundle → toggle हिन्दी/EN.
4. **2:30–3:30** — How it works (RAG pipeline one-slide) + design principle.
5. **3:30–4:30** — Tech stack + why Supabase/Gemini/Groq.
6. **4:30–5:00** — Social impact + ask for next step. 🎯

### Demo Tips (Critical!)
- 🔥 **Use `/demo1`** (tailor, ₹2L, SC, rural) — it's pre-wired and safe.
- ⌨️ Type the Hinglish query *live* — *"मुझे सिलाई मशीन के लिए 2 लाख चाहिए"*.
- 🖱️ Show the **citations** — judges love that it's grounded, not made up.
- 📊 After chat hit **"Finish"** → show Results + Dashboard + Documentation.
- 🌐 Toggle **EN/हिन्दी** to prove multilingual.
- ⚠️ Doublespeak disclaimer: *"AI sirf explain karta hai, eligibility bank/meindecides."*

### What Judges Usually Ask (lead with these)
- *"How do we trust the AI isn't hallucinating?"* → citations + verified docs + prompt rules.
- *"Who decides eligibility?"* → deterministic rules engine (not the AI).
- *"Is it bilingual?"* → yes, Hindi/Hinglish/English, Gemini native Hindi.
- *"How is it deployed?"* → FastAPI + Supabase, Docker/Cloud-Run ready.
- *"Can it handle live data?"* → `POST /fetch-scheme` pulls live official pages.

---

# 🛠️ PART 2 — TECH-DEEP-DIVE

## Tech Stack Overview

### Backend — FastAPI (Python 3.11)
- **Framework:** FastAPI (`app/main.py`) — async, Pydantic, auto Swagger at `/docs`.
- **Structure:**
  - `core/config.py` — env-driven settings (`pydantic-settings`)
  - `core/database.py` — Supabase client + vector search + chunk upsert
  - `models/` — Pydantic request/response/entity schemas
  - `services/rag.py` — RAG pipeline orchestration
  - `services/chat.py` — LLM completion + Sahayak system prompt
  - `services/embedding.py` — Gemini/OpenAI embedding abstraction
  - `services/chunker.py` — word-based chunking with overlap
  - `services/questions.py` — prerequisite questions
  - `services/generate.py` — auto-generates Results/Dashboard/Docs bundle
  - `services/history.py` — Q&A logging to dashboard
  - `services/govt_source.py` — fetch + ingest official govt portals
  - `services/tools.py` — AI function-calling definitions
  - `data/default_documents.py` — 10 verified scheme docs (the KB)
- **Server:** uvicorn (port 8000), CORS configured.

### Database — Supabase (PostgreSQL + pgvector + Auth)
- `rag_chunks` table with `VECTOR(768)` + **IVFFlat** index (cosine similarity).
- `match_chunks()` Postgres function — vector retrieval.
- `get_chunk_stats()` — KB stats.
- `chat_history` table — dashboard Q&A log.
- `user_sessions` table — AI-generated bundles.
- **Row Level Security (RLS)**; service-role key for backend ops.

### AI Providers
| Role | Provider | Model / Config |
|------|----------|----------------|
| **Embeddings** | Google Gemini | `gemini-embedding-001`, 768-dim (native Hindi) |
| **Chat LLM** | Groq | OpenAI-compatible, `openai/gpt-oss-20b` |
| **Chat alt** | Gemini / OpenAI / Anthropic | drop-in via `AI_PROVIDER` |
| **Doc ingest** | BeautifulSoup + lxml | fetch official govt portals |

### Frontend — Vanilla HTML/CSS/JS (no build step)
- Served by FastAPI static mount in `static/site/`.
- Pages: index, chat, results, dashboard, documentation, documents, scheme, login.
- Bilingual toggle, Supabase Auth, editable profile panel.

### Deployment
- **Dockerfile** (python:3.11-slim) — Cloud-Run ready (`PORT` env).
- `main.py` = legacy entry point re-exporting `app.main:app`.

---

## 🔁 How the RAG Pipeline Works

1. **Ingestion / Seeding** — `POST /seed` chunks the 10 default docs (~400 tokens,
   15% overlap) → embeds with Gemini → upserts into `rag_chunks`.
2. **Query enrichment** — `_build_retrieval_query()` appends profile facts
   (category, stage, type, amount, location) to the question.
3. **Embed the query** — uses `task_type = "RETRIEVAL_DOCUMENT"` (**same as stored
   chunks**) so query + docs live in the **same embedding space** (a key fix).
4. **Vector search** — `match_chunks()` RPC → top-K (default 6) via cosine distance.
5. **Deduplicate** — MMR-lite: dedup by chunk-id prefix.
6. **Prerequisite check** — scheme question + no profile → `needs_prerequisites=True`.
7. **Generate** — `chat_service.generate_answer()` with the SAHAYAK system prompt
   (hard rules: answer only from context, cite `[chunk_id]`, hedge, no eligibility,
   reply in user's language).
8. **Extract citations** — regex `[chunk_id]` markers; falls back to top chunks.
9. **Log history** (best-effort) → `chat_history`.

### RAG config knobs (`config.py`)
| Setting | Default | Notes |
|---------|---------|-------|
| `default_top_k` | 6 | chunks retrieved |
| `chunk_size` | 400 | approx tokens/chunk |
| `chunk_overlap` | 60 | 15% overlap |
| `temperature` | 0.1 | low = factual |
| `embedding_dimensions` | 768 | must match SQL VECTOR() |
| `gemini_max_retries` | 4 | transient retry |
| `gemini_retry_delay` | 7.0s | backoff |

---

## 📚 Knowledge Base (10 Verified Schemes)

| # | Scheme | chunk_id | Source |
|---|--------|----------|--------|
| 1 | Stand-Up India | `scheme_standup_india_v1` | standupmitra.in |
| 2 | PMEGP | `scheme_pmegp_v1` | kviconline.gov.in/pmegp |
| 3 | MUDRA (PMMY) | `scheme_mudra_pmmy_v1` | mudra.org.in |
| 4 | NSFDC | `scheme_nsfdc_v1` | nsfdc.nic.in |
| 5 | ASIIM | `scheme_asiiim_v1` | vcfsc.in/asiim |
| 6 | Nai Roshni | `scheme_nai_roshni_v1` | minorityaffairs.gov.in |
| 7 | DDU-GKY | `scheme_ddu_gky_v1` | ddugky.gov.in |
| 8 | PM SVANidhi | `scheme_pm_svanidhi_v1` | pmavanidhi.gov.in |
| 9 | CGTMSE | `scheme_credit_guarantee_v1` | cgtmse.in |
| 10 | PM Vishwakarma | `scheme_pm_vishwakarma_v1` | pmvishwakarma.gov.in |

Each doc includes amounts, eligibility focus, and **how it differs** (e.g. Nai Roshni =
training not loan; PM SVANidhi = small vendor micro-loans). `POST /fetch-scheme` fetches
**live** official pages to keep the KB fresh.

---

# ❓ PART 3 — COUNTER-QUESTIONS & ANSWERS

**Q1: "How do we prevent the AI from hallucinating schemes or amounts?"**
- Answer generated **only from retrieved official context**; system prompt hard rules:
  never invent names/amounts/deadlines; cite with `[chunk_id]`; say plainly when thin.
  All 10 KB docs verified against official portals.

**Q2: "Who decides eligibility?"**
- **A deterministic rules engine decides; the AI only explains.** Enforced in
  architecture and restated in the prompt. The AI describes criteria; it never says
  "you are eligible / approved."

**Q3: "Why did vector search return nothing / poor results?"**
- We embed queries with `RETRIEVAL_DOCUMENT` so query + docs share the same subspace.
  Also `EMBEDDING_DIMENSIONS` (768) must match SQL `VECTOR(768)`.

**Q4: "Which AI providers?"**
- Chat: **Groq** (default) + Gemini/OpenAI/Anthropic via `AI_PROVIDER`.
- Embeddings: **Gemini** (native Hindi) or OpenAI via `EMBEDDING_PROVIDER`.

**Q5: "Is it bilingual?"**
- Yes — answers in the same language the user used; Gemini embeds Hindi natively;
  site has a हिन्दी/EN toggle; prerequisite questions in Hindi + English.

**Q6: "Does it handle low digital literacy?"**
- Short plain sentences, jargon explained, scheme names spelled out; guided document
  checklist + next steps auto-generated after the chat.

**Q7: "What if scheme details change after our demo?"**
- `POST /fetch-scheme` fetches the **current** text from official portals live.
  KB docs carry a `verified_on` date; rules engine remains the authority.

**Q8: "How is the Results/Dashboard/Documentation generated?"**
- `POST /api/generate` (Groq) takes final question + cited answer + profile → returns
  a structured bundle (matched schemes, checklist, dashboard, next steps), saved
  best-effort to `user_sessions`.

**Q9: "Is it production-ready / auditable?"**
- Deterministic rules = source of truth (auditable). RLS on Supabase tables.
  Service-role key only server-side. Best-effort persistence never blocks an answer.
  Docker + Cloud Run ready.

**Q10: "What's the architecture / can I run it myself?"**
- FastAPI + Supabase + Gemini embeddings + Groq LLM + vanilla JS frontend. Fully
  local-runnable — see **`server-run-commands.md`**.

---

## 📊 Dashboard / Monitoring
- `/api/history` — per-user Q&A log (or all users if admin).
- `/api/stats` — total queries + unique users.
- `/healthz` — DB connectivity health check.

---

## ✍️ Credits
- **Smart India Hackathon 2026** · Problem Statement **SIH26092**
- **Ministry of Social Justice & Empowerment (MoSJE)** — Sponsor
- **Supabase** — Postgres + pgvector + Auth
- **Groq** — Fast AI inference
- **Google Gemini** — Bilingual embeddings

*Built for Smart India Hackathon 2026. Not for commercial use.*
