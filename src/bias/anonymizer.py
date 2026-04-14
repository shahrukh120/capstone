"""
Anonymizer: strips identifying attributes from candidate data before scoring.

Removes name, email, phone, and gender-coded language to reduce bias.
"""
from __future__ import annotations

import re
from typing import Dict, Any


# Words that may introduce gender bias
GENDER_CODED_WORDS = {
    # Masculine-coded
    "aggressive", "ambitious", "analytical", "assertive", "autonomous",
    "boast", "challenge", "champion", "compete", "competitive", "confident",
    "courageous", "decisive", "determined", "dominant", "driven", "fearless",
    "fight", "force", "greedy", "headstrong", "hierarchy", "hostile",
    "impulsive", "independent", "individual", "lead", "logic", "ninja",
    "objective", "opinion", "outspoken", "persist", "principle", "reckless",
    "rockstar", "self-reliant", "stubborn", "superior", "warrior",
    # Feminine-coded
    "agree", "affectionate", "caring", "cheerful", "collaborate",
    "committed", "communal", "compassionate", "connected", "considerate",
    "cooperative", "dependable", "emotional", "empathy", "enthusiastic",
    "feeling", "gentle", "honest", "interpersonal", "kind", "loyal",
    "modesty", "nag", "nurture", "pleasant", "polite", "quiet",
    "responsive", "submissive", "support", "sympathetic", "tender",
    "together", "trust", "understanding", "warm", "yield",
}

# Common gendered titles/honorifics
HONORIFICS = re.compile(
    r'\b(Mr|Mrs|Ms|Miss|Dr|Prof|Sir|Madam|Mme|Herr|Frau)\b\.?\s*',
    re.IGNORECASE,
)


def anonymize_candidate(candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a copy of candidate data with identifying information removed.

    Strips: name, email, phone, gender-coded language signals.
    Keeps: skills, experience titles, education degrees, years of experience.
    """
    anon = candidate_data.copy()

    # Remove PII
    anon["name"] = None
    anon["email"] = None
    anon["phone"] = None

    # Clean summary of gender-coded words and honorifics
    if anon.get("summary"):
        anon["summary"] = _neutralize_text(anon["summary"])

    # Clean experience descriptions
    if anon.get("experience"):
        cleaned_exp = []
        for exp in anon["experience"]:
            exp_copy = exp.copy()
            if exp_copy.get("description"):
                exp_copy["description"] = _neutralize_text(exp_copy["description"])
            # Remove company name (could reveal demographics)
            exp_copy.pop("company", None)
            cleaned_exp.append(exp_copy)
        anon["experience"] = cleaned_exp

    # Remove raw_text entirely
    anon.pop("raw_text", None)

    return anon


def _neutralize_text(text: str) -> str:
    """Remove gender-coded words and honorifics from text."""
    text = HONORIFICS.sub("", text)
    words = text.split()
    neutralized = [w for w in words if w.lower().strip(".,;:!?") not in GENDER_CODED_WORDS]
    return " ".join(neutralized)
