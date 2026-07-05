"""Basic Postgres connectivity check."""
import argparse

from sqlalchemy import create_engine, text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--postgres-url', default='postgresql+psycopg2://postgres:4321@localhost:5432/cloudcost')
    args = parser.parse_args()

    engine = create_engine(args.postgres_url)
    with engine.connect() as conn:
        res = conn.execute(text('SELECT 1'))
        print(f'Postgres OK: {res.scalar()}')


if __name__ == '__main__':
    main()
