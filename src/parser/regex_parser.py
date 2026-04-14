from __future__ import annotations

import re
from typing import Optional, List, Dict
from src.parser.models import ResumeData


def parse_resume_with_regex(raw_text: str, file_name: str, category: str) -> ResumeData:
    """Fallback regex-based parser for when LLM is unavailable."""
    return ResumeData(
        file_name=file_name,
        category=category,
        name=_extract_name(raw_text),
        email=_extract_email(raw_text),
        phone=_extract_phone(raw_text),
        skills=_extract_skills(raw_text),
        experience=_extract_experience(raw_text),
        education=_extract_education(raw_text),
        summary=_extract_summary(raw_text),
        raw_text=raw_text,
    )


def _extract_email(text: str) -> Optional[str]:
    match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    return match.group(0) if match else None


def _extract_phone(text: str) -> Optional[str]:
    match = re.search(
        r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text
    )
    return match.group(0).strip() if match else None


def _extract_name(text: str) -> Optional[str]:
    """Heuristic: first non-empty line that looks like a name (all caps or title case)."""
    lines = text.strip().split("\n")
    for line in lines[:5]:
        line = line.strip()
        if not line or "@" in line or re.search(r"\d{3}", line):
            continue
        # Skip lines that are section headers
        if line.upper() in {
            "SUMMARY", "EXPERIENCE", "EDUCATION", "SKILLS",
            "OBJECTIVE", "HIGHLIGHTS", "PROFILE",
        }:
            continue
        # If it looks like a name (2-4 words, mostly alpha)
        words = line.split()
        if 1 <= len(words) <= 5 and all(w.isalpha() or w in {"-", "."} for w in words):
            return line.title() if line.isupper() else line
    return None


def _extract_summary(text: str) -> Optional[str]:
    patterns = [
        r"(?:Summary|Objective|Profile)\s*\n([\s\S]*?)(?:\n(?:Experience|Highlights|Skills|Education))",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:500]
    return None


COMMON_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
    "rust", "php", "swift", "kotlin", "sql", "html", "css", "react", "angular",
    "vue", "node.js", "django", "flask", "fastapi", "spring", "docker",
    "kubernetes", "aws", "azure", "gcp", "terraform", "jenkins", "git",
    "linux", "windows", "macos", "postgresql", "mysql", "mongodb", "redis",
    "elasticsearch", "kafka", "rabbitmq", "graphql", "rest", "grpc",
    "machine learning", "deep learning", "nlp", "computer vision", "pytorch",
    "tensorflow", "scikit-learn", "pandas", "numpy", "spark", "hadoop",
    "tableau", "power bi", "excel", "word", "powerpoint", "photoshop",
    "figma", "sketch", "jira", "confluence", "agile", "scrum",
    "project management", "leadership", "communication", "teamwork",
    "problem solving", "critical thinking", "data analysis", "data science",
    "devops", "ci/cd", "microservices", "api", "networking", "security",
    "active directory", "vmware", "powershell", "bash", "sharepoint",
    "salesforce", "sap", "oracle", "accounting", "financial analysis",
    "marketing", "sales", "customer service", "healthcare", "nursing",
}


def _extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for skill in COMMON_SKILLS:
        if skill in text_lower:
            found.append(skill)
    return sorted(set(found))


def _extract_experience(text: str) -> list[dict]:
    """Extract experience entries using common resume patterns."""
    entries = []
    # Pattern: Title Date\nCompany
    pattern = r"([A-Za-z\s/&,]+?)\s+((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}|(?:\d{4}))\s+to\s+(Current|Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}|\d{4})"
    for match in re.finditer(pattern, text, re.IGNORECASE):
        title = match.group(1).strip()
        start = match.group(2).strip()
        end = match.group(3).strip()
        if len(title) < 100:
            entries.append({"title": title, "start": start, "end": end})
    return entries[:10]


def _extract_education(text: str) -> list[dict]:
    """Extract education entries."""
    entries = []
    degree_patterns = [
        r"((?:Bachelor|Master|Ph\.?D|Associate|MBA|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|B\.?E\.?|M\.?E\.?)[^,\n]*)",
    ]
    for pattern in degree_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            entries.append({"degree": match.group(1).strip()})
    return entries[:5]
