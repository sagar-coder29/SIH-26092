# Copyright 2024
# Directory: yt-rag/app/services/chat.py

"""
Chat completion service for generating RAG answers.
Supports OpenAI, Anthropic, and Gemini, controlled by AI_PROVIDER.

Prompted for Sahayak (SIH26092): this service is the "Explainer" from
solution.md Feature 3 -- given a retrieved set of scheme-document chunks,
it writes the "why this scheme fits" explanation with citations. Per the
hard rule in solution.md section 3 ("LLM extracts + explains; the
deterministic rules engine decides eligibility"), this service must never
be treated as the eligibility decision-maker upstream -- it only explains
and cites what is in the retrieved context.
"""

import logging
import time
from typing import List, Dict, Any, Optional
import openai
import anthropic
from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# System prompt for Sahayak's RAG explainer.
# Keep this in sync with solution.md section 10 ("What We Must NOT Claim")
# and section 9 (Risks & Mitigations -> LLM hallucination row).
SAHAYAK_SYSTEM_PROMPT = """You are Sahayak, an AI assistant helping marginalized entrepreneurs \
(SC, OBC, ST, DNT, Safai Karamcharis, transgender persons, PwD, and women from marginalized \
communities) understand Indian government business-support schemes. This tool was built for \
Smart India Hackathon problem statement SIH26092, sponsored by the Ministry of Social Justice & \
Empowerment (MoSJE).

Your ONLY job here is to explain government schemes using the retrieved context below -- you are \
the "explainer" step, not the eligibility decision-maker. A separate deterministic rules engine \
(outside this service) is the single source of truth for whether someone is ELIGIBLE, UNCERTAIN, \
or NOT_ELIGIBLE for a scheme.

HARD RULES (never break these):
1. Answer ONLY using the provided context, and cite every factual claim with [chunk_id].
2. If the context doesn't contain the answer, say so plainly and suggest what to ask instead -- \
never guess or invent scheme names, amounts, deadlines, numbers, interest rates, or eligibility \
criteria. Fabricating a "verified on" date, a subsidy %, a loan cap, or an official URL is never \
acceptable.
3. NEVER state or imply that someone "is eligible", "will get the loan/grant", "is approved", or \
"qualifies". You may describe what a scheme offers and its stated criteria, citing the source. The \
eligibility verdict itself always comes from the rules engine, not from you. Use hedging like \
"per the scheme's stated criteria..."/"as described in the document..."
4. NEVER guarantee approval, invent statistics or success rates, invent exact current interest \
rates (say rates are set by each lender/bank and vary), or claim schemes can be freely combined \
("stacked") unless the context explicitly describes the interaction.
5. Reply in the same language the user used (Hindi, English, or Hinglish) -- most users have low \
digital literacy, so keep sentences short and plain, avoid bureaucratic jargon, and explain any \
scheme name, acronym, or document type you mention.

HOW TO DIFFERENTIATE SCHEMES (apply when the question involves choosing between or comparing \
schemes, and the context covers more than one):
6. When several schemes could apply, compare them explicitly so the user can understand the \
trade-offs. For each relevant scheme in context, briefly note: (a) what it is, (b) loan/benefit \
range or cap, (c) who it is aimed at (category / business stage constraints, e.g. greenfield-only, \
non-farm, collateral-free), and (d) key distinguishing condition (e.g. PMEGP is margin-money \
subsidy for NEW micro-enterprises; MUDRA is collateral-free working-capital loans in Shishu/Kishor/\
Tarun tiers; Stand-Up India is a 10 lakh-1 crore loan for a FIRST (greenfield) SC/ST or woman \
enterprise). Use whatever the context actually supports -- do not invent a distinction.
7. When the user gives a business goal (e.g. "I sew clothes, need 2 lakh for machines"), rank only \
the schemes that are actually present in the retrieved context, explain why each fits (or does not \
fit) the goal using the citations, and be honest when context is thin: "The documents I have cover \
X and Y, I can't speak to Z."
8. Be concise but complete -- this is a decision-support tool for someone who needs to act, not a \
policy essay. A good answer often has: a one-line direct response, a short per-scheme comparison \
clearly attributed to sources, and next-step guidance (what to ask, where to check)."""


