"""Generate ATS_Architecture.pdf — detailed architecture document."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Table,
    TableStyle, KeepTogether,
)

OUT = "ATS_Architecture.pdf"

# ── Styles ──────────────────────────────────────────────────────────
styles = getSampleStyleSheet()
INDIGO = colors.HexColor("#4f46e5")
DARK = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#6b7280")
LIGHT_BG = colors.HexColor("#f3f4f6")
CODE_BG = colors.HexColor("#0f172a")
CODE_FG = colors.HexColor("#e2e8f0")

TITLE = ParagraphStyle(
    "Title", parent=styles["Title"], fontSize=24, textColor=INDIGO,
    alignment=TA_CENTER, spaceAfter=8, leading=28,
)
SUBTITLE = ParagraphStyle(
    "Subtitle", parent=styles["Normal"], fontSize=11, textColor=MUTED,
    alignment=TA_CENTER, spaceAfter=18,
)
H1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontSize=17, textColor=INDIGO,
    spaceBefore=16, spaceAfter=10, leading=22,
)
H2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontSize=13, textColor=DARK,
    spaceBefore=12, spaceAfter=6, leading=18,
)
H3 = ParagraphStyle(
    "H3", parent=styles["Heading3"], fontSize=11, textColor=DARK,
    spaceBefore=8, spaceAfter=4, leading=15,
)
BODY = ParagraphStyle(
    "Body", parent=styles["Normal"], fontSize=10, textColor=DARK,
    leading=14, spaceAfter=6,
)
BULLET = ParagraphStyle(
    "Bullet", parent=BODY, leftIndent=14, bulletIndent=2, spaceAfter=3,
)
CODE = ParagraphStyle(
    "Code", parent=styles["Code"], fontName="Courier", fontSize=7.5,
    textColor=CODE_FG, backColor=CODE_BG, leftIndent=6, rightIndent=6,
    spaceBefore=4, spaceAfter=8, leading=10, borderPadding=8,
)


def p(text, style=BODY):
    return Paragraph(text, style)


def pre(text):
    return Preformatted(text, CODE)


def bullets(items):
    return [Paragraph(f"• {it}", BULLET) for it in items]


def table(data, col_widths=None, header=True):
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    style = [
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    t.setStyle(TableStyle(style))
    return t


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10 * mm, "AI-Powered ATS — System Architecture")
    canvas.drawRightString(
        A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}"
    )
    canvas.setStrokeColor(colors.HexColor("#e5e7eb"))
    canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canvas.restoreState()


# ── Content ─────────────────────────────────────────────────────────
story = []

# Cover
story.append(Spacer(1, 40 * mm))
story.append(p("AI-Powered ATS", TITLE))
story.append(p("Detailed System Architecture", ParagraphStyle(
    "t2", parent=TITLE, fontSize=16, textColor=DARK, spaceAfter=4,
)))
story.append(Spacer(1, 8))
story.append(p(
    "Applicant Tracking System built on FastAPI, LangGraph, pgvector, "
    "and multi-provider LLMs — with bias auditing, guardrails, and SMTP-based candidate outreach.",
    SUBTITLE,
))
story.append(Spacer(1, 20))
story.append(p(
    "<b>Production URL:</b> https://ai-ats-app.azurewebsites.net<br/>"
    "<b>Repository:</b> github.com/shahrukh120/capstone<br/>"
    "<b>Deployment:</b> Azure App Service + Azure Container Registry<br/>"
    "<b>Document version:</b> April 2026",
    ParagraphStyle("cover", parent=BODY, alignment=TA_CENTER, textColor=MUTED, fontSize=10),
))
story.append(PageBreak())

# ── Section 1: System Overview ──
story.append(p("1. System Overview", H1))
story.append(p(
    "The ATS is a full-stack recruiter tool: recruiters upload resumes, the system parses them "
    "with an LLM, indexes them semantically, and provides matching, pipeline management, ad-hoc "
    "SQL chat, bias auditing, and automated candidate outreach (email + interview invites). "
    "Every external interaction is protected by a layered guardrail stack.",
))
story.append(pre("""┌─────────────────────────────────────────────────────────────┐
│                    USERS (Recruiters)                       │
│           Browser SPA — Tailwind + vanilla JS               │
└─────────────────────────┬───────────────────────────────────┘
                          │  HTTPS
