from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.cloud_api.cost_explorer_client import get_daily_cost_history
from app.models.anomaly_event import AnomalyEvent, FalsePositivePattern
from app.models.database import SessionLocal
from app.models.account import CloudAccount
from app.ml.seasonal_anomaly_detector import build_features, SeasonalAnomalyDetector


def analyze_account_anomalies(account_id: int, days: int = 30) -> Dict:
    db: Session = SessionLocal()
    try:
        account = db.get(CloudAccount, account_id)
        if account is None:
            return {"status": "missing", "account_id": account_id}

        # Fetch daily costs for the account
        daily = get_daily_cost_history(role_arn=account.role_arn, days=days)
        if not daily:
            return {"status": "no_data", "account_id": account_id}

        X, dates, df = build_features(daily)
        detector = SeasonalAnomalyDetector()
        detector.fit(X, df)

        # analyze the most recent day
        last_x = X[-1]
        last_date = dates[-1]
        dow = int(df['day_of_week'].iloc[-1])
        result = detector.predict_single(last_x, day_of_week=dow)

        # check false positive patterns
        bucket = result.get('magnitude_bucket')
        patterns = (
            db.query(FalsePositivePattern)
            .filter(FalsePositivePattern.account_id == account_id)
            .filter(FalsePositivePattern.day_of_week == dow)
            .filter(FalsePositivePattern.magnitude_bucket == bucket)
            .all()
        )
        if patterns:
            result['is_false_positive_pattern'] = True
            result['is_anomaly'] = False

        # persist anomaly event if detected
        if result.get('is_anomaly'):
            evt = AnomalyEvent(
                account_id=account_id,
                cost_date=datetime.strptime(last_date, '%Y-%m-%d').date(),
                service=None,
                cost_value=float(last_x[0]),
                expected_low=result.get('expected_low'),
                expected_high=result.get('expected_high'),
                deviation_pct=result.get('deviation_pct') or 0.0,
                reason=result.get('reason') or '',
            )
            db.add(evt)
            db.commit()
            db.refresh(evt)
            result['persisted_id'] = evt.id

        return {"status": "ok", "account_id": account_id, "result": result}
    finally:
        db.close()


def mark_false_positive(anomaly_id: int, account_id: int, service: Optional[str] = None) -> Dict:
    db: Session = SessionLocal()
    try:
        evt = db.get(AnomalyEvent, anomaly_id)
        if evt is None or evt.account_id != account_id:
            return {"status": "not_found"}

        evt.is_false_positive = True
        db.add(evt)

        # create a false-positive pattern from event
        dow = evt.cost_date.weekday()
        bucket = None
        try:
            from app.ml.seasonal_anomaly_detector import magnitude_bucket

            bucket = magnitude_bucket(evt.cost_value)
        except Exception:
            bucket = None

        pattern = FalsePositivePattern(
            account_id=account_id,
            service=service,
            day_of_week=dow,
            magnitude_bucket=bucket,
        )
        db.add(pattern)
        db.commit()
        return {"status": "recorded", "pattern_id": pattern.id}
    finally:
        db.close()
