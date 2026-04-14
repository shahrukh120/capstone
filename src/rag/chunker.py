"""Document chunking for RAG pipeline using LangChain text splitters."""
from __future__ import annotations

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def prepare_candidate_text(candidate) -> str:
    """Build a single text representation of a candidate for embedding."""
    parts = []
    if candidate.summary:
        parts.append(candidate.summary)
    if candidate.skills:
        parts.append("Skills: " + ", ".join(candidate.skills))
    if candidate.experience:
        for exp in candidate.experience:
            title = exp.get("title", "")
            company = exp.get("company", "")
            desc = exp.get("description", "")
            parts.append(f"{title} at {company}. {desc}")
    if candidate.education:
        for edu in candidate.education:
            degree = edu.get("degree", "")
            institution = edu.get("institution", "")
            parts.append(f"{degree} from {institution}")
    return "\n".join(parts) if parts else (candidate.raw_text or "")[:2000]


def prepare_job_text(job_role) -> str:
    """Build a single text representation of a job role for embedding."""
    parts = [job_role.title, job_role.description]
    if job_role.requirements:
        parts.append("Requirements: " + ", ".join(job_role.requirements))
    return "\n".join(parts)
