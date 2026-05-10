#!/bin/bash
set -e

echo "--- Cloud Cost Optimizer Backend ---"

# 1. Create virtual environment if missing
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# 2. Activate
source venv/bin/activate

# 3. Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# 4. Copy .env if missing
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo ".env created from .env.example — fill in your values"
fi

# 5. Init SQLite DB (creates tables)
echo "Initialising SQLite database..."
python -m app.models.init_db

# 6. Start FastAPI
echo "Starting server at http://localhost:8000"
echo "Swagger docs at http://localhost:8000/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000