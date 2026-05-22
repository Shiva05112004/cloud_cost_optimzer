"""Feature engineering and time-series split pipeline."""
from typing import Dict, Tuple

import pandas as pd
from sqlalchemy import create_engine, text

from app.config import get_settings


FEATURE_COLUMNS = [
    "cpu",
    "memory",
    "connections",
    "cpu_velocity",
    "memory_velocity",
    "connections_velocity",
    "rolling_cpu",
    "rolling_memory",
    "rolling_connections",
]


def load_metric_features(limit: int = 50000) -> pd.DataFrame:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    query = text(
        """
        SELECT ts, cpu, memory, connections,
               cpu_velocity, memory_velocity, connections_velocity,
               rolling_cpu, rolling_memory, rolling_connections,
               is_failure_imminent
        FROM metric_features
        ORDER BY ts ASC
        LIMIT :limit
        """
    )
    return pd.read_sql_query(query, engine, params={"limit": limit})


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    df = df.dropna(subset=["ts"]).reset_index(drop=True)

    if df["cpu_velocity"].isna().any():
        df["cpu_velocity"] = df["cpu"].diff().fillna(0.0)
    if df["memory_velocity"].isna().any():
        df["memory_velocity"] = df["memory"].diff().fillna(0.0)
    if df["connections_velocity"].isna().any():
        df["connections_velocity"] = df["connections"].diff().fillna(0.0)

    if df["rolling_cpu"].isna().any():
        df["rolling_cpu"] = df["cpu"].rolling(6, min_periods=1).mean()
    if df["rolling_memory"].isna().any():
        df["rolling_memory"] = df["memory"].rolling(6, min_periods=1).mean()
    if df["rolling_connections"].isna().any():
        df["rolling_connections"] = df["connections"].rolling(6, min_periods=1).mean()

    df = df.fillna(0.0)
    return df


def time_series_split(df: pd.DataFrame, train_ratio: float = 0.8, val_ratio: float = 0.1) -> Dict[str, pd.DataFrame]:
    total = len(df)
    train_end = int(total * train_ratio)
    val_end = int(total * (train_ratio + val_ratio))

    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()

    return {
        "train": train_df,
        "val": val_df,
        "test": test_df,
    }


def build_splits(limit: int = 50000) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    df = load_metric_features(limit=limit)
    df = compute_features(df)
    splits = time_series_split(df)

    def xy(frame: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        X = frame[FEATURE_COLUMNS]
        y = frame["is_failure_imminent"].astype(int)
        return X, y

    X_train, y_train = xy(splits["train"])
    X_val, y_val = xy(splits["val"])
    X_test, y_test = xy(splits["test"])
    return X_train, y_train, X_val, y_val, X_test, y_test
