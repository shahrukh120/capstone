"""ReAct Text-to-SQL agent: multi-turn conversational database queries.

Flow (ReAct pattern):
  1. User asks a natural language question
  2. LLM REASONS about what SQL to run (Thought)
  3. LLM ACTS by generating a SQL query (Action: run_sql)
  4. System executes SQL and returns rows (Observation)
  5. LLM reads the rows and produces a natural language answer
  6. Conversation history is preserved for follow-up questions
"""
from __future__ import annotations

import json
import logging
import re
from typing import Optional, List, Dict, Any

from sqlalchemy import text

from config.settings import settings
from src.database.session import SessionLocal
from src.agents.llm_client import llm_chat
from src.guardrails.sql_guard import validate_sql, sanitize_sql_output, enforce_limit
from src.guardrails.prompt_guard import wrap_user_input, sanitize_for_llm

logger = logging.getLogger(__name__)

SCHEMA_DESCRIPTION = """
PostgreSQL ATS database schema:

TABLE candidates (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(100) UNIQUE NOT NULL,  -- resume file identifier
    category VARCHAR(100) NOT NULL,          -- job category (e.g. ACCOUNTANT, ENGINEERING, HEALTHCARE)
    name VARCHAR(200),                       -- candidate full name
    email VARCHAR(200),
    phone VARCHAR(50),
    skills JSON,                             -- array of skill strings, e.g. ["Python", "SQL", "Excel"]
    experience JSON,                         -- array of {title, company, start, end, description}
    education JSON,                          -- array of {degree, institution, year}
    summary TEXT,                            -- professional summary
    total_years_experience FLOAT,            -- estimated years of experience
    created_at TIMESTAMP
);

TABLE job_roles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,             -- e.g. "Senior Software Engineer"
    department VARCHAR(100),                 -- e.g. "Engineering"
    description TEXT NOT NULL,
    requirements JSON,                       -- array of requirement strings
    min_experience_years FLOAT DEFAULT 0,
    location VARCHAR(200),
    salary_range VARCHAR(100),
    status VARCHAR(20) DEFAULT 'open',       -- open, closed, paused
    created_at TIMESTAMP
);

TABLE applications (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id),
    job_role_id INTEGER REFERENCES job_roles(id),
    match_score FLOAT,                       -- semantic similarity score 0-1
    status VARCHAR(30) DEFAULT 'applied',    -- applied, screening, interview, offered, rejected, hired
    applied_at TIMESTAMP,
    notes TEXT
);

TABLE interview_feedback (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id),
    job_role_id INTEGER REFERENCES job_roles(id),
    questions JSON,                          -- array of interview question strings
    interviewer_notes TEXT,
    rating FLOAT,                            -- 1-5 scale
    created_at TIMESTAMP
);

Categories: ACCOUNTANT, ADVOCATE, AGRICULTURE, APPAREL, ARTS, AUTOMOBILE, AVIATION, BANKING, BPO, BUSINESS-DEVELOPMENT, CHEF, CONSTRUCTION, CONSULTANT, DESIGNER, DIGITAL-MEDIA, ENGINEERING, FINANCE, FITNESS, HEALTHCARE, HR, INFORMATION-TECHNOLOGY, PUBLIC-RELATIONS, SALES, TEACHER

Notes:
- skills is a JSON array, query with skills::text ILIKE '%keyword%'
- Use ILIKE for case-insensitive matching
"""

# ── Step 1: Generate SQL ─────────────────────────────────────────────

SQL_SYSTEM_PROMPT = f"""You are a ReAct Text-to-SQL agent for an Applicant Tracking System.

{SCHEMA_DESCRIPTION}

Given the user's question (and any prior conversation context), generate a SQL query.

Rules:
1. Return ONLY a JSON object with "thought", "sql", and "explanation" keys.
2. "thought" = your brief reasoning about what data to fetch.
3. "sql" = a valid PostgreSQL SELECT query. Only SELECT is allowed.
4. "explanation" = one-line description of what the SQL does.
5. Use ILIKE for text searches. For JSON arrays: skills::text ILIKE '%keyword%'
6. Always LIMIT results to 50 unless user specifies otherwise.
7. Never use DELETE, DROP, ALTER, INSERT, UPDATE, TRUNCATE.
8. If the user asks a follow-up question, use the conversation context to understand what they mean.

Example output:
{{"thought": "The user wants top engineers, so I should query candidates in ENGINEERING category sorted by experience.", "sql": "SELECT name, category, total_years_experience FROM candidates WHERE category = 'ENGINEERING' ORDER BY total_years_experience DESC LIMIT 3", "explanation": "Top 3 engineering candidates by experience"}}
"""

# ── Step 2: Summarize results in natural language ────────────────────

SUMMARIZE_SYSTEM_PROMPT = """You are a helpful ATS database assistant. The user asked a question, a SQL query was run, and here are the database results.

Your job: Read the results and give a clear, conversational natural language answer. Be specific — mention names, numbers, categories. Keep it concise (2-4 sentences). If the results are empty, say so helpfully.

Do NOT return JSON. Just reply in plain English as if speaking to a recruiter."""


