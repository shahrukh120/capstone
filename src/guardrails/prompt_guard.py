"""Prompt injection detection and defense.

Wraps user inputs with delimiters and checks for injection patterns
before they reach the LLM.
"""
from __future__ import annotations

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Known prompt injection patterns ─────────────────────────────────
INJECTION_PATTERNS = [
    # Direct override attempts
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?above\s+instructions",
    r"disregard\s+(all\s+)?previous",
    r"forget\s+(all\s+)?(your\s+)?instructions",
    r"override\s+(all\s+)?instructions",
    r"new\s+instructions?\s*:",
    # Role-play hijacking
    r"you\s+are\s+now\s+(?:a|an|the)\s+",
    r"pretend\s+(?:you\s+are|to\s+be)",
    r"act\s+as\s+(?:a|an|the)\s+",
    r"switch\s+to\s+.*\s*mode",
    # System prompt extraction
    r"(show|reveal|print|output|repeat)\s+(me\s+)?(your|the)\s+(system\s+)?(prompt|instructions)",
    r"what\s+(are|is)\s+your\s+(system\s+)?prompt",
    r"(display|give|tell)\s+(me\s+)?(your|the)\s+(system\s+)?(prompt|instructions)",
    r"system\s+prompt",
    # Data exfiltration
    r"(list|show|dump|export)\s+all\s+(api\s+)?keys",
    r"(show|print|output)\s+(the\s+)?(database\s+)?password",
    r"(reveal|show)\s+(the\s+)?environment\s+variables",
    # SQL injection via prompt
    r";\s*(DROP|DELETE|INSERT|UPDATE|ALTER|TRUNCATE)",
    r"UNION\s+SELECT",
    r"--\s*$",  # SQL comment at end
]

# Compile for performance
_compiled_patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def detect_prompt_injection(text: str) -> tuple[bool, Optional[str]]:
    """Check if text contains prompt injection attempts.

    Returns (is_injection, matched_pattern_description).
    """
    if not text:
        return False, None

    for pattern in _compiled_patterns:
        match = pattern.search(text)
        if match:
            matched = match.group(0)
            logger.warning(f"Prompt injection detected: '{matched}' in input")
            return True, f"Blocked: suspicious pattern detected — '{matched[:50]}'"

    return False, None


def wrap_user_input(user_text: str, input_type: str = "query") -> str:
    """Wrap user input with clear delimiters to prevent injection.

    This creates a clear boundary between system instructions and user data.
    """
    delimiter = "=" * 20
    return (
        f"\n{delimiter} START USER {input_type.upper()} {delimiter}\n"
        f"{user_text}\n"
        f"{delimiter} END USER {input_type.upper()} {delimiter}\n"
    )


def sanitize_for_llm(text: str, max_length: int = 4000) -> str:
    """Sanitize text before sending to LLM.

    Strips control characters, truncates, and adds safety markers.
    """
    if not text:
        return ""

    # Remove null bytes and control characters (keep newlines, tabs)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Truncate
    if len(text) > max_length:
        text = text[:max_length] + "\n[...truncated]"

    return text
