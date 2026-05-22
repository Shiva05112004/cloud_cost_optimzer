# Postgres and Alembic Setup

## 1) Start local Postgres + Redis

```bash
docker compose up -d
```

## 2) Configure environment

Create a `.env` based on `.env.example` and point `DATABASE_URL` at Postgres.

## 3) Initialize Alembic

From the `Backend` folder:

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## 3a) Verify Postgres connectivity

```bash
python scripts/check_postgres.py \
  --postgres-url postgresql+psycopg2://postgres:4321@localhost:5432/cloudcost
```

## 4) Migrate SQLite data to Postgres

```bash
python scripts/migrate_sqlite_to_postgres.py \
  --sqlite-url sqlite:///../cloud_optimizer.db \
  --postgres-url postgresql+psycopg2://postgres:4321@localhost:5432/cloudcost \
  --truncate
```

The script prints row counts for each table in SQLite and Postgres so you can verify the migration.
