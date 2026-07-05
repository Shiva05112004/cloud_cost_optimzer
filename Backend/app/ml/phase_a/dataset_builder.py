"""Build a labeled dataset from events or CSV for Phase A ML."""
from typing import Optional, Tuple

import pandas as pd
from sqlalchemy import create_engine, text

from app.config import get_settings


def load_events_from_db(limit: int = 20000) -> pd.DataFrame:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    query = text(
        """
        SELECT event_time, metric_name, value, resource, service
        FROM events
        WHERE value IS NOT NULL
        ORDER BY event_time DESC
        LIMIT :limit
        """
    )
    return pd.read_sql_query(query, engine, params={"limit": limit})


def load_events_from_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce")
    df = df.dropna(subset=["event_time", "value"]).reset_index(drop=True)
    df["hour"] = df["event_time"].dt.hour
    df["day_of_week"] = df["event_time"].dt.weekday
    return df


def label_by_quantile(df: pd.DataFrame, quantile: float = 0.90) -> pd.DataFrame:
    df = df.copy()
    threshold = df["value"].quantile(quantile)
    df["label"] = (df["value"] >= threshold).astype(int)
    return df


def build_dataset(
    source: str = "db",
    csv_path: Optional[str] = None,
    limit: int = 20000,
    quantile: float = 0.90,
) -> pd.DataFrame:
    if source == "csv":
        if not csv_path:
            raise ValueError("csv_path is required when source='csv'")
        df = load_events_from_csv(csv_path)
    else:
        df = load_events_from_db(limit=limit)

    df = add_time_features(df)
    df = label_by_quantile(df, quantile=quantile)
    return df


def split_features_labels(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    features = df[["value", "hour", "day_of_week", "metric_name", "service", "resource"]].copy()
    labels = df["label"].astype(int)
    return features, labels
