"""Pydantic schemas for API request/response models."""
from __future__ import annotations

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class CandidateResponse(BaseModel):
    id: int
    file_name: str
    category: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    skills: List[str]
    experience: List[Dict]
    education: List[Dict]
    summary: Optional[str]
    total_years_experience: Optional[float]

    class Config:
        from_attributes = True


class JobRoleResponse(BaseModel):
    id: int
    title: str
    department: Optional[str]
    description: str
    requirements: List[str]
    min_experience_years: float
    location: Optional[str]
    salary_range: Optional[str]
    status: str

    class Config:
        from_attributes = True


class MatchResult(BaseModel):
    candidate_id: int
    candidate_name: Optional[str]
    category: str
    match_score: float
    skills: List[str]
    total_years_experience: Optional[float]


class MatchResponse(BaseModel):
    job_id: int
    job_title: str
    matches: List[MatchResult]


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"


class QueryResponse(BaseModel):
    question: str
    sql: str
    explanation: str
    thought: str = ""
    answer: str = ""
    columns: List[str] = []
    results: List[Dict[str, Any]] = []
    row_count: int = 0
    error: Optional[str] = None
    conversation_turns: int = 0


class InterviewQuestion(BaseModel):
    question: str
    category: str
    rationale: str


class InterviewResponse(BaseModel):
    candidate_id: int
    candidate_name: Optional[str]
    job_id: int
    job_title: str
    match_score: float
    questions: List[InterviewQuestion]


class JobCreateRequest(BaseModel):
    title: str
    department: Optional[str] = None
    description: str
    requirements: List[str] = []
    min_experience_years: float = 0
    location: Optional[str] = None
    salary_range: Optional[str] = None


class UploadResponse(BaseModel):
    candidate_id: int
    file_name: str
    name: Optional[str]
    category: str
    skills: List[str]
    total_years_experience: Optional[float]
    message: str
