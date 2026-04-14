"""Resume parser using LLM — supports both Groq (cloud) and Ollama (local)."""
import json
import logging
import requests
from groq import Groq
from src.parser.models import ResumeData
from config.settings import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a resume parsing assistant. Extract structured information from the resume text provided.

Return ONLY valid JSON with this exact schema (no markdown, no explanation):
{
  "name": "Full Name or null",
  "email": "email@example.com or null",
  "phone": "phone number or null",
  "skills": ["skill1", "skill2"],
  "experience": [
    {"title": "Job Title", "company": "Company Name", "start": "Start Date", "end": "End Date", "description": "Brief description"}
  ],
  "education": [
    {"degree": "Degree Name", "institution": "School Name", "year": "Graduation Year or null"}
  ],
  "summary": "1-2 sentence professional summary",
  "total_years_experience": 5.0
}

Rules:
- Extract ALL skills mentioned (technical and soft skills)
- For experience, include all positions found
- Estimate total_years_experience from the work history dates
- If information is not found, use null for strings and empty lists for arrays
"""


def _parse_with_groq(raw_text: str) -> dict:
    """Parse resume using Groq cloud API."""
    client = Groq(api_key=settings.groq_api_key, timeout=30.0, max_retries=2)
    truncated = raw_text[:4000]

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Parse this resume:\n\n{truncated}"},
        ],
        temperature=0.1,
        max_tokens=1500,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def _parse_with_ollama(raw_text: str) -> dict:
    """Parse resume using local Ollama (gemma3:12b)."""
    truncated = raw_text[:4000]
    prompt = f"{SYSTEM_PROMPT}\n\nParse this resume:\n\n{truncated}"

    response = requests.post(
        f"{settings.ollama_base_url}/api/generate",
        json={
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1, "num_predict": 1500},
        },
        timeout=300,
    )
    response.raise_for_status()
    result = response.json()
    return json.loads(result["response"])


def _parse_with_nvidia(raw_text: str) -> dict:
    """Parse resume using NVIDIA NIM API (OpenAI-compatible)."""
    truncated = raw_text[:4000]
    headers = {
        "Authorization": f"Bearer {settings.nvidia_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.nvidia_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Parse this resume:\n\n{truncated}"},
        ],
        "temperature": 0.1,
        "max_tokens": 1500,
        "stream": False,
    }

    response = requests.post(
        f"{settings.nvidia_base_url}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    # Strip markdown code fences if present
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    return json.loads(content)


def parse_resume_with_llm(
    raw_text: str, file_name: str, category: str, provider: str = None
) -> ResumeData:
    """Parse resume text using LLM for structured extraction.

    Args:
        provider: "groq" or "ollama". If None, uses settings.llm_provider.
    """
    provider = provider or settings.llm_provider

    if provider == "groq":
        if settings.groq_api_key == "your_groq_api_key_here":
            raise ValueError("Groq API key not configured. Set GROQ_API_KEY in .env")
        parsed = _parse_with_groq(raw_text)
    elif provider == "ollama":
        parsed = _parse_with_ollama(raw_text)
    elif provider == "nvidia":
        if settings.nvidia_api_key == "your_nvidia_api_key_here":
            raise ValueError("NVIDIA API key not configured. Set NVIDIA_API_KEY in .env")
        parsed = _parse_with_nvidia(raw_text)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

    # Normalize "null" string to actual None
    name = parsed.get("name")
    if name and str(name).lower() in ("null", "none", "n/a"):
        name = None

    return ResumeData(
        file_name=file_name,
        category=category,
        name=name,
        email=parsed.get("email"),
        phone=parsed.get("phone"),
        skills=parsed.get("skills", []),
        experience=parsed.get("experience", []),
        education=parsed.get("education", []),
        summary=parsed.get("summary"),
        total_years_experience=parsed.get("total_years_experience"),
        raw_text=raw_text,
    )
