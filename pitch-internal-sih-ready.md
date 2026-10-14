# 🎤 Sahayak — Internal SIH-2026 Pitch (Ready to Present)

> **Smart India Hackathon 2026 · Problem Statement SIH26092**
> **Sponsor:** Ministry of Social Justice & Empowerment (MoSJE)
> **Format:** ~3–5 minute internal round pitch, live demo, then Q&A

---

## 🗣️ OPENING (0:00–0:30) — Hook + the one-liner

> *"Namaste judges. Meet **Sahayak** — in Hindi it means both 'companion' and 'help'.*
>
> *Crores of marginalized entrepreneurs — SC, OBC, ST, Safai Karamcharis, transgender persons, women — are the exact people our government schemes were built for. Yet most of them never reach those schemes.*
>
> *Sahayak is an AI copilot where you simply say — in Hindi, English or Hinglish — 'मैं सिलाई का काम करता हूँ, मशीन के लिए 2 लाख चाहिए' — and it finds the right scheme, explains why it fits, and hands you a ready document checklist to apply. Nothing more, nothing less."*

---

## 😢 THE PROBLEM (0:30–1:00) — Human story first, not features

**Meet Rani, a tailor in Bihar — and Kaushalya, a street vendor.**

- They need a loan or subsidy to grow their business. The schemes exist — Stand-Up India, PMEGP, MUDRA, NSFDC, PM SVANidhi, PM Vishwakarma… 10+ schemes map directly to people like them.
- **The gap isn't money. It's information.** Portals are scattered. Language is bureaucratic jargon — income ceiling, margin money, collateral-free, greenfield. For a low-digital-literacy user, these words are a wall.
- Result: **the very schemes designed for them stay under-utilized.** Government fails to reach the last person.

> **"A good scheme doesn't work until the user understands it."**

**Numbers to quote if challenged:**
- 10+ active central schemes target this user group.
- Users need Hindi/Hinglish — official pages are mostly English-first.
- Adoption collapses when people don't believe they're eligible.

---

## 💡 THE SOLUTION (1:00–2:30) — What Sahayak does + LIVE DEMO

### The journey (demo these live)
1. User types a goal in **Hindi/English/Hinglish** — no forms. (`/chat`)
2. Sahayak asks a few **prerequisite questions** — category, stage, amount, location.
3. **RAG pipeline** searches only official, verified scheme documents.
4. It answers **with citations** — explaining *why* each scheme may fit.
5. One click → **Results + Dashboard + Documentation** bundle with a document checklist and next steps. (`/api/generate`)
6. Fully **bilingual** — हिन्दी/EN toggle everywhere.

### 🔥 Demo script (safe path)
- Use **`/demo1`** (tailor, ₹2 lakh, SC, rural) — pre-wired, reliable.
- Type the Hinglish query live.
- **Show the Source chips / citations** — this proves it's grounded, not made up.
- Click **Finish** → show Results, Dashboard, Documentation.
- Toggle **हिन्दी / EN** to prove multilingual.
- Say: *"Every claim carries a citation. Try to break it — it answers only from documents it can cite."*

---

## 🔑 THE DESIGN PRINCIPLE (2:30–3:00) — The differentiator, say this clearly

> **"The AI explains and cites — it never decides eligibility."**

- 🧠 **LLM = Explainer** — retrieves, cites, and hedges ("you *may* be eligible").
- ⚖️ **Deterministic rules engine = Decision-maker** — the single auditable source of truth for eligibility.
- ✅ The result is **factual, hallucination-resistant, and legally clean.**

> *"We gave the AI only what AI is great at — understanding and explaining. The decision of who is eligible stays with rules humans can audit. That's why Sahayak won't ever tell someone 'you're approved' — the bank does."*

---

## ⚙️ HOW IT WORKS + TECH STACK (3:00–4:00) — one slide, keep it tight

