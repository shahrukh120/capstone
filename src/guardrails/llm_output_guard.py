"""LLM output validation — catches malformed responses, hallucinations, and unsafe content."""
from __future__ import annotations

import json
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ── Toxic / inappropriate content patterns ──────────────────────────
TOXIC_PATTERNS = [
    r'\b(kill|murder|suicide|bomb|terrorist)\b',
    r'\b(racial\s+slur|hate\s+speech)\b',
]
_compiled_toxic = [re.compile(p, re.IGNORECASE) for p in TOXIC_PATTERNS]


def validate_json_response(raw: str, required_keys: list = None) -> tuple[bool, Optional[dict], str]:
    """Validate LLM JSON output.

    Returns (is_valid, parsed_dict_or_None, error_message).
    """
    if not raw or not raw.strip():
        return False, None, "Empty response from LLM"

    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON from LLM: {str(e)[:100]}"

    if not isinstance(parsed, dict):
        return False, None, "LLM response is not a JSON object"

    if required_keys:
        missing = [k for k in required_keys if k not in parsed]
        if missing:
            return False, parsed, f"Missing keys in LLM response: {missing}"

    return True, parsed, ""


def validate_resume_parse(parsed: dict) -> tuple[bool, list]:
    """Validate a parsed resume response for quality.

    Returns (is_acceptable, list_of_warnings).
    """
    warnings = []

    # Check skills extraction quality
    skills = parsed.get("skills", [])
    if not skills:
        warnings.append("No skills extracted")
    elif len(skills) < 2:
        warnings.append(f"Very few skills extracted ({len(skills)})")

    # Check experience
    exp = parsed.get("experience", [])
    if not exp:
        warnings.append("No experience entries extracted")

    # Check for hallucinated years (> 60 years experience is suspicious)
    years = parsed.get("total_years_experience")
    if years is not None and isinstance(years, (int, float)):
        if years > 60:
            warnings.append(f"Suspicious experience value: {years} years")
            parsed["total_years_experience"] = None  # Remove hallucinated value
        elif years < 0:
            warnings.append(f"Negative experience value: {years}")
            parsed["total_years_experience"] = 0

    # Check for hallucinated name patterns
    name = parsed.get("name")
    if name and isinstance(name, str):
        suspicious_names = ["john doe", "jane doe", "test", "example", "n/a", "none", "null", "unknown"]
        if name.lower().strip() in suspicious_names:
            warnings.append(f"Suspicious name detected: '{name}'")
            parsed["name"] = None

    is_acceptable = len(warnings) < 3  # allow up to 2 minor warnings
    return is_acceptable, warnings


def check_toxic_content(text: str) -> tuple[bool, Optional[str]]:
    """Check if LLM output contains toxic/inappropriate content.

    Returns (is_safe, detected_pattern).
    """
    if not text:
        return True, None

    for pattern in _compiled_toxic:
        match = pattern.search(text)
        if match:
            return False, match.group(0)

    return True, None


def validate_interview_questions(questions: list) -> tuple[bool, list]:
    """Validate generated interview questions for quality.

    Returns (is_valid, cleaned_questions).
    """
    if not questions:
        return False, []

    cleaned = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        question_text = q.get("question", "")
        if not question_text or len(question_text) < 10:
            continue  # Skip empty/trivial questions

        # Check for toxic content in questions
        is_safe, _ = check_toxic_content(question_text)
        if not is_safe:
            logger.warning(f"Toxic content filtered from interview question")
            continue

        # Ensure expected structure
        cleaned.append({
            "question": question_text,
            "category": q.get("category", "general"),
            "rationale": q.get("rationale", ""),
        })

    return len(cleaned) > 0, cleaned