┌─────────────────────────▼───────────────────────────────────┐
│         AZURE APP SERVICE  (Linux container)                │
│  Image: atscapstoneacr123.azurecr.io/ats-app:email-v1       │
│  Stack: Python 3.11 + FastAPI + Uvicorn                     │
└────────┬──────────────┬────────────────────┬────────────────┘
         ▼              ▼                    ▼
  ┌────────────┐  ┌────────────┐      ┌──────────────┐
  │ Postgres   │  │  LLM APIs  │      │  Gmail SMTP  │
  │ + pgvector │  │ Groq /     │      │  (app pwd)   │
  │ (Azure DB) │  │ NVIDIA NIM │      │              │
  └────────────┘  └────────────┘      └──────────────┘"""))

# ── Section 2: Layered Architecture ──
story.append(p("2. Layered Architecture", H1))
story.append(p(
    "The codebase follows a strict layered design. Cross-cutting concerns "
    "(guardrails, observability, config) are isolated into their own packages.",
))
story.append(pre("""╔═════════════════════════════════════════════════════════════╗
║   PRESENTATION                                              ║
║   templates/index.html   — single-page Jinja2 shell         ║
║   static/js/app.js       — fetch-based SPA, Kanban drag-drop║
╠═════════════════════════════════════════════════════════════╣
║   API  (FastAPI)                                            ║
║   src/api/main.py        — 30+ REST endpoints               ║
║   src/api/schemas.py     — Pydantic request/response models ║
║   Middleware: CORS, rate limiter, static mount              ║
╠═════════════════════════════════════════════════════════════╣
║   GUARDRAILS  (cross-cutting)                               ║
║   src/guardrails/                                           ║
║     input_validator  prompt_guard  resume_validator         ║
║     rate_limiter     pii_detector  sql_guard                ║
║     llm_output_guard                                        ║
╠═════════════════════════════════════════════════════════════╣
║   DOMAIN                                                    ║
║   parser/  rag/  agents/  bias/  communication/             ║
╠═════════════════════════════════════════════════════════════╣
║   DATA                                                      ║
║   src/database/ — SQLAlchemy ORM, Postgres + pgvector       ║
╚═════════════════════════════════════════════════════════════╝"""))
story.append(PageBreak())

# ── Section 3: Modules ──
story.append(p("3. Module-by-Module Detail", H1))

# 3.1 Parser
story.append(p("3.1 Parser — <font color='#6b7280'>src/parser/</font>", H2))
story.append(p("Transforms a raw PDF into a structured ResumeData object."))
story.append(pre("""┌────────────┐   ┌─────────────────┐   ┌────────────────────┐
│ PDF upload │──▶│ pdf_extractor   │──▶│ raw_text (no NUL)  │
└────────────┘   │ pdfplumber      │   └─────────┬──────────┘
                 └─────────────────┘             │
                 ┌──────────────────┐  ┌─────────▼──────────┐
                 │ regex_parser     │  │ llm_parser         │
                 │ email/phone      │  │ Groq/NVIDIA JSON   │
                 └──────────────────┘  └─────────┬──────────┘
                                                 ▼
                         ResumeData {name, email, phone, skills[],
                                     experience[], education[],
                                     summary, total_years_experience}"""))

# 3.2 RAG
story.append(p("3.2 RAG — <font color='#6b7280'>src/rag/</font>", H2))
story.append(p(
    "Embeds candidates with SentenceTransformer (all-MiniLM-L6-v2, 384 dims) and stores "
    "them in a pgvector column. Retrieval is cosine similarity via the &lt;=&gt; operator."
))
story.append(pre("""┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ chunker.py   │─▶│ embeddings.py    │─▶│ pgvector column  │
│ prep text    │  │ MiniLM (MPS/CPU) │  │ candidates.embed │
└──────────────┘  └──────────────────┘  └────────┬─────────┘
                                                 │
                                                 ▼
                         retriever.py
                           match_candidates_to_job(job_id)
                           get_top_candidates(query)
                           SQL: ORDER BY embedding <=> :query"""))

# 3.3 Agents
story.append(p("3.3 Agents — <font color='#6b7280'>src/agents/</font>", H2))
story.append(p(
    "All LLM calls route through a single <b>llm_client.py</b> that switches between "
    "Groq, NVIDIA NIM, and Ollama. LangGraph wires parser → matching → interview nodes. "
    "Text-to-SQL is a ReAct loop with conversation memory."
))
story.append(pre("""              llm_client.py  (provider router)
          ┌──────┐    ┌──────┐    ┌───────┐
          │ Groq │    │NVIDIA│    │Ollama │
          └──┬───┘    └──┬───┘    └──┬────┘
             └──────┬────┴───────────┘
                    ▼
    ┌───────────────────┐  ┌──────────────────┐  ┌──────────────────┐
    │ orchestrator.py   │  │ text_to_sql.py   │  │ interview_agent  │
    │ LangGraph         │  │ ReAct loop +     │  │ JD + resume →    │
    │  parser_node      │  │ ConversationMem  │  │  ranked Qs       │
    │  matching_node    │  │ + sql_guard      │  │  w/ rationale    │
    │  interview_node   │  │                  │  │                  │
    └───────────────────┘  └──────────────────┘  └──────────────────┘"""))
story.append(p("<b>Orchestrator state (TypedDict):</b>", BODY))
story.append(pre("""PipelineState {
  pdf_path, job_id, query,         # inputs
  parsed_resume, candidate_id,     # parser_node output
  matches: List[Dict],             # matching_node output
  interview_questions: List[Dict], # interview_node output
}"""))

story.append(PageBreak())

# 3.4 Bias
story.append(p("3.4 Bias — <font color='#6b7280'>src/bias/</font>", H2))
story.append(p(
    "Three complementary fairness tools: <b>anonymize</b> before LLM-as-judge, "
    "<b>audit</b> score disparities across cohorts, <b>explain</b> per-skill match contributions."
))
story.append(table([
    ["Module", "Purpose", "Endpoint"],
    ["anonymizer.py", "Strip name, email, pronouns, schools, photos", "/candidates/{id}/anon"],
    ["fairness.py", "Score disparity report across category / gender hint", "/audit/fairness"],
    ["explainability.py", "Per-skill contribution + LLM rationale", "/candidates/{id}/explain"],
], col_widths=[40*mm, 80*mm, 45*mm]))

# 3.5 Communication
story.append(p("3.5 Communication — <font color='#6b7280'>src/communication/</font>", H2))
story.append(p(
    "SMTP-based email delivery using Python's built-in smtplib — supports STARTTLS (587) "
    "and implicit SSL (465). Meeting links: paste Google Meet/Teams URL, or auto-generate "
    "a free Jitsi room with a UUID-scoped room name. Templated HTML + plain-text invites."
))
story.append(pre("""send_email(to, subject, body, html_body)
     │
     ▼  smtplib STARTTLS 587  OR  SMTP_SSL 465
