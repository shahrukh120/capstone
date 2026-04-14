#!/bin/bash
set -e

echo "========================================="
echo "  AI-Powered ATS — Starting Up"
echo "========================================="

# Wait for PostgreSQL to be ready
echo "[1/4] Waiting for database..."
MAX_RETRIES=30
RETRY=0
until python -c "
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/ats_db'))
with engine.connect() as conn:
    conn.execute(text('SELECT 1'))
    print('Database connected!')
" 2>/dev/null; do
    RETRY=$((RETRY+1))
    if [ $RETRY -ge $MAX_RETRIES ]; then
        echo "ERROR: Database not reachable after $MAX_RETRIES attempts"
        exit 1
    fi
    echo "  Waiting for DB... ($RETRY/$MAX_RETRIES)"
    sleep 2
done

# Create tables + pgvector extension
echo "[2/4] Initializing database schema..."
python -c "
from src.database.session import engine, SessionLocal
from src.database.models import Base
from sqlalchemy import text

# Ensure pgvector extension exists
with engine.connect() as conn:
    conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
    conn.commit()

Base.metadata.create_all(bind=engine)
print('Schema ready!')
"

# Seed database if empty (only on first run)
echo "[3/4] Checking if seeding is needed..."
python -c "
from src.database.session import SessionLocal
from src.database.models import Candidate
session = SessionLocal()
count = session.query(Candidate).count()
session.close()
if count == 0:
    print('Database empty — running seed...')
    import subprocess, sys
    subprocess.run([sys.executable, '-m', 'scripts.seed_database'], check=True)
    subprocess.run([sys.executable, '-m', 'scripts.compute_embeddings'], check=True)
    print('Seeding complete!')
else:
    print(f'Database has {count} candidates — skipping seed.')
"

echo "[4/4] Starting application server..."
echo "========================================="

exec "$@"
