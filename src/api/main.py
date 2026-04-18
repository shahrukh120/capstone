"""FastAPI application for the AI-powered ATS."""
from __future__ import annotations

import logging
import os
import tempfile
from typing import Optional

from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from config.settings import settings
from src.database.models import Base, Candidate, JobRole, Application
from src.database.session import engine, SessionLocal
from src.api.schemas import (
    CandidateResponse, JobRoleResponse, MatchResponse, MatchResult,
    QueryRequest, QueryResponse, InterviewResponse, InterviewQuestion,
    UploadResponse, JobCreateRequest,
    PipelineResponse, PipelineColumn, PipelineCard,
    StageUpdateRequest, ApplicationCreateRequest,
)
from src.parser.pdf_extractor import extract_text_from_pdf
from src.parser.llm_parser import parse_resume_with_llm
from src.rag.embeddings import embed_text
from src.rag.retriever import match_candidates_to_job, get_top_candidates
from src.rag.chunker import prepare_candidate_text
from src.agents.text_to_sql import text_to_sql, clear_conversation
from src.agents.interview_agent import generate_interview_questions
from src.bias.anonymizer import anonymize_candidate
from src.bias.fairness import run_fairness_audit
from src.bias.explainability import explain_match_score

# ── Guardrails ──────────────────────────────────────────────────────
from src.guardrails.input_validator import (
    sanitize_text, validate_query, validate_category,
    validate_job_description, validate_file_size,
    MAX_QUERY_LENGTH, MAX_FIELD_LENGTH,
)
from src.guardrails.prompt_guard import detect_prompt_injection
from src.guardrails.rate_limiter import api_limiter, llm_limiter, upload_limiter
from src.guardrails.pii_detector import redact_pii

os.environ["TOKENIZERS_PARALLELISM"] = "false"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI-Powered ATS",
    description="Applicant Tracking System with RAG, Text-to-SQL, and Multi-Agent Orchestration",
    version="1.0.0",
)

