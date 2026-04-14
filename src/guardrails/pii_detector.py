"""PII (Personally Identifiable Information) detection and redaction.

Detects emails, phone numbers, SSN, and other PII in text before
logging or displaying.
"""
from __future__ import annotations

import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# ── PII detection patterns ──────────────────────────────────────────
PII_PATTERNS = {
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "phone": re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
    "ssn": re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'),
    "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
    "ip_address": re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
}

# Replacement tokens
REDACTION_MAP = {
    "email": "[EMAIL_REDACTED]",
    "phone": "[PHONE_REDACTED]",
    "ssn": "[SSN_REDACTED]",
    "credit_card": "[CC_REDACTED]",
    "ip_address": "[IP_REDACTED]",
}


def detect_pii(text: str) -> List[Dict[str, str]]:
    """Detect PII in text and return list of findings.

    Returns list of {"type": "email", "value": "...", "position": "123-145"}.
    """
    if not text:
        return []

    findings = []
    for pii_type, pattern in PII_PATTERNS.items():
        for match in pattern.finditer(text):
            findings.append({
                "type": pii_type,
                "value": match.group(),
                "position": f"{match.start()}-{match.end()}",
            })

    return findings


def redact_pii(text: str, types: List[str] = None) -> str:
    """Redact PII from text. If types is None, redact all types."""
    if not text:
        return text

    redacted = text
    for pii_type, pattern in PII_PATTERNS.items():
        if types and pii_type not in types:
            continue
        replacement = REDACTION_MAP.get(pii_type, "[REDACTED]")
        redacted = pattern.sub(replacement, redacted)

    return redacted


def redact_pii_in_dict(data: dict, fields: List[str] = None) -> dict:
    """Redact PII from specific fields in a dictionary.

    If fields is None, redacts all string values.
    """
    redacted = {}
    for key, value in data.items():
        if isinstance(value, str):
            if fields is None or key in fields:
                redacted[key] = redact_pii(value)
            else:
                redacted[key] = value
        elif isinstance(value, dict):
            redacted[key] = redact_pii_in_dict(value, fields)
        elif isinstance(value, list):
            redacted[key] = [
                redact_pii_in_dict(item, fields) if isinstance(item, dict)
                else redact_pii(item) if isinstance(item, str) and (fields is None or key in fields)
                else item
                for item in value
            ]
        else:
            redacted[key] = value
    return redacted