```
 User goal (Hinglish) → Gemini embedding (768-dim, native Hindi)
        → pgvector search in Supabase (top-6 chunks, cosine similarity)
        → Groq LLM answers ONLY from those chunks, with [chunk-id] citations
        → one-click /api/generate → Results + Dashboard + Doc checklist bundle
```

| Layer | Choice | Why |
|-------|--------|-----|
| Backend | **FastAPI (Python 3.11)** | async, Pydantic, auto Swagger, Cloud-Run ready |
| Database | **Supabase Postgres + pgvector + Auth + RLS** | vector search + authed sessions in one place |
| Embeddings | **Gemini `gemini-embedding-001`** (768-dim, `RETRIEVAL_DOCUMENT` task) | native Hindi, same vector space for query + docs |
| Chat LLM | **Groq** (`openai/gpt-oss-20b`) | fast (~2.4s answers, low temperature = factual) |
| Frontend | **Vanilla HTML/CSS/JS** | zero build step, served by FastAPI, runs anywhere |
| Knowledge base | **10 verified scheme docs** + live `POST /fetch-scheme` ingest | answers stay current from official portals |

**Measured performance (live):** `/answer` in **3.5s**, `/api/generate` in **1.8s**, all 8 pages < 2ms static. (audir.md)

---

## 📈 SCOPE, SCALING & ROADMAP (4:00–4:30)

**Current:** 10 central schemes (Stand-Up, PMEGP, MUDRA, NSFDC, ASIIM, Nai Roshni, DDU-GKY, PM SVANidhi, CGTMSE, PM Vishwakarma), Hindi+English front-to-back, login, dashboard, EMI calculator.

**Scaling:**
- **More schemes** — state schemes + live `fetch-scheme` ingestion keeps KB fresh.
- **Voice-first** — Bhashini route for fully illiterate users (voice input already stubbed in the UI 🎤).
- **CSC / field-worker mode** — guided onboarding where a CSC agent enters the goal on the user's behalf.
- **Rules engine API** — make the deterministic eligibility engine a first-class public endpoint.

**Impact:** every 1% adoption gain across this user group turns thousands of under-used schemes into real loans, real training, real enterprises.

---

## ❓ TOP 5 JUDGE QUESTIONS (lead with these)

| Question | Answer (1 line) |
|----------|-----------------|
| "How do we know the AI isn't hallucinating?" | Answers are generated **only from cited official docs** — "no citation, no claim". |
| "Who decides eligibility?" | **Rules engine, not the AI.** AI explains criteria; it never says "eligible". |
| "Is it bilingual in practice?" | Yes — answers in the user's language; Gemini embeds Hindi natively; EN/हिन्दी toggle site-wide. |
| "What if scheme details change?" | `POST /fetch-scheme` pulls the **current official page** live; docs carry a `verified_on` date. |
| "Is it production-ready / auditable?" | Deterministic rules = source of truth, RLS on Supabase, keys server-side only, Docker + Cloud Run ready. |

---

## 🎯 CLOSE (4:30–5:00) — the ask

> *"Judges, government schemes are the intent. **Sahayak is the last-mile delivery.** We proved it works live, with citations, in two languages, in under five seconds.*
>
> *The next step is clear: more schemes, voice support, and field-worker mode so no entrepreneur — however remote — is left out of the schemes meant for them. Thank you — and we'd love your questions."*

---

## 🚫 PRESENTATION RULES (internal round)

- ✅ **Demo live first** — use `/demo1`, show citations, click Finish, toggle language.
- ✅ **Tell the human story** before any feature talk.
- ✅ **Say the design principle out loud** — it's your edge over other teams.
- ✅ **Hedge language**: *"may be eligible", "check with the bank"* — precisely what proves maturity.
- ❌ Don't read slides or the feature list.
- ❌ Don't claim stats we can't back (say "10 verified schemes", not "15+").
- ❌ Don't call the AI the "eligibility decider" — the rules engine is.

*Built for Smart India Hackathon 2026 · Problem Statement SIH26092 · MoSJE*