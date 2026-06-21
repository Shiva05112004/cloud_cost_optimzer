"""Feature engineering and time-series split pipeline with data quality validation."""
from typing import Dict, Tuple
import logging

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

from app.config import get_settings

logger = logging.getLogger(__name__)

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
    """Load metric features from database."""
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
    df = pd.read_sql_query(query, engine, params={"limit": limit})
    logger.info(f"Loaded {len(df)} records from metric_features table")
    return df


def validate_data_quality(df: pd.DataFrame) -> Dict:
    """Validate data quality and return report."""
    quality_report = {
        'total_rows': len(df),
        'null_counts': df.isnull().sum().to_dict(),
        'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
        'feature_stats': {},
    }
    
    # Feature statistics
    for col in FEATURE_COLUMNS:
        if col in df.columns:
            quality_report['feature_stats'][col] = {
                'min': float(df[col].min()) if len(df) > 0 else None,
                'max': float(df[col].max()) if len(df) > 0 else None,
                'mean': float(df[col].mean()) if len(df) > 0 else None,
                'std': float(df[col].std()) if len(df) > 0 else None,
            }
    
    # Class distribution
    if 'is_failure_imminent' in df.columns:
        class_dist = df['is_failure_imminent'].value_counts()
        quality_report['class_distribution'] = class_dist.to_dict()
        quality_report['class_imbalance_ratio'] = float(class_dist.get(0, 0) / max(class_dist.get(1, 1), 1))
    
    # Log warnings for data quality issues
    for col in FEATURE_COLUMNS:
        if col in df.columns:
            null_pct = quality_report['missing_percentage'].get(col, 0)
            if null_pct > 10:
                logger.warning(f"Feature {col} has {null_pct:.1f}% missing values")
    
    logger.info(f"Data quality report: {quality_report}")
    return quality_report


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute and impute features."""
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
    """Split data into train, validation, and test sets using time-series ordering."""
    total = len(df)
    train_end = int(total * train_ratio)
    val_end = int(total * (train_ratio + val_ratio))

    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()
    
    logger.info(f"Time-series split: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")

    return {
        "train": train_df,
        "val": val_df,
        "test": test_df,
    }


def build_splits(limit: int = 50000) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, Dict]:
    """
    Build train/val/test splits with data quality validation.
    
    Returns:
        (X_train, y_train, X_val, y_val, X_test, y_test, quality_report)
    """
    logger.info("Building splits for Phase A ML...")
    
    df = load_metric_features(limit=limit)
    
    # Validate data quality before processing
    quality_report = validate_data_quality(df)
    
    if len(df) < 100:
        raise ValueError(f"Insufficient data: only {len(df)} records available, need at least 100")
    
    df = compute_features(df)
    splits = time_series_split(df)

    def xy(frame: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        X = frame[FEATURE_COLUMNS]
        y = frame["is_failure_imminent"].astype(int)
        return X, y

    X_train, y_train = xy(splits["train"])
    X_val, y_val = xy(splits["val"])
    X_test, y_test = xy(splits["test"])
    
    logger.info(f"Final splits: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")
    
    return X_train, y_train, X_val, y_val, X_test, y_test, quality_report