┌────────────────────────┐
│ Gmail / SendGrid /     │
│ Outlook / any SMTP     │
└────────────────────────┘

send_interview_invite(...)
  ├─ subject + HTML body (indigo header, emoji, link button)
  ├─ plain-text fallback
  └─ generate_jitsi_link() if auto_jitsi=True and no link pasted
         → https://meet.jit.si/ats-interview-<uuid12>"""))

# 3.6 Data model
story.append(p("3.6 Data Model — <font color='#6b7280'>src/database/models.py</font>", H2))
story.append(pre("""Candidate                         JobRole
────────────────────────          ──────────────────────
id PK                             id PK
file_name UNIQUE                  title
category                          department
name / email / phone              description
skills       JSONB                requirements  JSONB
experience   JSONB                min_experience_years
education    JSONB                location, salary_range
summary      TEXT                 status
raw_text     TEXT
embedding    vector(384)
total_years_experience
                    │                │
                    └────────┬───────┘
                             ▼
                   Application
                   ──────────────────────
                   id PK
                   candidate_id  FK
                   job_role_id   FK
                   stage  (applied/screened/interview/
                           offer/hired/rejected)
                   match_score
                   notes
                   created_at / updated_at"""))

story.append(PageBreak())

# ── Section 4: Request flows ──
story.append(p("4. Request Flows", H1))
story.append(p("The five most important end-to-end flows in the system."))

