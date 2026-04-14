from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Index
)
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    name = Column(String(200))
    email = Column(String(200))
    phone = Column(String(50))
    skills = Column(JSON, default=list)
    experience = Column(JSON, default=list)
    education = Column(JSON, default=list)
    summary = Column(Text)
    total_years_experience = Column(Float)
    raw_text = Column(Text)
    # 384-dim embedding from all-MiniLM-L6-v2
    embedding = Column(Vector(384))
    created_at = Column(DateTime, default=datetime.utcnow)

    applications = relationship("Application", back_populates="candidate")
    interview_feedbacks = relationship("InterviewFeedback", back_populates="candidate")


class JobRole(Base):
    __tablename__ = "job_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    department = Column(String(100))
    description = Column(Text, nullable=False)
    requirements = Column(JSON, default=list)
    min_experience_years = Column(Float, default=0)
    location = Column(String(200))
    salary_range = Column(String(100))
    status = Column(String(20), default="open", index=True)
    # 384-dim embedding of the job description
    embedding = Column(Vector(384))
    created_at = Column(DateTime, default=datetime.utcnow)

    applications = relationship("Application", back_populates="job_role")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_role_id = Column(Integer, ForeignKey("job_roles.id"), nullable=False)
    match_score = Column(Float)
    status = Column(String(30), default="applied", index=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

    candidate = relationship("Candidate", back_populates="applications")
    job_role = relationship("JobRole", back_populates="applications")


class InterviewFeedback(Base):
    __tablename__ = "interview_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_role_id = Column(Integer, ForeignKey("job_roles.id"), nullable=False)
    questions = Column(JSON, default=list)
    interviewer_notes = Column(Text)
    rating = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="interview_feedbacks")
