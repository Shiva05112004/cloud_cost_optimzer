"""CLI runner for Phase A ML playground."""
import argparse
import json

from app.ml.phase_a.pipeline import build_splits
from app.ml.phase_a.train import train_models


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=50000)
    parser.add_argument('--output', default='phase_a_report.json')
    args = parser.parse_args()

    X_train, y_train, X_val, y_val, X_test, y_test = build_splits(limit=args.limit)
    report = train_models(X_train, y_train, X_val, y_val, X_test, y_test)

    with open(args.output, 'w', encoding='utf8') as fh:
        json.dump(report, fh, indent=2)

    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