story.append(p("4.1 Resume Upload", H2))
story.append(pre("""POST /upload (file, category)
  ▼
[1] filename .pdf          ▶ validate_category()
[2] category whitelist     ▶ validate_file_size()
[3] size ≤ 10 MB           ▶ PDF magic bytes %PDF-
[4] extract text           ▶ strip NUL bytes (Postgres)
[5] looks_like_resume()    ◀ heuristic scoring (reject recipes, etc.)
[6] detect_prompt_injection ◀ scan raw_text
  ▼
[7] llm_parser → Groq/NVIDIA → JSON
[8] strip NUL from LLM output
[9] embed_text(summary + skills) → vector(384)
[10] INSERT candidates (..., embedding)
[11] return UploadResponse"""))

story.append(p("4.2 Job Match", H2))
story.append(pre("""GET /match/{job_id}?top_k=10
  ▼
Load JobRole → build query text (title + description + requirements)
  ▼
embed_text(query) → vector(384)
  ▼
SELECT *, 1 - (embedding <=> :q) AS score
FROM candidates ORDER BY embedding <=> :q LIMIT :top_k
  ▼
MatchResponse { job_id, job_title, matches[] }"""))

story.append(p("4.3 Text-to-SQL (conversational)", H2))
story.append(pre("""POST /query {question, session_id}
  ▼
get_conversation(session_id) → ConversationMemory (last N turns)
  ▼
┌─ ReAct loop ───────────────────────────────────────────┐
│  THOUGHT: which tables/columns?                        │
│  ACTION:  generate SQL                                 │
│  OBSERVATION: sql_guard → execute → rows               │
│  THOUGHT: do rows answer the question?                 │
│  ACTION:  write natural-language answer                │
└────────────────────────────────────────────────────────┘
  ▼
QueryResponse {sql, explanation, results, columns,
               answer, thought}"""))

story.append(p("4.4 Pipeline / Kanban", H2))
story.append(pre("""GET /pipeline/{job_id}
  ▼  JOIN applications ⨝ candidates  (filter job_role_id)
  ▼  Group by stage → 6 columns
  ▼  PipelineResponse → renderPipelineBoard() → drag-drop UI

PATCH /applications/{id}/stage {stage}
  ▼  Optimistic UI update + DB write
  ▼  Refresh column counts"""))

story.append(p("4.5 Interview Invite (email)", H2))
story.append(pre("""POST /candidates/{id}/interview-invite
   {job_id, meeting_link?, auto_jitsi, datetime, ...}
  ▼
[1] load candidate.email (or to_override)
[2] is_valid_email()
[3] sanitize_text + detect_prompt_injection on custom_message
[4] if no link and auto_jitsi → generate_jitsi_link()
  ▼
send_interview_invite() builds plain + HTML bodies
  ▼
smtplib STARTTLS → Gmail App Password → candidate inbox
  ▼
EmailResponse {ok, to, subject, meeting_link, source}"""))

story.append(PageBreak())

# ── Section 5: Guardrails ──
story.append(p("5. Guardrails — Defense in Depth", H1))
story.append(p(
    "Every untrusted input is filtered <b>before</b> business logic. LLM calls are guarded on both "
    "sides (input prompt-injection scan, output JSON validation). Text-to-SQL has a strict write-block."
))

