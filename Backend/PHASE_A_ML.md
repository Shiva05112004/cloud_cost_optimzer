# Phase A ML Playground

This playground trains and compares **Random Forest** and **XGBoost** using event data from Postgres or a CSV file. It creates a simple label based on a value quantile (default: top 10%).

## Quick Start (DB)

```bash
python scripts/run_phase_a_ml.py \
  --source db \
  --limit 20000 \
  --quantile 0.90 \
  --output phase_a_report.json
```

## Quick Start (CSV)

CSV must include: `event_time`, `value`, `metric_name`, `service`, `resource`

```bash
python scripts/run_phase_a_ml.py \
  --source csv \
  --csv-path path/to/events.csv \
  --quantile 0.90 \
  --output phase_a_report.json
```

## Output

The script prints and writes a JSON report with metrics on the validation split.
