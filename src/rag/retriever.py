"""RAG retriever: semantic matching of candidates to job descriptions via pgvector."""
from __future__ import annotations

import logging
from typing import List, Tuple

from sqlalchemy import text
from src.database.session import SessionLocal
from src.database.models import Candidate, JobRole
from src.rag.embeddings import embed_text, embed_texts
from src.rag.chunker import prepare_candidate_text, prepare_job_text

logger = logging.getLogger(__name__)


def _format_embedding(emb) -> str:
    """Format embedding as pgvector-compatible string '[0.1,0.2,...]'."""
    if isinstance(emb, str):
        return emb
    values = list(emb) if hasattr(emb, '__iter__') else emb
    return "[" + ",".join(str(float(v)) for v in values) + "]"


def compute_and_store_embeddings():
    """Compute embeddings for all candidates and job roles that don't have them yet."""
    session = SessionLocal()
    try:
        # Embed candidates
        candidates = session.query(Candidate).filter(Candidate.embedding.is_(None)).all()
        if candidates:
            logger.info(f"Computing embeddings for {len(candidates)} candidates...")
            texts = [prepare_candidate_text(c) for c in candidates]
            embeddings = embed_texts(texts)
            for candidate, emb in zip(candidates, embeddings):
                candidate.embedding = emb
            session.commit()
            logger.info(f"Stored embeddings for {len(candidates)} candidates")

        # Embed job roles
        jobs = session.query(JobRole).filter(JobRole.embedding.is_(None)).all()
        if jobs:
            logger.info(f"Computing embeddings for {len(jobs)} job roles...")
            texts = [prepare_job_text(j) for j in jobs]
            embeddings = embed_texts(texts)
            for job, emb in zip(jobs, embeddings):
                job.embedding = emb
            session.commit()
            logger.info(f"Stored embeddings for {len(jobs)} job roles")
    finally:
        session.close()


def match_candidates_to_job(job_id: int, top_k: int = 10) -> List[Tuple[Candidate, float]]:
    """Find top-k candidates most semantically similar to a job description."""
    session = SessionLocal()
    try:
        job = session.query(JobRole).get(job_id)
        if not job:
            raise ValueError(f"Job role {job_id} not found")

        if job.embedding is None:
            job_text = prepare_job_text(job)
            job.embedding = embed_text(job_text)
            session.commit()

        emb_str = _format_embedding(job.embedding)

        results = session.execute(
            text("""
                SELECT id, 1 - (embedding <=> CAST(:job_embedding AS vector)) AS similarity
                FROM candidates
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:job_embedding AS vector)
                LIMIT :top_k
            """),
            {"job_embedding": emb_str, "top_k": top_k},
        ).fetchall()

        candidates_with_scores = []
        for row in results:
            candidate = session.query(Candidate).get(row[0])
            candidates_with_scores.append((candidate, round(float(row[1]), 4)))

        return candidates_with_scores
    finally:
        session.close()


def get_top_candidates(query: str, top_k: int = 10) -> List[Tuple[Candidate, float]]:
    """Semantic search: find candidates matching a free-text query."""
    session = SessionLocal()
    try:
        query_embedding = embed_text(query)
        emb_str = _format_embedding(query_embedding)

        results = session.execute(
            text("""
                SELECT id, 1 - (embedding <=> CAST(:query_embedding AS vector)) AS similarity
                FROM candidates
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:query_embedding AS vector)
                LIMIT :top_k
            """),
            {"query_embedding": emb_str, "top_k": top_k},
        ).fetchall()

        candidates_with_scores = []
        for row in results:
            candidate = session.query(Candidate).get(row[0])
            candidates_with_scores.append((candidate, round(float(row[1]), 4)))

        return candidates_with_scores
    finally:
        session.close()