story.append(p("5.1 Input-side guards", H2))
story.append(table([
    ["Endpoint", "Guards applied"],
    ["/upload", "Extension, magic bytes, size, category, NUL strip, resume heuristic, prompt-injection scan"],
    ["/query", "Length cap, sanitize_text, prompt-injection detection"],
    ["/jobs (POST)", "JD length, sanitize, field validation"],
    ["/candidates/…/email", "Sanitize subject+body, prompt-injection on body and custom_message, URL scheme (https://) check"],
    ["ALL endpoints", "Rate limiter (per-IP sliding window, tiered by endpoint class)"],
], col_widths=[45*mm, 120*mm]))

story.append(p("5.2 LLM-facing guards", H2))
story.extend(bullets([
    "<b>Before LLM call:</b> sanitize_text + prompt_guard on any user-originated text",
    "<b>After LLM call:</b> llm_output_guard validates JSON shape; retries on malformed output",
    "<b>Text-to-SQL:</b> sql_guard blocks DROP / DELETE / UPDATE / INSERT / DDL, blocks system tables (pg_*, information_schema), enforces SELECT-only with row limit",
]))

story.append(p("5.3 Output-side guards", H2))
story.extend(bullets([
    "<b>pii_detector.redact_pii()</b> before any sensitive data hits logs",
    "<b>bias.anonymizer</b> before LLM-as-judge in scoring or explainability",
    "<b>fairness audit</b> available on demand for any cohort",
]))

story.append(p("5.4 Rate-limit tiers (per IP, sliding window)", H2))
story.append(table([
    ["Endpoint class", "Limit", "Rationale"],
    ["/upload", "Strict", "Each upload burns LLM tokens"],
    ["/query, /interview", "Medium", "LLM-backed, moderate cost"],
    ["Everything else", "Lenient", "Read-only, fast"],
], col_widths=[50*mm, 30*mm, 75*mm]))

story.append(PageBreak())

# ── Section 6: Config & secrets ──
story.append(p("6. Configuration & Secrets", H1))
story.append(p(
    "Configuration is driven by <b>pydantic-settings</b> with <code>extra=\"ignore\"</code> so "
    "operational env vars (SMTP_*, ALLOWED_ORIGINS, etc.) co-exist with typed settings."
))
story.append(pre("""config/settings.py  —  reads .env (local) or env vars (Azure)

  GROQ_API_KEY, NVIDIA_API_KEY
  DATABASE_URL
  LLM_PROVIDER  (groq | nvidia | ollama)
  LLM_MODEL     (llama-3.3-70b-versatile, ...)
  EMBEDDING_MODEL  (all-MiniLM-L6-v2)
  SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASSWORD
  SMTP_FROM / SMTP_USE_TLS
  ALLOWED_ORIGINS"""))

# ── Section 7: Deployment ──
story.append(p("7. Deployment Topology", H1))
story.append(pre("""┌──────────────────────────────────────────────────────────┐
│  GitHub  —  shahrukh120/capstone (main)                  │
└─────────────────┬────────────────────────────────────────┘
                  │ git push
                  ▼
┌──────────────────────────────────────────────────────────┐
│  Local dev (macOS)                                       │
│  docker buildx --platform linux/amd64  →  push           │
└─────────────────┬────────────────────────────────────────┘
                  ▼
┌──────────────────────────────────────────────────────────┐
│  Azure Container Registry                                │
│  atscapstoneacr123.azurecr.io/ats-app                    │
│   tags: :email-v1   :kanban   :latest                    │
└─────────────────┬────────────────────────────────────────┘
                  │ DOCKER_ENABLE_CI=true  (webhook)
                  ▼
┌──────────────────────────────────────────────────────────┐
│  Azure App Service  (ai-ats-app, India region)           │
│  Linux container, single instance                        │
│  ENV: GROQ_API_KEY, NVIDIA_API_KEY, DATABASE_URL,        │
│       SMTP_HOST/USER/PASSWORD/FROM/USE_TLS               │
└────┬───────────────────┬────────────────────┬────────────┘
     ▼                   ▼                    ▼
┌──────────────┐  ┌──────────────┐    ┌───────────────┐
│ Azure DB     │  │ Groq API     │    │ Gmail SMTP    │
│ Postgres +   │  │ NVIDIA NIM   │    │ 587 STARTTLS  │
│ pgvector     │  │ (fallback)   │    │               │
└──────────────┘  └──────────────┘    └───────────────┘"""))

