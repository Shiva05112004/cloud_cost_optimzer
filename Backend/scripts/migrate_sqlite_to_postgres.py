"""Migrate data from SQLite to Postgres and verify row counts."""
import argparse
from typing import List

from sqlalchemy import create_engine, MetaData, Table, select, text


def fetch_table_names(engine) -> List[str]:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        return [row[0] for row in result if row[0] != 'sqlite_sequence']


def copy_table(sqlite_engine, pg_engine, table_name: str, chunk_size: int = 1000) -> None:
    sqlite_md = MetaData()
    pg_md = MetaData()
    sqlite_table = Table(table_name, sqlite_md, autoload_with=sqlite_engine)
    pg_table = Table(table_name, pg_md, autoload_with=pg_engine)

    with sqlite_engine.connect() as src, pg_engine.connect() as dst:
        rows = src.execute(select(sqlite_table)).fetchall()
        if not rows:
            return

        # Insert in chunks
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            payload = [dict(row._mapping) for row in chunk]
            dst.execute(pg_table.insert(), payload)
        dst.commit()


def get_count(engine, table_name: str) -> int:
    with engine.connect() as conn:
        res = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return int(res.scalar() or 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--sqlite-url', default='sqlite:///./cloud_optimizer.db')
    parser.add_argument('--postgres-url', default='postgresql+psycopg2://postgres:4321@localhost:5432/cloudcost')
    parser.add_argument('--truncate', action='store_true')
    args = parser.parse_args()

    sqlite_engine = create_engine(args.sqlite_url)
    pg_engine = create_engine(args.postgres_url)

    tables = fetch_table_names(sqlite_engine)
    if not tables:
        print('No tables found in SQLite.')
        return

    if args.truncate:
        with pg_engine.connect() as conn:
            for table in tables:
                conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
            conn.commit()

    for table in tables:
        copy_table(sqlite_engine, pg_engine, table)

    print('Row counts (sqlite -> postgres):')
    for table in tables:
        s_count = get_count(sqlite_engine, table)
        p_count = get_count(pg_engine, table)
        print(f"{table}: {s_count} -> {p_count}")


if __name__ == '__main__':
    main()
