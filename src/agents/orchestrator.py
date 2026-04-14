"""
Multi-agent orchestrator using LangGraph.

Three agents in sequence:
1. Parser Agent — ingests resume PDF and extracts structured data
2. Matching Agent — uses RAG to find best job matches
3. Interview Agent — generates interview questions for top matches
"""
from __future__ import annotations

import json
import logging
from typing import TypedDict, Optional, List, Dict, Any
from pathlib import Path

from langgraph.graph import StateGraph, END

from config.settings import settings
from src.parser.pdf_extractor import extract_text_from_pdf
from src.parser.llm_parser import parse_resume_with_llm
from src.rag.embeddings import embed_text
from src.rag.retriever import get_top_candidates, match_candidates_to_job
from src.rag.chunker import prepare_candidate_text
from src.agents.interview_agent import generate_interview_questions
from src.agents.text_to_sql import text_to_sql
from src.database.session import SessionLocal
from src.database.models import Candidate, JobRole, Application

logger = logging.getLogger(__name__)


class PipelineState(TypedDict):
    # Input
    pdf_path: Optional[str]
    job_id: Optional[int]
    query: Optional[str]

    # Parser output
    parsed_resume: Optional[Dict]
    candidate_id: Optional[int]

    # Matching output
    matches: List[Dict]

    # Interview output
    interview_questions: List[Dict]

    # Metadata
    errors: List[str]
    stage: str


def parser_node(state: PipelineState) -> PipelineState:
    """Parse resume PDF and store in database."""
    logger.info("Parser Agent: Processing resume...")
    state["stage"] = "parsing"

    pdf_path = state.get("pdf_path")
    if not pdf_path:
        state["errors"].append("No PDF path provided")
        return state

    try:
        raw_text = extract_text_from_pdf(pdf_path)
        if not raw_text.strip():
            state["errors"].append("Empty text extracted from PDF")
            return state

        file_name = Path(pdf_path).stem
        category = Path(pdf_path).parent.name

        resume_data = parse_resume_with_llm(raw_text, file_name, category)
        state["parsed_resume"] = resume_data.model_dump()

        # Store in database
        session = SessionLocal()
        try:
            existing = session.query(Candidate).filter_by(file_name=file_name).first()
            if existing:
                state["candidate_id"] = existing.id
            else:
                candidate = Candidate(
                    file_name=file_name,
                    category=category,
                    name=resume_data.name,
                    email=resume_data.email,
                    phone=resume_data.phone,
                    skills=resume_data.skills,
                    experience=resume_data.experience,
                    education=resume_data.education,
                    summary=resume_data.summary,
                    total_years_experience=resume_data.total_years_experience,
                    raw_text=raw_text,
                )
                # Compute embedding
                candidate_text = prepare_candidate_text(candidate)
                candidate.embedding = embed_text(candidate_text)

                session.add(candidate)
                session.commit()
                state["candidate_id"] = candidate.id

            logger.info(f"Parser Agent: Stored candidate {file_name} (id={state['candidate_id']})")
        finally:
            session.close()

    except Exception as e:
        state["errors"].append(f"Parser error: {str(e)}")
        logger.error(f"Parser Agent error: {e}")

    return state


def matching_node(state: PipelineState) -> PipelineState:
    """Match candidate against job roles using RAG."""
    logger.info("Matching Agent: Computing semantic matches...")
    state["stage"] = "matching"

    job_id = state.get("job_id")

    try:
        if job_id:
            # Match specific candidate against a specific job
            session = SessionLocal()
            try:
                job = session.query(JobRole).get(job_id)
                if not job:
                    state["errors"].append(f"Job role {job_id} not found")
                    return state

                results = match_candidates_to_job(job_id, top_k=10)
                matches = []
                for candidate, score in results:
                    matches.append({
                        "candidate_id": candidate.id,
                        "candidate_name": candidate.name,
                        "category": candidate.category,
                        "match_score": score,
                        "skills": candidate.skills,
                        "total_years_experience": candidate.total_years_experience,
                    })

                state["matches"] = matches
                logger.info(f"Matching Agent: Found {len(matches)} matches for job {job_id}")
            finally:
                session.close()
        elif state.get("query"):
            # Free text matching
            results = get_top_candidates(state["query"], top_k=10)
            matches = []
            for candidate, score in results:
                matches.append({
                    "candidate_id": candidate.id,
                    "candidate_name": candidate.name,
                    "category": candidate.category,
                    "match_score": score,
                    "skills": candidate.skills,
                    "total_years_experience": candidate.total_years_experience,
                })
            state["matches"] = matches
        else:
            state["errors"].append("No job_id or query provided for matching")

    except Exception as e:
        state["errors"].append(f"Matching error: {str(e)}")
        logger.error(f"Matching Agent error: {e}")

    return state


