"""Model persistence and loading for Phase A ML."""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional

import joblib
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

logger = logging.getLogger(__name__)

# Default model directory
MODEL_DIR = Path(__file__).parent.parent.parent / "models" / "phase_a"


def ensure_model_dir():
    """Create model directory if it doesn't exist."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)


def save_models(
    rf_model: RandomForestClassifier,
    xgb_model: XGBClassifier,
    report: Dict,
    feature_names: list,
) -> Dict[str, str]:
    """
    Save trained models and metadata.
    
    Returns:
        {
            'rf_model_path': '...',
            'xgb_model_path': '...',
            'metadata_path': '...',
        }
    """
    ensure_model_dir()
    timestamp = datetime.utcnow().isoformat()
    
    # Save models
    rf_path = MODEL_DIR / f"rf_model_{timestamp}.joblib"
    xgb_path = MODEL_DIR / f"xgb_model_{timestamp}.joblib"
    
    joblib.dump(rf_model, rf_path)
    joblib.dump(xgb_model, xgb_path)
    logger.info(f"Saved RF model to {rf_path}")
    logger.info(f"Saved XGB model to {xgb_path}")
    
    # Save metadata
    metadata = {
        'timestamp': timestamp,
        'rf_model_path': str(rf_path),
        'xgb_model_path': str(xgb_path),
        'feature_names': feature_names,
        'best_model': report.get('best_model'),
        'rf_test_f1': report['results']['random_forest']['test']['f1'],
        'xgb_test_f1': report['results']['xgboost']['test']['f1'],
        'class_imbalance_ratio': report.get('class_imbalance_ratio'),
    }
    
    metadata_path = MODEL_DIR / f"metadata_{timestamp}.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved metadata to {metadata_path}")
    
    # Create/update symlinks to latest models
    latest_rf = MODEL_DIR / "rf_model_latest.joblib"
    latest_xgb = MODEL_DIR / "xgb_model_latest.joblib"
    latest_metadata = MODEL_DIR / "metadata_latest.json"
    
    for old_link in [latest_rf, latest_xgb, latest_metadata]:
        if old_link.exists():
            old_link.unlink()
    
    latest_rf.symlink_to(rf_path.name)
    latest_xgb.symlink_to(xgb_path.name)
    latest_metadata.symlink_to(metadata_path.name)
    
    return {
        'rf_model_path': str(rf_path),
        'xgb_model_path': str(xgb_path),
        'metadata_path': str(metadata_path),
    }


def load_latest_models() -> Tuple[Optional[RandomForestClassifier], Optional[XGBClassifier], Optional[Dict]]:
    """
    Load the latest trained models and metadata.
    
    Returns:
        (rf_model, xgb_model, metadata) or (None, None, None) if not found
    """
    ensure_model_dir()
    
    latest_rf_path = MODEL_DIR / "rf_model_latest.joblib"
    latest_xgb_path = MODEL_DIR / "xgb_model_latest.joblib"
    latest_metadata_path = MODEL_DIR / "metadata_latest.json"
    
    if not latest_rf_path.exists() or not latest_xgb_path.exists():
        logger.warning("Latest models not found in model directory")
        return None, None, None
    
    try:
        rf_model = joblib.load(latest_rf_path)
        xgb_model = joblib.load(latest_xgb_path)
        
        metadata = None
        if latest_metadata_path.exists():
            with open(latest_metadata_path) as f:
                metadata = json.load(f)
        
        logger.info(f"Loaded models from {latest_rf_path} and {latest_xgb_path}")
        return rf_model, xgb_model, metadata
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        return None, None, None


def load_model_by_timestamp(timestamp: str) -> Tuple[Optional[RandomForestClassifier], Optional[XGBClassifier], Optional[Dict]]:
    """Load models from a specific timestamp."""
    ensure_model_dir()
    
    rf_path = MODEL_DIR / f"rf_model_{timestamp}.joblib"
    xgb_path = MODEL_DIR / f"xgb_model_{timestamp}.joblib"
    metadata_path = MODEL_DIR / f"metadata_{timestamp}.json"
    
    if not rf_path.exists() or not xgb_path.exists():
        logger.warning(f"Models for timestamp {timestamp} not found")
        return None, None, None
    
    try:
        rf_model = joblib.load(rf_path)
        xgb_model = joblib.load(xgb_path)
        
        metadata = None
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)
        
        return rf_model, xgb_model, metadata
    except Exception as e:
        logger.error(f"Failed to load models for timestamp {timestamp}: {e}")
        return None, None, None


def list_available_models() -> list:
    """List all available model timestamps."""
    ensure_model_dir()
    
    metadata_files = list(MODEL_DIR.glob("metadata_*.json"))
    timestamps = []
    
    for mf in metadata_files:
        if "latest" in mf.name:
            continue
        try:
            with open(mf) as f:
                meta = json.load(f)
                timestamps.append({
                    'timestamp': meta.get('timestamp'),
                    'rf_f1': meta.get('rf_test_f1'),
                    'xgb_f1': meta.get('xgb_test_f1'),
                    'best_model': meta.get('best_model'),
                })
        except Exception as e:
            logger.warning(f"Could not read metadata from {mf}: {e}")
    
    return sorted(timestamps, key=lambda x: x['timestamp'], reverse=True)
