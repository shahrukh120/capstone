from __future__ import annotations

import os
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    groq_api_key: str = "your_groq_api_key_here"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ats_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama-3.3-70b-versatile"

    # LLM provider: "ollama" for local, "groq" for cloud, "nvidia" for NVIDIA NIM
    # Default to groq for cloud deployments; override via LLM_PROVIDER env var
    llm_provider: str = "groq"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:12b"

    # NVIDIA NIM API
    nvidia_api_key: str = "your_nvidia_api_key_here"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "meta/llama-3.3-70b-instruct"

    data_dir: Path = Path(__file__).resolve().parent.parent / "data"
    parsed_dir: Path = Path(__file__).resolve().parent.parent / "parsed_resumes"

    # SMTP (read directly via os.environ in src/communication/email_sender.py;
    # declared here so pydantic-settings doesn't reject them from .env)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True

    class Config:
        # Only load .env if it exists (not in Docker/Azure)
        env_file = ".env" if os.path.exists(".env") else None
        env_file_encoding = "utf-8"
        extra = "ignore"  # tolerate extra env vars (don't fail on unknown keys)


settings = Settings()
