"""Train and evaluate Random Forest vs XGBoost for Phase A ML."""
from typing import Dict, Tuple

import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier


def _evaluate(model, X: pd.DataFrame, y: pd.Series) -> Dict:
    preds = model.predict(X)
    proba = model.predict_proba(X)[:, 1]
    precision, recall, f1, _ = precision_recall_fscore_support(y, preds, average="binary")
    auc = roc_auc_score(y, proba)
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(auc),
    }


def train_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    seed: int = 42,
) -> Dict:
    rf = Pipeline(
        [
            ("clf", RandomForestClassifier(n_estimators=300, random_state=seed, n_jobs=-1)),
        ]
    )

    xgb = Pipeline(
        [
            ("clf", XGBClassifier(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.9,
                colsample_bytree=0.9,
                eval_metric="logloss",
                random_state=seed,
                n_jobs=-1,
            )),
        ]
    )

    results = {}
    for name, model in [("random_forest", rf), ("xgboost", xgb)]:
        model.fit(X_train, y_train)
        results[name] = {
            "val": _evaluate(model, X_val, y_val),
            "test": _evaluate(model, X_test, y_test),
        }

    return {
        "results": results,
        "splits": {
            "train": len(X_train),
            "val": len(X_val),
            "test": len(X_test),
        },
    }