# ── CORS — restrict in production ───────────────────────────────────
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ── Rate Limiting Middleware ────────────────────────────────────────
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting based on client IP and endpoint type."""
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path

    # Skip rate limiting for static files, health, and admin/seed endpoints
    if path.startswith("/static") or path == "/health" or path == "/" or path.startswith("/seed"):
        return await call_next(request)

    # Choose limiter based on endpoint
    if path == "/upload":
        limiter = upload_limiter
    elif path in ("/query", "/interview") or path.startswith("/interview/"):
        limiter = llm_limiter
    else:
        limiter = api_limiter

    allowed, info = limiter.is_allowed(client_ip)
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Please slow down.",
                "requests_in_window": info["requests_in_window"],
                "limit": info["limit"],
            },
            headers={"Retry-After": "10"},
        )

    response = await call_next(request)
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    return response

# Static files and templates
BASE_DIR = Path(__file__).resolve().parent.parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# ── Database initialization on startup (not at import time) ────────
@app.on_event("startup")
async def init_database():
    """Create tables + pgvector extension + seed job roles on first startup."""
    try:
        from sqlalchemy import text as sa_text
        with engine.connect() as conn:
            conn.execute(sa_text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully")

        # Auto-seed job roles (hardcoded, no files needed)
        from scripts.seed_database import SYNTHETIC_JOBS
        session = SessionLocal()
        try:
            existing = session.query(JobRole).count()
            if existing == 0:
                for job_data in SYNTHETIC_JOBS:
                    session.add(JobRole(**job_data))
                session.commit()
                logger.info(f"Seeded {len(SYNTHETIC_JOBS)} job roles")
            else:
                logger.info(f"Job roles already exist ({existing}), skipping seed")
        finally:
            session.close()
    except Exception as e:
        logger.warning(f"Database init deferred (will retry on first request): {e}")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    """Serve the frontend."""
    return templates.TemplateResponse("index.html", {"request": request})


# ─── Bulk Seed Endpoint (for populating Azure DB from local data) ──

@app.post("/seed/candidates", tags=["Admin"])
async def seed_candidates_bulk(request: Request):
    """Bulk insert candidates from JSON array.

    POST body: [{"file_name": "...", "category": "...", "name": "...", ...}, ...]
    Used to populate Azure DB from locally parsed resumes.
    """
    data = await request.json()
    if not isinstance(data, list):
        raise HTTPException(status_code=400, detail="Expected JSON array of candidate objects")

    session = SessionLocal()
    inserted = 0
    skipped = 0
    try:
        for item in data:
            existing = session.query(Candidate).filter_by(
                file_name=item.get("file_name", "")
            ).first()
            if existing:
                skipped += 1
                continue

            candidate = Candidate(
                file_name=item.get("file_name", "unknown"),
                category=item.get("category", "GENERAL"),
                name=item.get("name"),
                email=item.get("email"),
                phone=item.get("phone"),
                skills=item.get("skills", []),
                experience=item.get("experience", []),
                education=item.get("education", []),
                summary=item.get("summary"),
                total_years_experience=item.get("total_years_experience"),
                raw_text=item.get("raw_text", ""),
            )
            session.add(candidate)
            inserted += 1

            if inserted % 100 == 0:
                session.commit()

        session.commit()
    finally:
        session.close()

    return {"inserted": inserted, "skipped": skipped, "total_in_batch": len(data)}


@app.post("/seed/embeddings", tags=["Admin"])
async def seed_embeddings():
    """Compute embeddings for all candidates that don't have one yet."""
    session = SessionLocal()
    try:
        from sqlalchemy import text as sa_text
        rows = session.execute(
            sa_text("SELECT id, name, category, skills, summary, raw_text FROM candidates WHERE embedding IS NULL LIMIT 200")
        ).fetchall()

        if not rows:
            return {"message": "All candidates already have embeddings", "computed": 0}

        computed = 0
        for row in rows:
            # Build text for embedding
            parts = []
            if row.name:
                parts.append(row.name)
            if row.category:
                parts.append(f"Category: {row.category}")
            if row.skills:
                skills = row.skills if isinstance(row.skills, list) else []
                parts.append(f"Skills: {', '.join(skills[:20])}")
            if row.summary:
                parts.append(row.summary[:500])
            elif row.raw_text:
                parts.append(row.raw_text[:500])

            text = " | ".join(parts) if parts else "unknown candidate"
            embedding = embed_text(text)

            session.execute(
                sa_text("UPDATE candidates SET embedding = :emb WHERE id = :id"),
                {"emb": str(embedding), "id": row.id},
            )
            computed += 1

            if computed % 50 == 0:
                session.commit()
                logger.info(f"  Computed {computed}/{len(rows)} embeddings...")

        session.commit()
        return {"message": f"Computed {computed} embeddings", "computed": computed, "remaining": max(0, len(rows) - computed)}
    finally:
        session.close()


# ─── Upload Endpoint ────────────────────────────────────────────────

