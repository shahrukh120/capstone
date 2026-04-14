"""
Batch parse all resumes in the data directory using LLM.

Usage:
    python -m scripts.parse_all_resumes                    # uses settings.llm_provider (default: ollama)
    python -m scripts.parse_all_resumes --provider ollama  # force local Ollama
    python -m scripts.parse_all_resumes --provider groq    # force Groq cloud
    python -m scripts.parse_all_resumes --resume-limit 100 # parse first N only
"""
import argparse
import json
import logging
import sys
import time
from pathlib import Path
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import settings
from src.parser.pdf_extractor import extract_text_from_pdf
from src.parser.llm_parser import parse_resume_with_llm

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def parse_all(provider: str = None, resume_limit: int = 0,
              model_override: str = None, delay_override: float = None):
    provider = provider or settings.llm_provider
    data_dir = settings.data_dir
    output_dir = settings.parsed_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Apply model override temporarily
    original_llm_model = settings.llm_model
    original_ollama_model = settings.ollama_model
    if model_override:
        if provider == "groq":
            settings.llm_model = model_override
        elif provider == "nvidia":
            settings.nvidia_model = model_override
        else:
            settings.ollama_model = model_override
        logger.info(f"Model override: {model_override}")

    pdf_files = sorted(data_dir.rglob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files total")

    # Skip already-parsed resumes
    remaining = []
    for pdf_path in pdf_files:
        category = pdf_path.parent.name
        file_name = pdf_path.stem
        out_file = output_dir / category / f"{file_name}.json"
        if not out_file.exists():
            remaining.append(pdf_path)

    logger.info(f"Already parsed: {len(pdf_files) - len(remaining)}, remaining: {len(remaining)}")
    logger.info(f"Using provider: {provider}")

    if resume_limit > 0:
        remaining = remaining[:resume_limit]
        logger.info(f"Limiting to {resume_limit} resumes this run")

    # Groq needs rate limiting; NVIDIA and Ollama can go fast
    if delay_override is not None:
        delay = delay_override
    else:
        delay = 15.0 if provider == "groq" else 1.0 if provider == "nvidia" else 0.0

    success, failed = 0, 0

    for pdf_path in tqdm(remaining, desc="Parsing resumes"):
        category = pdf_path.parent.name
        file_name = pdf_path.stem

        try:
            raw_text = extract_text_from_pdf(pdf_path)
            if not raw_text.strip():
                logger.warning(f"Empty text from {pdf_path}")
                failed += 1
                continue

            resume = parse_resume_with_llm(raw_text, file_name, category, provider=provider)

            # Save individual JSON
            out_file = output_dir / category / f"{file_name}.json"
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(resume.model_dump_json(indent=2))
            success += 1

        except Exception as e:
            logger.error(f"Failed to parse {pdf_path}: {e}")
            failed += 1
            if ("rate_limit" in str(e).lower() or "429" in str(e)):
                logger.info("Rate limited — waiting 60s")
                time.sleep(60)

        if delay > 0:
            time.sleep(delay)

    # Build combined JSON
    logger.info("Building combined JSON from all parsed resumes...")
    all_results = []
    for json_file in sorted(output_dir.rglob("*.json")):
        if json_file.name == "all_resumes.json":
            continue
        try:
            data = json.loads(json_file.read_text())
            all_results.append(data)
        except Exception:
            pass

    combined_path = output_dir / "all_resumes.json"
    combined_path.write_text(json.dumps(all_results, indent=2, default=str))

    logger.info(f"Done! This run — Success: {success}, Failed: {failed}")
    logger.info(f"Total parsed resumes: {len(all_results)}")
    logger.info(f"Output saved to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse all resumes with LLM")
    parser.add_argument("--provider", choices=["groq", "ollama", "nvidia"], default=None, help="LLM provider")
    parser.add_argument("--resume-limit", type=int, default=0, help="Max resumes to parse (0=all)")
    parser.add_argument("--model", default=None, help="Override model name (e.g. llama-3.1-8b-instant)")
    parser.add_argument("--delay", type=float, default=None, help="Override delay between requests (seconds)")
    args = parser.parse_args()
    parse_all(provider=args.provider, resume_limit=args.resume_limit,
              model_override=args.model, delay_override=args.delay)
