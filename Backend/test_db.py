import os
from sqlalchemy import create_engine, text

url = os.getenv("DATABASE_URL")
print("Using DATABASE_URL:", url)

engine = create_engine(url)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Connected successfully, result:", result.scalar())
except Exception as e:
    print("❌ Connection failed:", e)