story.append(PageBreak())

# ── Section 8: End-to-end journey ──
story.append(p("8. End-to-End Recruiter Journey", H1))
story.append(p(
    "The full workflow stitched together, touching every major module."
))
story.append(table([
    ["#", "Step", "Module(s) involved"],
    ["1", "Upload resume PDF", "guardrails (8 layers) → parser → rag → database"],
    ["2", "Create job role, find matches", "database → rag.retriever → embeddings"],
    ["3", "Analyze a match (explain)", "bias.explainability + llm_client"],
    ["4", "Add top matches to Kanban", "database (Application bulk insert)"],
    ["5", "Generate interview questions", "agents.interview_agent → llm_client"],
    ["6", "Send interview invite", "communication.email_sender → Gmail SMTP"],
    ["7", "Drag card through stages", "api (PATCH) → database"],
    ["8", "Fairness audit", "bias.fairness → cohort-level score report"],
    ["9", "Ad-hoc SQL chat", "agents.text_to_sql (ReAct) + sql_guard"],
], col_widths=[10*mm, 55*mm, 100*mm]))

# ── Section 9: Intentional gaps ──
story.append(p("9. Intentional Gaps (Future Work)", H1))
story.append(p("Limitations that are acknowledged design choices, not bugs."))
story.extend(bullets([
    "No background workers (Celery / RQ) — everything is sync request/response",
    "No object storage — PDFs are parsed and discarded; only raw_text persisted",
    "No auth / multi-tenancy — single shared workspace",
    "No event bus / webhooks — pipeline changes are not broadcast",
    "No AI voice interviewer — planned as a future phase (OpenAI Realtime or LiveKit Agents)",
    "No calendar integration — Google Meet / Teams URLs must be pasted manually",
    "No EEOC / DPDP compliance export",
]))

# ── Section 10: Module index ──
story.append(p("10. Module Index", H1))
story.append(table([
    ["Package", "Files", "Responsibility"],
    ["src/api", "main.py, schemas.py", "FastAPI app, 30+ endpoints, Pydantic models"],
    ["src/parser", "pdf_extractor, regex_parser, llm_parser, models", "PDF → ResumeData"],
    ["src/rag", "chunker, embeddings, retriever", "Semantic indexing and search"],
    ["src/agents", "orchestrator, llm_client, text_to_sql, interview_agent", "LLM workflows"],
    ["src/bias", "anonymizer, fairness, explainability", "Fairness and explanation tools"],
    ["src/communication", "email_sender", "SMTP + Jitsi link generation"],
    ["src/guardrails", "input_validator, prompt_guard, resume_validator, rate_limiter, pii_detector, sql_guard, llm_output_guard", "Defense-in-depth"],
    ["src/database", "models, session", "SQLAlchemy ORM + pgvector"],
    ["config", "settings.py", "pydantic-settings config loader"],
    ["scripts", "seed_database, compute_embeddings, parse_all_resumes, push_to_azure", "Ops / one-off jobs"],
    ["templates / static", "index.html, app.js", "SPA shell + client"],
], col_widths=[35*mm, 60*mm, 70*mm]))

# ── Footer line on last page ──
story.append(Spacer(1, 12))
story.append(p(
    "<i>Generated from the capstone codebase. "
    "Re-run scripts/generate_architecture_pdf.py after architectural changes.</i>",
    ParagraphStyle("footer", parent=BODY, fontSize=8, textColor=MUTED, alignment=TA_CENTER),
))


# ── Build ──
doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=18*mm, rightMargin=18*mm,
    topMargin=18*mm, bottomMargin=18*mm,
    title="AI-Powered ATS — Architecture",
    author="Capstone",
)
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"Wrote {OUT}")