def interview_node(state: PipelineState) -> PipelineState:
    """Generate interview questions for top matched candidates."""
    logger.info("Interview Agent: Generating questions...")
    state["stage"] = "interview"

    matches = state.get("matches", [])
    job_id = state.get("job_id")

    if not matches:
        state["errors"].append("No matches to generate questions for")
        return state

    try:
        session = SessionLocal()
        try:
            job = session.query(JobRole).get(job_id) if job_id else None
            job_data = {
                "title": job.title if job else "General",
                "department": job.department if job else "",
                "description": job.description if job else "",
                "requirements": job.requirements if job else [],
                "min_experience_years": job.min_experience_years if job else 0,
            }

            # Generate questions for top 3 candidates
            top_matches = matches[:3]
            all_questions = []

            for match in top_matches:
                candidate = session.query(Candidate).get(match["candidate_id"])
                if not candidate:
                    continue

                candidate_data = {
                    "name": candidate.name,
                    "category": candidate.category,
                    "skills": candidate.skills,
                    "experience": candidate.experience,
                    "education": candidate.education,
                    "summary": candidate.summary,
                    "total_years_experience": candidate.total_years_experience,
                }

                questions = generate_interview_questions(candidate_data, job_data)
                all_questions.append({
                    "candidate_id": candidate.id,
                    "candidate_name": candidate.name,
                    "match_score": match["match_score"],
                    "questions": questions,
                })

            state["interview_questions"] = all_questions
            logger.info(f"Interview Agent: Generated questions for {len(all_questions)} candidates")
        finally:
            session.close()

    except Exception as e:
        state["errors"].append(f"Interview error: {str(e)}")
        logger.error(f"Interview Agent error: {e}")

    return state


def should_continue_to_matching(state: PipelineState) -> str:
    """Decide whether to proceed to matching after parsing."""
    if state.get("errors"):
        return "end"
    if state.get("job_id") or state.get("query"):
        return "matching"
    return "end"


def should_continue_to_interview(state: PipelineState) -> str:
    """Decide whether to proceed to interview after matching."""
    if state.get("errors"):
        return "end"
    if state.get("matches") and state.get("job_id"):
        return "interview"
    return "end"


def build_pipeline() -> StateGraph:
    """Build the LangGraph multi-agent pipeline."""
    workflow = StateGraph(PipelineState)

    # Add nodes
    workflow.add_node("parser", parser_node)
    workflow.add_node("matching", matching_node)
    workflow.add_node("interview", interview_node)

    # Set entry point
    workflow.set_entry_point("parser")

    # Add conditional edges
    workflow.add_conditional_edges(
        "parser",
        should_continue_to_matching,
        {"matching": "matching", "end": END},
    )
    workflow.add_conditional_edges(
        "matching",
        should_continue_to_interview,
        {"interview": "interview", "end": END},
    )
    workflow.add_edge("interview", END)

    return workflow.compile()


def build_matching_pipeline() -> StateGraph:
    """Build a pipeline that starts from matching (no parsing needed)."""
    workflow = StateGraph(PipelineState)

    workflow.add_node("matching", matching_node)
    workflow.add_node("interview", interview_node)

    workflow.set_entry_point("matching")

    workflow.add_conditional_edges(
        "matching",
        should_continue_to_interview,
        {"interview": "interview", "end": END},
    )
    workflow.add_edge("interview", END)

    return workflow.compile()


# Pre-built pipelines
full_pipeline = build_pipeline()
matching_pipeline = build_matching_pipeline()
