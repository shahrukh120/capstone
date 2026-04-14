from __future__ import annotations

from typing import Optional, List, Dict
from pydantic import BaseModel


class ResumeData(BaseModel):
    file_name: str
    category: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience: List[Dict] = []
    education: List[Dict] = []
    summary: Optional[str] = None
    total_years_experience: Optional[float] = None
    raw_text: str = ""
