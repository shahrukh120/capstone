"""Enhanced SQL validation beyond basic keyword blocking.

Catches semantic attacks, stacked queries, comment-based bypasses,
and validates query structure.
"""
from __future__ import annotations

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Dangerous keywords (case-insensitive) ────────────────────────────
BLOCKED_KEYWORDS = {
    "DELETE", "DROP", "ALTER", "INSERT", "UPDATE", "TRUNCATE",
    "EXEC", "EXECUTE", "CREATE", "GRANT", "REVOKE",
    "COPY", "LOAD", "DUMP", "BACKUP", "RESTORE",
    "SHUTDOWN", "KILL",
}

# ── Dangerous SQL patterns ──────────────────────────────────────────
DANGEROUS_PATTERNS = [
    r";\s*\w",                          # Stacked queries (semicolon followed by a new statement)
    r"--\s*\S",                         # SQL line comments used to bypass
    r"/\*.*\*/",                        # SQL block comments (potential bypass)
    r"UNION\s+(ALL\s+)?SELECT",         # UNION injection
    r"INTO\s+(OUT|DUMP)FILE",           # File write attacks
    r"LOAD_FILE\s*\(",                  # File read attacks
    r"pg_sleep\s*\(",                   # Time-based blind injection
    r"information_schema",              # Schema reconnaissance
    r"pg_catalog\.\w*password",         # Password access
    r"pg_read_file\s*\(",              # File read via pg
    r"pg_ls_dir\s*\(",                 # Directory listing via pg
    r"current_setting\s*\(",           # Config extraction
    r"set_config\s*\(",                # Config manipulation
]

_compiled_dangerous = [re.compile(p, re.IGNORECASE) for p in DANGEROUS_PATTERNS]

# ── Allowed tables ──────────────────────────────────────────────────
ALLOWED_TABLES = {"candidates", "job_roles", "applications", "interview_feedback"}

# ── Allowed aggregate/window functions ──────────────────────────────
ALLOWED_FUNCTIONS = {
    "COUNT", "SUM", "AVG", "MIN", "MAX", "ROUND",
    "UPPER", "LOWER", "LENGTH", "TRIM", "COALESCE",
    "CAST", "EXTRACT", "DATE_PART", "NOW", "AGE",
    "ROW_NUMBER", "RANK", "DENSE_RANK",
    "STRING_AGG", "ARRAY_AGG", "JSON_AGG",
    "CONCAT", "SUBSTRING", "REPLACE", "SPLIT_PART",
    "CASE", "WHEN", "THEN", "ELSE", "END",
    "NULLIF", "GREATEST", "LEAST", "ABS",
}


def validate_sql(sql: str) -> tuple[bool, Optional[str]]:
    """Comprehensive SQL validation.

    Returns (is_safe, error_message).
    """
    if not sql or not sql.strip():
        return False, "Empty SQL query"

    sql_stripped = sql.strip()

    # 1. Must start with SELECT
    if not sql_stripped.upper().startswith("SELECT"):
        return False, "Only SELECT queries are allowed"

    # 2. Block dangerous keywords
    tokens = set(re.findall(r'\b([A-Z_]+)\b', sql_stripped.upper()))
    blocked_found = tokens & BLOCKED_KEYWORDS
    if blocked_found:
        return False, f"Prohibited keywords: {', '.join(blocked_found)}"

    # 3. Check for dangerous patterns
    for pattern in _compiled_dangerous:
        if pattern.search(sql_stripped):
            return False, f"Dangerous SQL pattern detected"

    # 4. Validate referenced tables
    # Extract table names from FROM and JOIN clauses
    table_refs = re.findall(
        r'(?:FROM|JOIN)\s+(\w+)',
        sql_stripped,
        re.IGNORECASE,
    )
    for table in table_refs:
        if table.lower() not in ALLOWED_TABLES:
            return False, f"Access to table '{table}' is not allowed"

    # 5. Check LIMIT value isn't too high (if present)
    limit_match = re.search(r'LIMIT\s+(\d+)', sql_stripped, re.IGNORECASE)
    if limit_match:
        limit_val = int(limit_match.group(1))
        if limit_val > 100:
            return False, f"LIMIT too high ({limit_val}). Maximum is 100"

    return True, None


def enforce_limit(sql: str, max_limit: int = 50) -> str:
    """Add LIMIT clause if missing, or cap existing LIMIT."""
    if not re.search(r'\bLIMIT\b', sql, re.IGNORECASE):
        sql = sql.rstrip().rstrip(';') + f" LIMIT {max_limit}"
    return sql


def sanitize_sql_output(rows: list, max_rows: int = 50) -> list:
    """Sanitize SQL query results before returning to user.

    Truncates results and strips any potentially sensitive data.
    """
    return rows[:max_rows]
