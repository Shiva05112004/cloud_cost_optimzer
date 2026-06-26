from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.services.optimizer_service import run_optimization
from app.routes.auth import get_current_user  
        # ← from auth, not utils

router = APIRouter()


@router.get("/")
def get_recommendations(
    role_arn: Optional[str] = Query(None),
    _user=Depends(get_current_user),                  # enforces JWT auth
):
    """
    Returns ranked cost optimization recommendations.
    Pass ?role_arn=arn:aws:iam::... to use IAM role access.
    """
    results = run_optimization(role_arn)
    total_savings = sum(r.get("estimated_savings", 0.0) for r in results)

    return {
        "count": len(results),
        "total_potential_savings": round(total_savings, 2),
        "recommendations": results,
    }