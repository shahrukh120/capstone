"""Input validation and sanitization for all user-facing inputs."""
from __future__ import annotations

import re
import html
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Length limits ────────────────────────────────────────────────────
MAX_QUERY_LENGTH = 1000         # Natural language query
MAX_DESCRIPTION_LENGTH = 5000   # Job description
MAX_FIELD_LENGTH = 500          # Generic text fields (title, department, etc.)
MAX_UPLOAD_SIZE_MB = 10         # PDF upload size
MAX_CATEGORY_LENGTH = 50


# ── Allowed categories ──────────────────────────────────────────────
VALID_CATEGORIES = {
    "ACCOUNTANT", "ADVOCATE", "AGRICULTURE", "APPAREL", "ARTS",
    "AUTOMOBILE", "AVIATION", "BANKING", "BPO", "BUSINESS-DEVELOPMENT",
    "CHEF", "CONSTRUCTION", "CONSULTANT", "DESIGNER", "DIGITAL-MEDIA",
    "ENGINEERING", "FINANCE", "FITNESS", "HEALTHCARE", "HR",
    "INFORMATION-TECHNOLOGY", "PUBLIC-RELATIONS", "SALES", "TEACHER",
    "GENERAL",
}


def sanitize_text(text: str, max_length: int = MAX_FIELD_LENGTH) -> str:
    """Sanitize user text input — strip, escape HTML, enforce length."""
    if not text:
        return ""
    text = text.strip()
    text = html.escape(text)  # prevent XSS
    if len(text) > max_length:
        text = text[:max_length]
        logger.warning(f"Input truncated to {max_length} chars")
    return text


def validate_query(question: str) -> tuple[bool, str]:
    """Validate a natural language query input.
    Returns (is_valid, error_message).
    """
    if not question or not question.strip():
        return False, "Query cannot be empty"
    if len(question) > MAX_QUERY_LENGTH:
        return False, f"Query too long (max {MAX_QUERY_LENGTH} characters)"
    # Block obvious code injection attempts
    suspicious_patterns = [
        r'<script',       # XSS
        r'javascript:',   # XSS
        r'\x00',          # null bytes
    ]
    for pattern in suspicious_patterns:
        if re.search(pattern, question, re.IGNORECASE):
            return False, "Query contains invalid characters"
    return True, ""


def validate_category(category: str) -> tuple[bool, str]:
    """Validate a job category."""
    cat = category.strip().upper()
    if cat not in VALID_CATEGORIES:
        return False, f"Invalid category '{category}'. Valid: {', '.join(sorted(VALID_CATEGORIES))}"
    return True, ""


def validate_job_description(description: str) -> tuple[bool, str]:
    """Validate job description text."""
    if not description or not description.strip():
        return False, "Description cannot be empty"
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return False, f"Description too long (max {MAX_DESCRIPTION_LENGTH} characters)"
    if len(description.strip()) < 20:
        return False, "Description too short (min 20 characters)"
    return True, ""


def validate_file_size(size_bytes: int) -> tuple[bool, str]:
    """Validate uploaded file size."""
    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        return False, f"File too large (max {MAX_UPLOAD_SIZE_MB}MB)"
    if size_bytes == 0:
        return False, "File is empty"
    return True, ""
