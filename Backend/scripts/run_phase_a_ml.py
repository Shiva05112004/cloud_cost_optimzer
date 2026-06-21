"""CLI runner for Phase A ML playground."""
import argparse
import json
import logging

from app.ml.phase_a.pipeline import build_splits
from app.ml.phase_a.train import train_models
from app.ml.phase_a.model_persistence import save_models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase A ML: Train and evaluate models")
    parser.add_argument('--limit', type=int, default=50000, help='Max records to load from DB')
    parser.add_argument('--output', default='phase_a_report.json', help='Output report path')
    parser.add_argument('--no-tune', action='store_true', help='Skip hyperparameter tuning')
    args = parser.parse_args()

    logger.info("Starting Phase A ML training...")
    
    try:
        # Load and prepare data
        logger.info(f"Loading up to {args.limit} records...")
        X_train, y_train, X_val, y_val, X_test, y_test, quality_report = build_splits(limit=args.limit)
        
        # Train models with optional hyperparameter tuning
        logger.info(f"Training models (tune_hyperparams={not args.no_tune})...")
        report, rf_model, xgb_model = train_models(
            X_train, y_train, X_val, y_val, X_test, y_test,
            tune_hyperparams=not args.no_tune
        )
        
        # Include quality report in final report
        report['data_quality'] = quality_report
        
        # Save models to disk
        logger.info("Saving models to disk...")
        save_result = save_models(rf_model, xgb_model, report, X_train.columns.tolist())
        report['model_paths'] = save_result
        
        # Save full report to JSON
        with open(args.output, 'w', encoding='utf8') as fh:
            json.dump(report, fh, indent=2)
        
        logger.info(f"Report saved to {args.output}")
        print(json.dumps(report, indent=2))
        
    except Exception as e:
        logger.error(f"Phase A ML training failed: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
