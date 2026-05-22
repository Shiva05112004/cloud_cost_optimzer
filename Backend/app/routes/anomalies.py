from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.account import CloudAccount
from app.models.anomaly_event import AnomalyEvent
from app.routes.auth import get_current_user
from app.services.anomaly_service import analyze_account_anomalies, mark_false_positive

router = APIRouter()


@router.get("/")
def list_anomalies(db: Session = Depends(get_db), user=Depends(get_current_user)):
    accounts = db.query(CloudAccount.id).filter(CloudAccount.user_id == user.id).all()
    account_ids = [a[0] for a in accounts]
    if not account_ids:
        return {"anomalies": []}

    rows = (
        db.query(AnomalyEvent)
        .filter(AnomalyEvent.account_id.in_(account_ids))
        .order_by(AnomalyEvent.created_at.desc())
        .limit(100)
        .all()
    )

    return {"anomalies": [
        {
            "id": r.id,
            "account_id": r.account_id,
            "cost_date": r.cost_date.isoformat(),
            "cost_value": r.cost_value,
            "expected_low": r.expected_low,
            "expected_high": r.expected_high,
            "deviation_pct": r.deviation_pct,
            "reason": r.reason,
            "is_false_positive": r.is_false_positive,
        }
        for r in rows
    ]}


@router.post("/{anomaly_id}/false-positive")
def post_false_positive(anomaly_id: int, user=Depends(get_current_user)):
    # mark anomaly as false positive and record pattern
    # ensure user owns the account for the anomaly
    res = mark_false_positive(anomaly_id, user.id)
    if res.get('status') == 'not_found':
        raise HTTPException(status_code=404, detail='Anomaly not found')
    return res


@router.post("/refresh/{account_id}")
def refresh_account(account_id: int, user=Depends(get_current_user)):
    # enqueue background analysis for a specific account
    # simple synchronous run for now
    return analyze_account_anomalies(account_id)
