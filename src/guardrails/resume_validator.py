"""Heuristic validator: is this PDF actually a resume?

Runs BEFORE the LLM to reject obvious non-resumes (recipes, contracts,
random documents) — saves LLM tokens and prevents index pollution.

Strategy: score the document against multiple resume-shaped signals.
A real resume almost always has:
  - Contact info (email OR phone)
  - One or more "section headers" (Experience, Education, Skills, etc.)
  - Resume vocabulary (years, company-shaped words, role nouns)
  - Reasonable length (not 3 lines, not a 200-page book)
"""
from __future__ import annotations

import logging
import re
from typing import Tuple, List

logger = logging.getLogger(__name__)

# ── Tunables ────────────────────────────────────────────────────────
MIN_TEXT_LENGTH = 250          # below this it's basically empty
MAX_TEXT_LENGTH = 200_000      # huge PDFs (books, manuals) — reject
MIN_SCORE = 3                  # need at least 3 of the signals below

# ── Resume signal patterns ──────────────────────────────────────────
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
URL_RE   = re.compile(r"(linkedin\.com|github\.com|gitlab\.com|portfolio|behance\.net)", re.I)

SECTION_HEADERS = [
    "experience", "work experience", "professional experience", "employment",
    "education", "academic", "qualification",
    "skills", "technical skills", "core competencies", "expertise",
    "projects", "certifications", "publications", "achievements",
    "summary", "objective", "profile", "about me",
    "languages", "interests", "references",
]
SECTION_RE = re.compile(
    r"(?im)^[\s•▪◦●\-–—]*(" + "|".join(re.escape(h) for h in SECTION_HEADERS) + r")\s*[:\-]?\s*$"
)
# Also count inline mentions (some resumes don't put headers on own line)
SECTION_INLINE_RE = re.compile(
    r"\b(" + "|".join(re.escape(h) for h in SECTION_HEADERS) + r")\b", re.I
)

# Resume vocabulary — verbs/nouns common in CVs
RESUME_VOCAB = [
    r"\b(years?|yrs?)\s+of\s+experience\b",
    r"\b(bachelor|master|phd|b\.?s\.?c?|m\.?s\.?c?|b\.?tech|m\.?tech|mba|degree|university|college|institute)\b",
    r"\b(developed|managed|led|implemented|designed|built|created|architected|delivered|improved|optimized|reduced|increased)\b",
    r"\b(team|project|client|stakeholder|deadline|deliverable|kpi|roi)\b",
    r"\b(intern(ship)?|full[\s-]?time|part[\s-]?time|contract|freelance|remote|hybrid)\b",
    r"\b(present|current(ly)?|jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?|jul(y)?|aug(ust)?|sep(t(ember)?)?|oct(ober)?|nov(ember)?|dec(ember)?)\s*[\-–—]?\s*\d{2,4}\b",
]
VOCAB_REGEXES = [re.compile(p, re.I) for p in RESUME_VOCAB]

# ── Suspicious / non-resume signals ─────────────────────────────────
NON_RESUME_PHRASES = [
    # legal docs
    "this agreement", "hereinafter referred to as", "whereas", "in witness whereof",
    # invoices / receipts
    "invoice number", "tax invoice", "amount due", "subtotal", "purchase order",
    # academic papers
    "abstract\n", "1. introduction", "references\n[1]", "doi:",
    # recipes / random
    "ingredients:", "preheat the oven", "serves 4",
    "table of contents", "chapter 1", "isbn",
    # prompt-injection markers
    "ignore previous instructions", "ignore all prior", "system prompt",
    "you are now", "disregard the above", "forget everything",
]


def looks_like_resume(text: str) -> Tuple[bool, str, dict]:
    """Heuristic check: does this text look like a resume?

    Returns (is_resume, reason, details_dict).
    `details` exposes the score breakdown for logging/debugging.
    """
    if not text or not text.strip():
        return False, "Empty document — no extractable text.", {}

    text_len = len(text)
    if text_len < MIN_TEXT_LENGTH:
        return False, f"Document too short ({text_len} chars) — likely not a resume.", {"length": text_len}

    if text_len > MAX_TEXT_LENGTH:
        return False, f"Document too large ({text_len} chars) — looks like a book or manual, not a resume.", {"length": text_len}

    lower = text.lower()

    # Hard rejects: known non-resume phrases (reject if 2+ hits)
    bad_hits = [p for p in NON_RESUME_PHRASES if p in lower]
    if len(bad_hits) >= 2:
        return False, f"Document looks like a non-resume document (matched: {', '.join(bad_hits[:3])}).", {"non_resume_phrases": bad_hits}

    # Score positive signals
    score = 0
    breakdown: List[str] = []

    has_email = bool(EMAIL_RE.search(text))
    has_phone = bool(PHONE_RE.search(text))
    has_url   = bool(URL_RE.search(text))
    if has_email or has_phone:
        score += 1; breakdown.append("contact_info")
    if has_url:
        score += 1; breakdown.append("professional_url")

    # Section headers (own-line is stronger signal than inline)
    section_lines = SECTION_RE.findall(text)
    section_inline = SECTION_INLINE_RE.findall(text)
    distinct_headers = len({h.lower() for h in section_lines + section_inline})
    if distinct_headers >= 3:
        score += 2; breakdown.append(f"sections({distinct_headers})")
    elif distinct_headers >= 2:
        score += 1; breakdown.append(f"sections({distinct_headers})")

    # Resume vocabulary (verbs, dates, education words)
    vocab_hits = sum(1 for r in VOCAB_REGEXES if r.search(text))
    if vocab_hits >= 4:
        score += 2; breakdown.append(f"vocab({vocab_hits})")
    elif vocab_hits >= 2:
        score += 1; breakdown.append(f"vocab({vocab_hits})")

    details = {
        "length": text_len,
        "score": score,
        "min_score": MIN_SCORE,
        "signals": breakdown,
        "has_email": has_email,
        "has_phone": has_phone,
        "distinct_section_headers": distinct_headers,
        "vocab_hits": vocab_hits,
        "non_resume_phrases_matched": bad_hits,
    }

    if score < MIN_SCORE:
        reason = (
            f"Doesn't look like a resume (score {score}/{MIN_SCORE}). "
            f"Missing typical resume signals: contact info, section headers "
            f"(Experience/Education/Skills), or career vocabulary. "
            f"Found: {', '.join(breakdown) or 'none'}."
        )
        return False, reason, details

    return True, "Looks like a resume.", details
