"""Interview agent: generates role-specific interview questions for candidates."""
from __future__ import annotations

import json
import logging
from typing import List, Dict

from config.settings import settings
from src.agents.llm_client import llm_chat_json

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert interviewer. Given a candidate's profile and a job description, generate targeted interview questions.

Return ONLY valid JSON with this schema:
{
  "questions": [
    {"question": "The interview question", "category": "technical|behavioral|situational", "rationale": "Why this question matters for this role"}
  ]
}

Generate 8-10 questions total:
- 4-5 technical questions based on the candidate's skills and the job requirements
- 2-3 behavioral questions exploring relevant soft skills
- 2 situational questions to assess problem-solving ability

Tailor questions specifically to the gap/overlap between the candidate's experience and the job requirements.
"""


def generate_interview_questions(
    candidate_data: Dict,
    job_data: Dict,
) -> List[Dict]:
    """Generate interview questions for a candidate-job pair."""
    candidate_summary = (
        f"Name: {candidate_data.get('name', 'Unknown')}\n"
        f"Category: {candidate_data.get('category', 'Unknown')}\n"
        f"Skills: {', '.join(candidate_data.get('skills', []))}\n"
        f"Experience: {candidate_data.get('total_years_experience', 'Unknown')} years\n"
        f"Summary: {candidate_data.get('summary', 'N/A')}\n"
    )
    if candidate_data.get("experience"):
        for exp in candidate_data["experience"][:3]:
            candidate_summary += f"- {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('start', '')} - {exp.get('end', '')})\n"

    job_summary = (
        f"Title: {job_data.get('title', '')}\n"
        f"Department: {job_data.get('department', '')}\n"
        f"Description: {job_data.get('description', '')}\n"
        f"Requirements: {', '.join(job_data.get('requirements', []))}\n"
        f"Min Experience: {job_data.get('min_experience_years', 0)} years\n"
    )

    prompt = f"Candidate Profile:\n{candidate_summary}\n\nJob Description:\n{job_summary}"

    parsed = llm_chat_json(SYSTEM_PROMPT, prompt, temperature=0.3)
    return parsed.get("questions", [])
