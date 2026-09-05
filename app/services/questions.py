# Copyright 2024
# Directory: yt-rag/app/services/questions.py

"""
Prerequisite (pre-requesting) questions for the Sahayak scheme explainer.

Before the AI recommends a scheme, it should collect a small number of
eligibility-relevant facts about the applicant so retrieval can be narrowed
and the "why this scheme" explanation can address the user's actual profile.

These questions map directly to the fields that matter across the starter
scheme corpus (Stand-Up India, PMEGP, MUDRA, NSFDC): category, business
stage, business type, loan amount needed, and location. The deterministic
rules engine (outside this RAG service) remains the source of truth for
eligibility verdicts; this list only drives the *explainer*.
"""

from typing import Dict, List, Any


# Ordered list of prerequisite questions. Each maps to a profile key.
PREREQUISITE_QUESTIONS: List[Dict[str, Any]] = [
    {
        "key": "category",
        "question": "क्या आप किसी अनुसूचित जाति (SC), अनुसूचित जनजाति (ST), OBC, अल्पसंख्यक, महिला, दिव्यांग, या ट्रांसजेंडर श्रेणी से आते हैं? / Which category do you belong to (SC, ST, OBC, minority, woman, PwD, transgender, or general)?",
        "type": "choice",
        "options": ["SC", "ST", "OBC", "Minority", "Woman", "PwD", "Transgender", "General/Other"],
        "optional": False,
    },
    {
        "key": "business_stage",
        "question": "क्या यह आपका पहला व्यवसाय है या पहले से चल रहे व्यवसाय का विस्तार? / Is this your first business (new enterprise) or an expansion of an existing one?",
        "type": "choice",
        "options": ["New / first venture", "Expanding existing business", "Existing business (not expansion)"],
        "optional": False,
    },
    {
        "key": "business_type",
        "question": "आपका व्यवसाय किस प्रकार का है? / What type of business is it?",
        "type": "choice",
        "options": ["Manufacturing", "Services", "Trading", "Agriculture / agri-allied"],
        "optional": True,
    },
    {
        "key": "loan_amount",
        "question": "आपको लगभग कितने रुपये की ज़रूरत है? / Roughly how much do you need?",
        "type": "choice",
        "options": [
            "Up to 50,000",
            "50,000 to 5 lakh",
            "5 lakh to 10 lakh",
            "10 lakh to 20 lakh",
            "20 lakh to 50 lakh",
            "50 lakh to 1 crore",
            "Above 1 crore",
        ],
        "optional": False,
    },
    {
        "key": "location",
        "question": "आपकी यूनिट कहाँ स्थित है? / Where is your unit located (rural or urban)?",
        "type": "choice",
        "options": ["Rural", "Urban"],
        "optional": True,
    },
]


def build_questions_payload(with_intro: bool = True) -> Dict[str, Any]:
    """Return the prerequisite questions list with metadata for the client/AI."""
    return {
        "version": "1.0",
        "intro": (
            "Aapke liye sahi scheme chunne ke liye mujhe kuch zaroori sawaal poochhne hain. "
            "Ye eligibility fix nahi karte, bas main sahi document se jawab de sakun."
        ),
        "questions": PREREQUISITE_QUESTIONS,
    }


def required_keys() -> List[str]:
    """Names of prerequisite questions that should be answered before recommending."""
    return [q["key"] for q in PREREQUISITE_QUESTIONS if not q.get("optional", False)]