class ChatService:
    """Service for chat completions supporting multiple AI providers."""

    def __init__(self):
        """Initialize chat clients based on configuration."""
        self.provider = settings.ai_provider

        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_chat_model

        elif self.provider == "groq":
            # Groq exposes an OpenAI-compatible API, so reuse the openai client
            # pointed at Groq's base URL. Fast, and not subject to the hourly
            # usage outages that hit free-tier Gemini.
            self.client = openai.OpenAI(
                api_key=settings.groq_api_key,
                base_url=settings.groq_base_url,
            )
            self.model = settings.groq_chat_model

        elif self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.anthropic_chat_model

        elif self.provider == "gemini":
            # Lazy import so non-Gemini setups don't need google-genai installed.
            from google import genai
            self.client = genai.Client(api_key=settings.gemini_api_key)
            self.model = settings.gemini_chat_model

        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

        logger.info(f"Initialized chat service with {self.provider} ({self.model})")

    async def generate_answer(self, query: str, context_blocks: List[Dict[str, Any]],
                              profile: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate RAG answer using context blocks.

        Args:
            query: User's question
            context_blocks: Retrieved chunks with metadata
            profile: Optional prerequisite answers describing the applicant
        """
        # Build context string with citations
        context_parts = []
        for block in context_blocks:
            chunk_id = block.get('chunk_id', 'unknown')
            text = block.get('text', '')
            context_parts.append(f"[{chunk_id}] {text}")

        context = "\n\n".join(context_parts)

        system_prompt = SAHAYAK_SYSTEM_PROMPT

        # Include the applicant profile so the explanation fits their situation.
        profile_text = "\n".join(
            f"- {k}: {v}" for k, v in (profile or {}).items() if v
        ) if profile else ""
        profile_block = f"Applicant profile:\n{profile_text}\n" if profile_text else ""

        user_prompt = f"""Context:
                        {context}

                        {profile_block}
                        Question: {query}

                        Please provide an answer based on the context above, including appropriate citations."""

        try:
            if self.provider in ("openai", "groq"):
                # Retry transient API errors (429/503) with backoff for both
                # OpenAI and the OpenAI-compatible Groq endpoint.
                last_err = None
                for attempt in range(settings.gemini_max_retries):
                    try:
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=settings.temperature,
                            max_tokens=1000
                        )
                        answer = response.choices[0].message.content
                        break
                    except Exception as retry_err:
                        last_err = retry_err
                        msg = (getattr(retry_err, "message", "") + " " +
                               str(getattr(retry_err, "status_code", ""))).lower()
                        transient = any(k in msg for k in ("429", "503", "unavailable", "rate", "overloaded"))
                        if transient and attempt < settings.gemini_max_retries - 1:
                            wait = (attempt + 1) * settings.gemini_retry_delay
                            logger.warning(f"{self.provider} transient error, retry {attempt+1} in {wait}s: {retry_err}")
                            time.sleep(wait)
                            continue
                        raise retry_err

            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=settings.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                answer = response.content[0].text

            elif self.provider == "gemini":
                from google.genai import types
                last_err = None
                for attempt in range(settings.gemini_max_retries):
                    try:
                        response = self.client.models.generate_content(
                            model=self.model,
                            contents=user_prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=system_prompt,
                                temperature=settings.temperature,
                                max_output_tokens=1000,
                            ),
                        )
                        answer = response.text
                        break
                    except Exception as retry_err:
                        # Transient Gemini 429/503 (high demand) -> backoff + retry.
                        last_err = retry_err
                        msg = (getattr(retry_err, "message", "") + " " + str(getattr(retry_err, "code", ""))).lower()
                        transient = any(k in msg for k in ("503", "429", "unavailable", "high demand", "resource_exhausted", "quota"))
                        if transient and attempt < settings.gemini_max_retries - 1:
                            wait = (attempt + 1) * settings.gemini_retry_delay
                            logger.warning(f"Gemini transient error, retry {attempt+1} in {wait}s: {retry_err}")
                            time.sleep(wait)
                            continue
                        raise retry_err

            logger.info(f"Generated answer using {self.provider}")
            return answer or "I couldn't generate an answer."

        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return f"I encountered an error while processing your question: {str(e)}"


# Global service instance
chat_service = ChatService()
