"""Generate synthetic telemetry data with failure patterns."""
import argparse
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from app.config import get_settings
from app.models.metric_features import MetricFeature
from app.models.database import SessionLocal


def generate_series(days: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    hours = days * 24
    start = datetime.utcnow() - timedelta(hours=hours)
    timestamps = [start + timedelta(hours=i) for i in range(hours)]

    hour_of_day = np.array([t.hour for t in timestamps])
    daily_wave = np.sin((hour_of_day / 24.0) * 2 * np.pi)

    cpu = 40 + 10 * daily_wave + rng.normal(0, 3, size=hours)
    memory = 60 + 6 * daily_wave + rng.normal(0, 2, size=hours)
    connections = 200 + 40 * daily_wave + rng.normal(0, 15, size=hours)

    df = pd.DataFrame({
        "ts": timestamps,
        "cpu": cpu.clip(0, 100),
        "memory": memory.clip(0, 100),
        "connections": connections.clip(0, None),
        "is_failure_imminent": 0,
    })

    return df


def inject_failures(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    hours = len(df)
    failure_count = max(1, hours // (24 * 7))

    for _ in range(failure_count):
        start_idx = rng.integers(24, hours - 12)
        window = slice(start_idx, start_idx + 6)

        df.loc[window, "connections"] += rng.normal(150, 30, size=6)
        df.loc[window, "cpu"] += rng.normal(20, 5, size=6)
        df.loc[window, "memory"] += rng.normal(10, 3, size=6)

        label_window = slice(start_idx + 3, start_idx + 6)
        df.loc[label_window, "is_failure_imminent"] = 1

    return df


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["cpu_velocity"] = df["cpu"].diff().fillna(0.0)
    df["memory_velocity"] = df["memory"].diff().fillna(0.0)
    df["connections_velocity"] = df["connections"].diff().fillna(0.0)

    df["rolling_cpu"] = df["cpu"].rolling(6, min_periods=1).mean()
    df["rolling_memory"] = df["memory"].rolling(6, min_periods=1).mean()
    df["rolling_connections"] = df["connections"].rolling(6, min_periods=1).mean()
    return df


def insert_rows(df: pd.DataFrame) -> None:
    db = SessionLocal()
    try:
        objs = []
        for row in df.to_dict(orient="records"):
            objs.append(MetricFeature(**row))
        db.bulk_save_objects(objs)
        db.commit()
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=21)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--truncate", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    engine = create_engine(settings.database_url)

    if args.truncate:
        with engine.connect() as conn:
            conn.execute("TRUNCATE TABLE metric_features RESTART IDENTITY")
            conn.commit()

    df = generate_series(args.days, args.seed)
    df = inject_failures(df, args.seed)
    df = add_engineered_features(df)
    insert_rows(df)

    print(f"Inserted {len(df)} rows into metric_features")


if __name__ == "__main__":
    main()
