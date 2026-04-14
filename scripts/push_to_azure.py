"""
Push locally parsed resumes to the Azure-deployed ATS database.

Usage:
    python scripts/push_to_azure.py https://ai-ats-app.azurewebsites.net
    python scripts/push_to_azure.py http://localhost:8000  # for local testing
"""
import json
import sys
import time
import requests
from pathlib import Path

PARSED_DIR = Path(__file__).resolve().parent.parent / "parsed_resumes"
BATCH_SIZE = 50  # candidates per request
MAX_RETRIES = 3


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/push_to_azure.py <APP_URL>")
        print("  e.g. python scripts/push_to_azure.py https://ai-ats-app.azurewebsites.net")
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")
    seed_url = f"{base_url}/seed/candidates"

    # Collect all parsed JSONs
    json_files = sorted(PARSED_DIR.rglob("*.json"))
    json_files = [f for f in json_files if f.name != "all_resumes.json"]

    if not json_files:
        print(f"No JSON files found in {PARSED_DIR}")
        sys.exit(1)

    print(f"Found {len(json_files)} parsed resumes in {PARSED_DIR}")
    print(f"Pushing to {seed_url} in batches of {BATCH_SIZE}...")

    total_inserted = 0
    total_skipped = 0

    batch = []
    for i, json_file in enumerate(json_files):
        data = json.loads(json_file.read_text())
        batch.append(data)

        if len(batch) >= BATCH_SIZE or i == len(json_files) - 1:
            for retry in range(MAX_RETRIES):
                try:
                    resp = requests.post(seed_url, json=batch, timeout=120)
                    if resp.status_code == 429:
                        wait = 5 * (retry + 1)
                        print(f"  Rate limited, waiting {wait}s...")
                        time.sleep(wait)
                        continue
                    resp.raise_for_status()
                    result = resp.json()
                    total_inserted += result["inserted"]
                    total_skipped += result["skipped"]
                    print(f"  Batch {i // BATCH_SIZE + 1}: +{result['inserted']} inserted, "
                          f"{result['skipped']} skipped ({i + 1}/{len(json_files)} processed)")
                    break
                except requests.exceptions.HTTPError as e:
                    if "429" not in str(e):
                        print(f"  ERROR on batch ending at file {i}: {e}")
                        break
                except Exception as e:
                    print(f"  ERROR on batch ending at file {i}: {e}")
                    break
            batch = []

    print(f"\nDone! Inserted: {total_inserted}, Skipped: {total_skipped}")
    print(f"\nNow run embeddings: POST {base_url}/seed/embeddings (or compute locally)")


if __name__ == "__main__":
    main()