@app.post("/upload", response_model=UploadResponse, tags=["Resume"])
async def upload_resume(
    file: UploadFile = File(...),
    category: str = Query(default="GENERAL", description="Job category for the resume"),
):
    """Upload a resume PDF, parse with LLM, and store in database."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Guardrail: validate category
    valid, err = validate_category(category)
    if not valid:
        raise HTTPException(status_code=400, detail=err)

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        content = await file.read()
        # Guardrail: validate file size
        valid, err = validate_file_size(len(content))
        if not valid:
            raise HTTPException(status_code=400, detail=err)
        tmp.write(content)
        tmp_path = tmp.name

    try:
        raw_text = extract_text_from_pdf(tmp_path)
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        file_name = file.filename.replace(".pdf", "")

        try:
            resume_data = parse_resume_with_llm(raw_text, file_name, category)
        except Exception as e:
            logger.error(f"LLM parse failed: {e}")
            raise HTTPException(status_code=503, detail=f"LLM service error: {str(e)}")

        # Build embedding text from parsed data
        embed_text_input = (resume_data.summary or "") + " Skills: " + ", ".join(resume_data.skills)
        resume_embedding = embed_text(embed_text_input)

        session = SessionLocal()
        try:
            existing = session.query(Candidate).filter_by(file_name=file_name).first()
            if existing:
                raise HTTPException(status_code=409, detail=f"Resume '{file_name}' already exists")

            candidate = Candidate(
                file_name=file_name,
                category=category,
                name=resume_data.name if resume_data.name != "null" else None,
                email=resume_data.email,
                phone=resume_data.phone,
                skills=resume_data.skills,
                experience=resume_data.experience,
                education=resume_data.education,
                summary=resume_data.summary,
                total_years_experience=resume_data.total_years_experience,
                raw_text=raw_text,
                embedding=resume_embedding,
            )
            session.add(candidate)
            session.commit()
            session.refresh(candidate)

            return UploadResponse(
                candidate_id=candidate.id,
                file_name=candidate.file_name,
                name=candidate.name,
                category=candidate.category,
                skills=candidate.skills,
                total_years_experience=candidate.total_years_experience,
                message="Resume parsed and stored successfully",
            )
        finally:
            session.close()
    finally:
        os.unlink(tmp_path)


# ─── Matching Endpoint ──────────────────────────────────────────────

@app.get("/match/{job_id}", response_model=MatchResponse, tags=["Matching"])
def match_candidates(
    job_id: int,
    top_k: int = Query(default=10, ge=1, le=50, description="Number of top candidates"),
):
    """Find top candidates matching a job description using RAG semantic search."""
    session = SessionLocal()
    try:
        job = session.query(JobRole).get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job role {job_id} not found")

        results = match_candidates_to_job(job_id, top_k=top_k)

        matches = [
            MatchResult(
                candidate_id=c.id,
                candidate_name=c.name,
                category=c.category,
                match_score=score,
                skills=c.skills or [],
                total_years_experience=c.total_years_experience,
            )
            for c, score in results
        ]

        return MatchResponse(job_id=job_id, job_title=job.title, matches=matches)
    finally:
        session.close()


# ─── Text-to-SQL Query Endpoint ────────────────────────────────────

@app.post("/query", response_model=QueryResponse, tags=["Query"])
def query_ats(request: QueryRequest):
    """ReAct agent: natural language → SQL → execute → conversational answer."""
    # Guardrail: validate query input
    valid, err = validate_query(request.question)
    if not valid:
        raise HTTPException(status_code=400, detail=err)

    # Guardrail: prompt injection detection
    is_injection, reason = detect_prompt_injection(request.question)
    if is_injection:
        raise HTTPException(status_code=400, detail=reason)

    question = sanitize_text(request.question, max_length=MAX_QUERY_LENGTH)
    result = text_to_sql(question, session_id=request.session_id or "default")
    return QueryResponse(**result)


@app.post("/query/clear", tags=["Query"])
def clear_query_conversation(session_id: str = Query(default="default")):
    """Clear conversation history for a session."""
    clear_conversation(session_id)
    return {"message": "Conversation cleared", "session_id": session_id}


# ─── Interview Questions Endpoint ──────────────────────────────────

@app.get("/interview/{candidate_id}", response_model=InterviewResponse, tags=["Interview"])
def generate_interview(
    candidate_id: int,
    job_id: int = Query(..., description="Job role ID to generate questions for"),
):
    """Generate role-specific interview questions for a candidate."""
    session = SessionLocal()
    try:
        candidate = session.query(Candidate).get(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

        job = session.query(JobRole).get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job role {job_id} not found")

        candidate_data = {
            "name": candidate.name,
            "category": candidate.category,
            "skills": candidate.skills,
            "experience": candidate.experience,
            "education": candidate.education,
            "summary": candidate.summary,
            "total_years_experience": candidate.total_years_experience,
        }
        job_data = {
            "title": job.title,
            "department": job.department,
            "description": job.description,
            "requirements": job.requirements,
            "min_experience_years": job.min_experience_years,
        }

        try:
            questions = generate_interview_questions(candidate_data, job_data)
        except Exception as e:
            logger.error(f"Interview generation failed: {e}")
            raise HTTPException(status_code=503, detail=f"LLM service error: {str(e)}")

        return InterviewResponse(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            job_id=job.id,
            job_title=job.title,
            match_score=0.0,
            questions=[InterviewQuestion(**q) for q in questions],
        )
    finally:
        session.close()


# ─── Dashboard Stats ──────────────────────────────────────────────

@app.get("/dashboard/stats", tags=["System"])
def dashboard_stats():
    """Return aggregate stats for the dashboard (category counts, totals)."""
    from sqlalchemy import func
    session = SessionLocal()
    try:
        candidate_count = session.query(Candidate).count()
        job_count = session.query(JobRole).count()

        # Category breakdown — counts directly from DB
        rows = (
            session.query(Candidate.category, func.count(Candidate.id))
            .group_by(Candidate.category)
            .order_by(func.count(Candidate.id).desc())
            .all()
        )
        category_counts = {cat: count for cat, count in rows}

        return {
            "candidates": candidate_count,
            "job_roles": job_count,
            "category_counts": category_counts,
        }
    finally:
        session.close()


# ─── Utility Endpoints ─────────────────────────────────────────────

@app.get("/candidates", response_model=list, tags=["Candidates"])
def list_candidates(
    category: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """List candidates with optional category filter."""
    session = SessionLocal()
    try:
        q = session.query(Candidate)
        if category:
            q = q.filter(Candidate.category == category.upper())
        candidates = q.offset(offset).limit(limit).all()
        return [
            CandidateResponse.model_validate(c).model_dump()
            for c in candidates
        ]
    finally:
        session.close()


@app.get("/jobs", response_model=list, tags=["Jobs"])
def list_jobs():
    """List all job roles."""
    session = SessionLocal()
    try:
        jobs = session.query(JobRole).all()
        return [JobRoleResponse.model_validate(j).model_dump() for j in jobs]
    finally:
        session.close()


@app.post("/jobs", response_model=dict, tags=["Jobs"])
def create_job(job: JobCreateRequest):
    """Create a new job role with auto-computed embedding."""
    # Guardrails: validate inputs
    valid, err = validate_job_description(job.description)
    if not valid:
        raise HTTPException(status_code=400, detail=err)
    job.title = sanitize_text(job.title, max_length=200)
    job.department = sanitize_text(job.department, max_length=100) if job.department else None
    job.description = sanitize_text(job.description, max_length=5000)

    # Guardrail: prompt injection check on description
    is_injection, reason = detect_prompt_injection(job.description)
    if is_injection:
        raise HTTPException(status_code=400, detail=f"Job description blocked: {reason}")

    session = SessionLocal()
    try:
        # Build embedding from description + requirements
        embed_input = job.description + " Requirements: " + ", ".join(job.requirements)
        job_embedding = embed_text(embed_input)

        new_job = JobRole(
            title=job.title,
            department=job.department,
            description=job.description,
            requirements=job.requirements,
            min_experience_years=job.min_experience_years,
            location=job.location,
            salary_range=job.salary_range,
            status="open",
            embedding=job_embedding,
        )
        session.add(new_job)
        session.commit()
        session.refresh(new_job)

        return {
            "id": new_job.id,
            "title": new_job.title,
            "department": new_job.department,
            "message": f"Job '{new_job.title}' created successfully",
        }
    finally:
        session.close()


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint."""
    session = SessionLocal()
    try:
        candidate_count = session.query(Candidate).count()
        job_count = session.query(JobRole).count()
        return {
            "status": "healthy",
            "candidates": candidate_count,
            "job_roles": job_count,
            "llm_provider": settings.llm_provider,
            "llm_model": (
                settings.llm_model if settings.llm_provider == "groq"
                else settings.nvidia_model if settings.llm_provider == "nvidia"
                else settings.ollama_model
            ),
            "guardrails": {
                "rate_limiting": True,
                "prompt_injection_detection": True,
                "input_validation": True,
                "sql_guard": True,
                "pii_detection": True,
                "llm_output_validation": True,
            },
        }
    finally:
        session.close()


