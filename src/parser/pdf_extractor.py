from __future__ import annotations

import pdfplumber
from pathlib import Path
from typing import Union


def extract_text_from_pdf(pdf_path: Union[str, Path]) -> str:
    """Extract text from a PDF file using pdfplumber."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)