# ── Conversation memory (per-session, in-memory) ────────────────────

class ConversationMemory:
    """Stores conversation turns for multi-turn context."""

    def __init__(self, max_turns: int = 10):
        self.turns: List[Dict[str, str]] = []
        self.max_turns = max_turns

    def add_turn(self, question: str, sql: str, answer: str):
        self.turns.append({
            "question": question,
            "sql": sql,
            "answer": answer,
        })
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def get_context(self) -> str:
        if not self.turns:
            return ""
        lines = ["Previous conversation:"]
        for t in self.turns[-5:]:  # last 5 turns for context
            lines.append(f"  User: {t['question']}")
            lines.append(f"  SQL: {t['sql']}")
            lines.append(f"  Answer: {t['answer']}")
        return "\n".join(lines)

    def clear(self):
        self.turns = []


# Global conversation store keyed by session_id
_conversations: Dict[str, ConversationMemory] = {}


def get_conversation(session_id: str = "default") -> ConversationMemory:
    if session_id not in _conversations:
        _conversations[session_id] = ConversationMemory()
    return _conversations[session_id]


def clear_conversation(session_id: str = "default"):
    if session_id in _conversations:
        _conversations[session_id].clear()


# ── Safety checks (delegated to guardrails.sql_guard) ────────────────


# ── Main ReAct function ──────────────────────────────────────────────

def text_to_sql(question: str, session_id: str = "default") -> Dict[str, Any]:
    """ReAct agent: Question → SQL → Execute → Natural language answer.

    Returns dict with: question, sql, explanation, columns, results,
                       row_count, answer, thought, error, conversation_turns
    """
    memory = get_conversation(session_id)
    context = memory.get_context()

    # ── STEP 1: Reasoning + SQL generation ───────────────────────────
    # Guardrail: wrap user input with delimiters to prevent injection
    safe_question = sanitize_for_llm(question, max_length=1000)
    user_prompt = wrap_user_input(safe_question, input_type="question")
    if context:
        user_prompt = f"{context}\n\n{user_prompt}"

    try:
        raw = llm_chat(SQL_SYSTEM_PROMPT, user_prompt, json_mode=True)
        parsed = json.loads(raw)
    except Exception as e:
        return {
            "question": question,
            "sql": "",
            "explanation": "",
            "thought": "",
            "answer": f"Sorry, I couldn't understand that question. Error: {str(e)}",
            "error": f"LLM error: {str(e)}",
            "columns": [],
            "results": [],
            "row_count": 0,
            "conversation_turns": len(memory.turns),
        }

    sql = parsed.get("sql", "")
    explanation = parsed.get("explanation", "")
    thought = parsed.get("thought", "")

    # Guardrail: enforce LIMIT on all queries
    sql = enforce_limit(sql, max_limit=50)

    # ── STEP 2: Validate SQL (enhanced guardrail) ─────────────────────
    is_safe, error = validate_sql(sql)
    if not is_safe:
        return {
            "question": question,
            "sql": sql,
            "explanation": explanation,
            "thought": thought,
            "answer": f"I generated a query but it was blocked for safety: {error}",
            "error": error,
            "columns": [],
            "results": [],
            "row_count": 0,
            "conversation_turns": len(memory.turns),
        }

    # ── STEP 3: Execute SQL (Action: run_sql) ────────────────────────
    session = SessionLocal()
    try:
        result = session.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        rows = sanitize_sql_output(rows, max_rows=50)  # Guardrail: cap results
    except Exception as e:
        return {
            "question": question,
            "sql": sql,
            "explanation": explanation,
            "thought": thought,
            "answer": f"The SQL query had an error: {str(e)}. Try rephrasing your question.",
            "error": str(e),
            "columns": [],
            "results": [],
            "row_count": 0,
            "conversation_turns": len(memory.turns),
        }
    finally:
        session.close()

    # ── STEP 4: Summarize results in natural language ────────────────
    # Truncate results for the LLM (send at most 20 rows)
    rows_for_llm = rows[:20]
    results_text = json.dumps(rows_for_llm, indent=2, default=str)

    summarize_prompt = (
        f"User question: {question}\n\n"
        f"SQL executed: {sql}\n\n"
        f"Results ({len(rows)} row{'s' if len(rows) != 1 else ''}):\n{results_text}"
    )

    try:
        answer = llm_chat(SUMMARIZE_SYSTEM_PROMPT, summarize_prompt, json_mode=False)
    except Exception as e:
        logger.warning(f"Summarization failed: {e}")
        answer = f"Query returned {len(rows)} result{'s' if len(rows) != 1 else ''}."

    # ── STEP 5: Store in conversation memory ─────────────────────────
    memory.add_turn(question, sql, answer)

    return {
        "question": question,
        "sql": sql,
        "explanation": explanation,
        "thought": thought,
        "answer": answer,
        "columns": columns,
        "results": rows,
        "row_count": len(rows),
        "error": None,
        "conversation_turns": len(memory.turns),
    }