@app.get("/llm/status", tags=["System"])
def llm_status():
    """Get current LLM provider status."""
    provider = settings.llm_provider
    if provider == "groq":
        model = settings.llm_model
    elif provider == "nvidia":
        model = settings.nvidia_model
    else:
        model = settings.ollama_model

    # Check if provider is reachable
    available = False
    if provider == "ollama":
        try:
            import requests as req
            r = req.get(f"{settings.ollama_base_url}/api/tags", timeout=3)
            available = r.status_code == 200
        except Exception:
            available = False
    elif provider == "groq":
        available = settings.groq_api_key != "your_groq_api_key_here"
    elif provider == "nvidia":
        available = settings.nvidia_api_key != "your_nvidia_api_key_here"

    return {
        "provider": provider,
        "model": model,
        "available": available,
        "providers": {
            "ollama": {"model": settings.ollama_model, "configured": True},
            "groq": {"model": settings.llm_model, "configured": settings.groq_api_key != "your_groq_api_key_here"},
            "nvidia": {"model": settings.nvidia_model, "configured": settings.nvidia_api_key != "your_nvidia_api_key_here"},
        },
    }


@app.post("/llm/switch", tags=["System"])
def switch_llm(provider: str = Query(..., description="'groq', 'ollama', or 'nvidia'")):
    """Switch LLM provider at runtime."""
    if provider not in ("groq", "ollama", "nvidia"):
        raise HTTPException(status_code=400, detail="Provider must be 'groq', 'ollama', or 'nvidia'")

    if provider == "groq" and settings.groq_api_key == "your_groq_api_key_here":
        raise HTTPException(status_code=400, detail="Groq API key not configured")
    if provider == "nvidia" and settings.nvidia_api_key == "your_nvidia_api_key_here":
        raise HTTPException(status_code=400, detail="NVIDIA API key not configured")

    settings.llm_provider = provider
    if provider == "groq":
        model = settings.llm_model
    elif provider == "nvidia":
        model = settings.nvidia_model
    else:
        model = settings.ollama_model
    logger.info(f"Switched LLM provider to: {provider} ({model})")

    return {
        "provider": provider,
        "model": model,
        "message": f"Switched to {provider} ({model})",
    }


