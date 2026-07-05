from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.account import CloudAccount
from app.models.database import get_db
from app.models.recommendation import RecommendationLog
from app.routes.auth import get_current_user
from app.tasks import refresh_user_recommendations

router = APIRouter()


@router.get("/")
def get_recommendations(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Returns the latest cached recommendations for the authenticated user.
    The heavy AWS collection runs in Celery, so this endpoint stays fast.
    """
    account_ids = [row[0] for row in db.query(CloudAccount.id).filter(CloudAccount.user_id == user.id).all()]

    if not account_ids:
        return {
            "count": 0,
            "total_potential_savings": 0.0,
            "recommendations": [],
        }

    rows = (
        db.query(RecommendationLog)
        .filter(RecommendationLog.account_id.in_(account_ids))
        .order_by(RecommendationLog.priority_score.desc(), RecommendationLog.created_at.desc())
        .all()
    )

    recommendations = [
        {
            "instance_id": row.resource_id,
            "issue": row.issue,
            "action": row.action,
            "current_cost": round(row.current_cost or 0.0, 2),
            "estimated_savings": round(row.estimated_savings or 0.0, 2),
            "recommended_type": row.recommended_type,
            "confidence": round(row.confidence or 0.0, 2),
            "risk": row.risk,
            "priority_score": round(row.priority_score or 0.0, 2),
        }
        for row in rows
    ]
    total_savings = sum(recommendation["estimated_savings"] for recommendation in recommendations)

    return {
        "count": len(recommendations),
        "total_potential_savings": round(total_savings, 2),
        "recommendations": recommendations,
    }


@router.post("/refresh")
def refresh_recommendations(
    user=Depends(get_current_user),
):
    """
    Queue a background refresh for the authenticated user's cloud accounts.
    """
    task = refresh_user_recommendations.delay(user.id)
    return {"status": "queued", "task_id": task.id}
