from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    groq_api_key: str = "your_groq_api_key_here"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ats_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama-3.3-70b-versatile"

    # LLM provider: "ollama" for local gemma3, "groq" for cloud, "nvidia" for NVIDIA NIM
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "gemma3:12b"

    # NVIDIA NIM API
    nvidia_api_key: str = "your_nvidia_api_key_here"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "meta/llama-3.3-70b-instruct"

    data_dir: Path = Path(__file__).resolve().parent.parent / "data"
    parsed_dir: Path = Path(__file__).resolve().parent.parent / "parsed_resumes"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
