# AI-Powered Applicant Tracking System (ATS)

An end-to-end AI recruitment system built with LangGraph, pgvector, and FastAPI. Parses resumes with LLMs, matches candidates via semantic search, provides a conversational database agent, generates tailored interview questions, and audits for hiring bias.

## Architecture

```
PDF Resumes ─> LLM Parser ─> Structured JSON ─> PostgreSQL + pgvector
                                                       |
                                    ┌──────────────────┼──────────────────┐
                                    v                  v                  v
                              RAG Matching     ReAct SQL Agent     Bias Auditor
                              (semantic)       (conversational)    (fairlearn+SHAP)
                                    └──────────────────┼──────────────────┘
                                                       v
                                              FastAPI + Jinja2 UI
```

## Features

| Module | Description |
|--------|-------------|
| **Resume Parser** | PDF text extraction + LLM-powered structured parsing (name, skills, experience, education) |
| **RAG Pipeline** | Sentence-transformer embeddings (all-MiniLM-L6-v2) + pgvector cosine similarity matching |
| **ReAct Agent** | Multi-turn conversational Text-to-SQL with reasoning traces and natural language answers |
| **Interview Generator** | AI-generated technical, behavioral, and situational questions tailored to candidate + role |
| **Bias & Fairness** | Demographic parity audit (fairlearn), SHAP-based score explainability, PII anonymization |
| **Guardrails** | Prompt injection detection, SQL validation, rate limiting, PII detection, LLM output validation |
| **Multi-Provider LLM** | Hot-switchable between Groq, NVIDIA NIM, and Ollama (local) |
| **Responsive UI** | Mobile-friendly SPA with Tailwind CSS, collapsible sidebar, 8 feature pages |

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, LangGraph, LangChain
- **Database**: PostgreSQL 16 + pgvector (384-dim embeddings)
- **LLMs**: Groq (llama-3.3-70b), NVIDIA NIM (llama-3.3-70b-instruct), Ollama (gemma3:12b)
- **ML**: sentence-transformers, fairlearn, SHAP, scikit-learn
- **Frontend**: Jinja2 + Tailwind CSS + Lucide icons + vanilla JS
- **Deployment**: Docker Compose (local), Azure App Service + Azure Database for PostgreSQL (cloud)

## Quick Start (Local with Docker)

```bash
# 1. Clone the repo
git clone https://github.com/shahrukh120/capstone.git
cd capstone

# 2. Create .env from template
cp .env.example .env
# Edit .env — add your GROQ_API_KEY and/or NVIDIA_API_KEY

# 3. Add resume PDFs (optional — app auto-seeds from parsed_resumes/)
mkdir -p data parsed_resumes

# 4. Start services
docker compose up --build -d

# 5. Open the app
open http://localhost:8000
```

The entrypoint automatically:
1. Waits for PostgreSQL to be ready
2. Creates the schema + pgvector extension
3. Seeds the database from `parsed_resumes/` if empty
4. Starts the FastAPI server

## Deploy to Azure

### Prerequisites
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed and logged in (`az login`)
- A valid GROQ or NVIDIA API key

### One-command deploy

```bash
export DB_ADMIN_PASSWORD='YourStr0ngP@ss!'
export NVIDIA_API_KEY='nvapi-...'
export GROQ_API_KEY='gsk_...'

./azure-deploy.sh
```

This creates:
- **Resource Group**: `ats-capstone-rg`
- **Azure Container Registry**: Builds and hosts the Docker image
- **Azure Database for PostgreSQL Flexible Server**: PostgreSQL 16 with pgvector
- **Azure App Service (Linux)**: Runs the containerized app

After deployment, the app will be available at `https://ai-ats-app.azurewebsites.net`.

### Manual Azure steps (if needed)

See `azure-deploy.sh` for the full CLI commands. Key settings:
- **App SKU**: B2 (2 vCPU, 3.5 GB RAM) — sufficient for demo
- **DB SKU**: Standard_B1ms (Burstable) — 1 vCPU, 2 GB RAM
- **DB version**: PostgreSQL 16 with pgvector extension enabled

## Project Structure

```
capstone/
├── config/settings.py          # Pydantic settings (env-driven)
├── src/
│   ├── api/main.py             # FastAPI app + all endpoints
│   ├── api/schemas.py          # Pydantic request/response models
│   ├── parser/                 # PDF extraction + LLM parsing
│   ├── database/               # SQLAlchemy models + session
│   ├── rag/                    # Embeddings, chunker, retriever
│   ├── agents/                 # ReAct SQL agent, interview agent, LLM client, orchestrator
│   ├── bias/                   # Fairness audit, SHAP explainability, anonymizer
│   └── guardrails/             # Input validation, prompt/SQL guards, PII, rate limiter
├── scripts/                    # Batch parsing, seeding, embedding computation
├── templates/index.html        # SPA frontend
├── static/js/app.js            # Frontend logic
├── Dockerfile                  # Multi-stage container build
├── docker-compose.yml          # Local: app + pgvector DB
├── docker-compose.azure.yml    # Azure override (external DB)
├── azure-deploy.sh             # One-command Azure deployment
├── docker-entrypoint.sh        # Startup: DB wait → schema → seed → serve
└── requirements.txt            # Python dependencies
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Frontend SPA |
| GET | `/health` | Health check |
| GET | `/dashboard/stats` | Dashboard statistics |
| GET | `/jobs` | List all jobs |
| POST | `/jobs` | Create a new job |
| GET | `/candidates` | List candidates (filterable) |
| GET | `/match/{job_id}` | Semantic matching |
| POST | `/query` | Conversational SQL query |
| POST | `/query/clear` | Clear conversation |
| GET | `/interview/{candidate_id}` | Generate interview questions |
| POST | `/upload` | Upload and parse a resume |
| GET | `/llm/status` | Current LLM provider info |
| POST | `/llm/switch` | Switch LLM provider |
| GET | `/bias/audit/{job_id}` | Fairness audit |
| GET | `/bias/explain/{candidate_id}` | SHAP explainability |
| GET | `/bias/anonymize/{candidate_id}` | PII anonymization |

## LLM Providers

Switch providers live from the UI or via API:

| Provider | Model | Speed | Notes |
|----------|-------|-------|-------|
| **NVIDIA NIM** | llama-3.3-70b-instruct | ~5.6s/resume | Recommended for cloud deployment |
| **Groq** | llama-3.3-70b-versatile | ~3s/resume | 500K TPD limit |
| **Ollama** | gemma3:12b | ~72s/resume | Local only, no API key needed |

## Environment Variables

See `.env.example` for all configuration options.
