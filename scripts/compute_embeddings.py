"""
Compute and store embeddings for all candidates and job roles.

Usage:
    python -m scripts.compute_embeddings
"""
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag.retriever import compute_and_store_embeddings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    compute_and_store_embeddings()
