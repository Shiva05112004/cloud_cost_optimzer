"""Train and evaluate Random Forest vs XGBoost for Phase A ML with hyperparameter tuning."""
from typing import Dict, Tuple
import logging

import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_recall_fscore_support,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier

logger = logging.getLogger(__name__)


def _evaluate(model, X: pd.DataFrame, y: pd.Series) -> Dict:
    """Evaluate model with comprehensive metrics."""
    preds = model.predict(X)
    proba = model.predict_proba(X)[:, 1]
    precision, recall, f1, _ = precision_recall_fscore_support(y, preds, average="binary")
    auc = roc_auc_score(y, proba)
    cm = confusion_matrix(y, preds)
    
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(auc),
        "confusion_matrix": cm.tolist(),
        "tn": int(cm[0, 0]),
        "fp": int(cm[0, 1]),
        "fn": int(cm[1, 0]),
        "tp": int(cm[1, 1]),
    }


def _get_feature_importance(model, feature_names: list, top_n: int = 10) -> Dict:
    """Extract feature importance from trained model."""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1][:top_n]
        importance_dict = {
            feature_names[i]: float(importances[i])
            for i in indices
        }
        return importance_dict
    return {}


def train_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    seed: int = 42,
    tune_hyperparams: bool = True,
) -> Tuple[Dict, RandomForestClassifier, XGBClassifier]:
    """
    Train and tune Random Forest and XGBoost models.
    
    Returns:
        (report_dict, best_rf_model, best_xgb_model)
    """
    feature_names = X_train.columns.tolist()
    
    num_healthy = int(np.sum(y_train == 0))
    num_failures = int(np.sum(y_train == 1))
    imbalance_ratio = num_healthy / max(num_failures, 1)
    logger.info(f"Class imbalance ratio: {imbalance_ratio:.2f} : 1")
    print(f"Class imbalance ratio: {imbalance_ratio:.2f} : 1")

    results = {}
    trained_models = {}

    # Random Forest with hyperparameter tuning
    logger.info("Training Random Forest...")
    if tune_hyperparams:
        rf_param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5],
        }
        rf_base = RandomForestClassifier(random_state=seed, n_jobs=-1)
        rf_grid = GridSearchCV(rf_base, rf_param_grid, cv=5, scoring='f1', n_jobs=-1, verbose=1)
        rf_grid.fit(X_train, y_train)
        rf = rf_grid.best_estimator_
        logger.info(f"Best RF params: {rf_grid.best_params_}")
        print(f"Best RF params: {rf_grid.best_params_}")
    else:
        rf = RandomForestClassifier(n_estimators=300, random_state=seed, n_jobs=-1)
        rf.fit(X_train, y_train)

    trained_models['random_forest'] = rf
    rf_importance = _get_feature_importance(rf, feature_names)
    results['random_forest'] = {
        'val': _evaluate(rf, X_val, y_val),
        'test': _evaluate(rf, X_test, y_test),
        'top_features': rf_importance,
    }

    # XGBoost with hyperparameter tuning
    logger.info("Training XGBoost...")
    if tune_hyperparams:
        xgb_param_grid = {
            'max_depth': [5, 6, 7],
            'learning_rate': [0.05, 0.1, 0.15],
            'n_estimators': [100, 200],
        }
        xgb_base = XGBClassifier(
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric='logloss',
            random_state=seed,
            n_jobs=-1,
            scale_pos_weight=imbalance_ratio,
        )
        xgb_grid = GridSearchCV(xgb_base, xgb_param_grid, cv=5, scoring='f1', n_jobs=-1, verbose=1)
        xgb_grid.fit(X_train, y_train)
        xgb = xgb_grid.best_estimator_
        logger.info(f"Best XGB params: {xgb_grid.best_params_}")
        print(f"Best XGB params: {xgb_grid.best_params_}")
    else:
        xgb = XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric='logloss',
            random_state=seed,
            n_jobs=-1,
            scale_pos_weight=imbalance_ratio,
        )
        xgb.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

    trained_models['xgboost'] = xgb
    xgb_importance = _get_feature_importance(xgb, feature_names)
    results['xgboost'] = {
        'val': _evaluate(xgb, X_val, y_val),
        'test': _evaluate(xgb, X_test, y_test),
        'top_features': xgb_importance,
    }

    # Model comparison
    rf_test_f1 = results['random_forest']['test']['f1']
    xgb_test_f1 = results['xgboost']['test']['f1']
    best_model_name = 'xgboost' if xgb_test_f1 > rf_test_f1 else 'random_forest'
    
    report = {
        'results': results,
        'splits': {
            'train': len(X_train),
            'val': len(X_val),
            'test': len(X_test),
        },
        'class_imbalance_ratio': float(imbalance_ratio),
        'best_model': best_model_name,
        'comparison': {
            'rf_test_f1': float(rf_test_f1),
            'xgb_test_f1': float(xgb_test_f1),
            'winner': best_model_name,
        }
    }

    return report, trained_models['random_forest'], trained_models['xgboost']