# ─── Bias & Fairness Endpoints ──────────────────────────────────────

@app.get("/bias/audit/{job_id}", tags=["Bias"])
def audit_fairness(
    job_id: int,
    threshold: float = Query(default=0.5, ge=0, le=1, description="Score threshold for selection"),
):
    """Run a fairness audit on match scores for a given job role."""
    session = SessionLocal()
    try:
        job = session.query(JobRole).get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job role {job_id} not found")

        results = match_candidates_to_job(job_id, top_k=100)
        candidates_data = [
            {"category": c.category, "name": c.name, "id": c.id}
            for c, _ in results
        ]
        scores = [score for _, score in results]

        audit = run_fairness_audit(candidates_data, scores, threshold=threshold)
        audit["job_id"] = job_id
        audit["job_title"] = job.title
        return audit
    finally:
        session.close()


@app.get("/bias/explain/{candidate_id}", tags=["Bias"])
def explain_candidate_score(
    candidate_id: int,
    job_id: int = Query(..., description="Job role ID"),
):
    """Explain why a candidate received their match score."""
    session = SessionLocal()
    try:
        candidate = session.query(Candidate).get(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

        job = session.query(JobRole).get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job role {job_id} not found")

        # Compute match score directly between candidate and job embeddings
        from sqlalchemy import text as sa_text
        from src.rag.retriever import _format_embedding
        match_score = 0.0
        if candidate.embedding is not None and job.embedding is not None:
            job_emb_str = _format_embedding(job.embedding)
            row = session.execute(
                sa_text("""
                    SELECT 1 - (embedding <=> CAST(:job_emb AS vector)) AS similarity
                    FROM candidates WHERE id = :cid
                """),
                {"job_emb": job_emb_str, "cid": candidate_id},
            ).fetchone()
            if row:
                match_score = round(float(row[0]), 4)

        candidate_data = {
            "name": candidate.name,
            "category": candidate.category,
            "skills": candidate.skills or [],
            "experience": candidate.experience or [],
            "education": candidate.education or [],
            "summary": candidate.summary,
            "total_years_experience": candidate.total_years_experience,
        }
        job_data = {
            "title": job.title,
            "department": job.department,
            "description": job.description,
            "requirements": job.requirements or [],
            "min_experience_years": job.min_experience_years,
        }

        explanation = explain_match_score(candidate_data, job_data, match_score)
        explanation["candidate_id"] = candidate_id
        explanation["candidate_name"] = candidate.name
        explanation["job_id"] = job_id
        explanation["job_title"] = job.title
        return explanation
    finally:
        session.close()


@app.get("/bias/anonymize/{candidate_id}", tags=["Bias"])
def get_anonymized_candidate(candidate_id: int):
    """Return an anonymized version of a candidate's profile."""
    session = SessionLocal()
    try:
        candidate = session.query(Candidate).get(candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")

        candidate_data = {
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "category": candidate.category,
            "skills": candidate.skills or [],
            "experience": candidate.experience or [],
            "education": candidate.education or [],
            "summary": candidate.summary,
            "total_years_experience": candidate.total_years_experience,
        }

        anonymized = anonymize_candidate(candidate_data)
        anonymized["candidate_id"] = candidate_id
        return anonymized
    finally:
        session.close()


# ─── Pipeline / Kanban Board ────────────────────────────────────────

PIPELINE_STAGES = [
    ("applied",   "Applied"),
    ("screened",  "Screened"),
    ("interview", "Interview"),
    ("offer",     "Offer"),
    ("hired",     "Hired"),
    ("rejected",  "Rejected"),
]
VALID_STAGES = {s for s, _ in PIPELINE_STAGES}


@app.get("/pipeline/{job_id}", response_model=PipelineResponse, tags=["Pipeline"])
def get_pipeline(job_id: int):
    """Return all applications for a job, grouped by pipeline stage."""
    session = SessionLocal()
    try:
        job = session.query(JobRole).get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job role {job_id} not found")

        apps = (
            session.query(Application, Candidate)
            .join(Candidate, Application.candidate_id == Candidate.id)
            .filter(Application.job_role_id == job_id)
            .order_by(Application.applied_at.desc())
            .all()
        )

        by_stage = {s: [] for s, _ in PIPELINE_STAGES}
        for app_row, cand in apps:
            stage = (app_row.status or "applied").lower()
            if stage not in by_stage:
                stage = "applied"
            by_stage[stage].append(PipelineCard(
                application_id=app_row.id,
                candidate_id=cand.id,
                candidate_name=cand.name,
                category=cand.category,
                skills=(cand.skills or [])[:10],
                total_years_experience=cand.total_years_experience,
                match_score=app_row.match_score,
                stage=stage,
                notes=app_row.notes,
            ))

        columns = [
            PipelineColumn(stage=s, label=lbl, count=len(by_stage[s]), cards=by_stage[s])
            for s, lbl in PIPELINE_STAGES
        ]
        return PipelineResponse(
            job_id=job_id, job_title=job.title,
            columns=columns, total=len(apps),
        )
    finally:
        session.close()


@app.post("/applications", tags=["Pipeline"])
def create_application(payload: ApplicationCreateRequest):
    """Add a candidate to a job's pipeline (creates an Application row)."""
    stage = (payload.stage or "applied").lower()
    if stage not in VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage '{stage}'. Must be one of {sorted(VALID_STAGES)}")

    session = SessionLocal()
    try:
        # Validate candidate and job exist
        if not session.query(Candidate).get(payload.candidate_id):
            raise HTTPException(status_code=404, detail=f"Candidate {payload.candidate_id} not found")
        if not session.query(JobRole).get(payload.job_role_id):
            raise HTTPException(status_code=404, detail=f"Job role {payload.job_role_id} not found")

        # Prevent duplicate (same candidate + job)
        existing = (
            session.query(Application)
            .filter_by(candidate_id=payload.candidate_id, job_role_id=payload.job_role_id)
            .first()
        )
        if existing:
            return {
                "id": existing.id, "status": existing.status,
                "message": "Candidate already in this pipeline",
                "duplicate": True,
            }

        notes = sanitize_text(payload.notes, max_length=MAX_FIELD_LENGTH) if payload.notes else None
        app_row = Application(
            candidate_id=payload.candidate_id,
            job_role_id=payload.job_role_id,
            match_score=payload.match_score,
            status=stage,
            notes=notes,
        )
        session.add(app_row)
        session.commit()
        session.refresh(app_row)
        return {
            "id": app_row.id, "status": app_row.status,
            "message": "Added to pipeline", "duplicate": False,
        }
    finally:
        session.close()


@app.post("/applications/bulk", tags=["Pipeline"])
def create_applications_bulk(payload: list[ApplicationCreateRequest]):
    """Bulk-add candidates to a job's pipeline in a single request.

    Used by the 'Add top 10 matches' quick action to avoid rate-limit thrash
    from 10 sequential POSTs.
    """
    if not payload:
        raise HTTPException(status_code=400, detail="Empty payload")
    if len(payload) > 100:
        raise HTTPException(status_code=400, detail="Max 100 applications per bulk request")

    session = SessionLocal()
    added, duplicates, errors = 0, 0, []
    try:
        # Prefetch existing (candidate_id, job_role_id) pairs to skip dups efficiently
        job_ids = {p.job_role_id for p in payload}
        cand_ids = {p.candidate_id for p in payload}
        existing_pairs = {
            (row.candidate_id, row.job_role_id)
            for row in session.query(Application)
                .filter(Application.job_role_id.in_(job_ids))
                .filter(Application.candidate_id.in_(cand_ids))
                .all()
        }

        # Also validate candidates/jobs exist in one query each
        valid_cands = {
            row.id for row in session.query(Candidate.id).filter(Candidate.id.in_(cand_ids)).all()
        }
        valid_jobs = {
            row.id for row in session.query(JobRole.id).filter(JobRole.id.in_(job_ids)).all()
        }

        for item in payload:
            stage = (item.stage or "applied").lower()
            if stage not in VALID_STAGES:
                errors.append({"candidate_id": item.candidate_id, "error": f"invalid stage '{stage}'"})
                continue
            if item.candidate_id not in valid_cands:
                errors.append({"candidate_id": item.candidate_id, "error": "candidate not found"})
                continue
            if item.job_role_id not in valid_jobs:
                errors.append({"candidate_id": item.candidate_id, "error": "job not found"})
                continue
            if (item.candidate_id, item.job_role_id) in existing_pairs:
                duplicates += 1
                continue

            notes = sanitize_text(item.notes, max_length=MAX_FIELD_LENGTH) if item.notes else None
            session.add(Application(
                candidate_id=item.candidate_id,
                job_role_id=item.job_role_id,
                match_score=item.match_score,
                status=stage,
                notes=notes,
            ))
            existing_pairs.add((item.candidate_id, item.job_role_id))
            added += 1

        session.commit()
        return {
            "added": added,
            "duplicates": duplicates,
            "errors": errors,
            "total_requested": len(payload),
        }
    finally:
        session.close()


@app.patch("/applications/{application_id}/stage", tags=["Pipeline"])
def update_application_stage(application_id: int, payload: StageUpdateRequest):
    """Move a candidate card to a different pipeline stage (drag-drop target)."""
    stage = (payload.stage or "").lower()
    if stage not in VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage '{stage}'. Must be one of {sorted(VALID_STAGES)}")

    session = SessionLocal()
    try:
        app_row = session.query(Application).get(application_id)
        if not app_row:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")

        prev = app_row.status
        app_row.status = stage
        session.commit()
        session.refresh(app_row)
        logger.info(f"Application {application_id} moved: {prev} → {stage}")
        return {
            "id": app_row.id,
            "previous_stage": prev,
            "stage": app_row.status,
            "message": f"Moved to {stage}",
        }
    finally:
        session.close()


@app.delete("/applications/{application_id}", tags=["Pipeline"])
def delete_application(application_id: int):
    """Remove a candidate from the pipeline."""
    session = SessionLocal()
    try:
        app_row = session.query(Application).get(application_id)
        if not app_row:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        session.delete(app_row)
        session.commit()
        return {"id": application_id, "message": "Removed from pipeline"}
    finally:
        session.close()
