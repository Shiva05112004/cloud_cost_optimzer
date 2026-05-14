from typing import List

import logging
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.cloud_api.cloudwatch_client import get_avg_cpu
from app.cloud_api.ec2_client import list_ec2_instances
from app.ml.rightsizer import suggest_rightsizing
from app.models.account import CloudAccount
from app.models.database import SessionLocal
from app.models.recommendation import RecommendationLog
from app.services.optimizer_service import priority_score

logger = logging.getLogger(__name__)


def build_recommendations(role_arn: str | None = None) -> List[dict]:
    instances = list_ec2_instances(role_arn)
    recommendations = []

    for inst in instances:
        if inst["state"] != "running":
            continue

        avg_cpu = get_avg_cpu(inst["instance_id"], days=7, role_arn=role_arn)
        rec = suggest_rightsizing(inst["instance_id"], inst["instance_type"], avg_cpu)

        if rec["action"] != "No action needed":
            rec["priority_score"] = priority_score(
                rec["estimated_savings"],
                rec["confidence"],
                rec["risk"],
            )
            recommendations.append(rec)

    return sorted(recommendations, key=lambda recommendation: recommendation["priority_score"], reverse=True)


def _persist_recommendations(db: Session, account_id: int, recommendations: List[dict]) -> None:
    db.query(RecommendationLog).filter(RecommendationLog.account_id == account_id).delete(synchronize_session=False)

    for recommendation in recommendations:
        db.add(
            RecommendationLog(
                account_id=account_id,
                resource_id=recommendation["instance_id"],
                resource_type="ec2",
                issue=recommendation["issue"],
                action=recommendation["action"],
                current_cost=recommendation.get("current_cost", 0.0),
                recommended_type=recommendation.get("recommended_type"),
                estimated_savings=recommendation["estimated_savings"],
                confidence=recommendation["confidence"],
                risk=recommendation["risk"],
                priority_score=recommendation["priority_score"],
            )
        )

    db.commit()


def _refresh_account(db: Session, account: CloudAccount) -> dict:
    recommendations = build_recommendations(account.role_arn)
    _persist_recommendations(db, account.id, recommendations)

    return {
        "account_id": account.id,
        "account_name": account.account_name,
        "count": len(recommendations),
    }


@celery_app.task(name="app.tasks.refresh_account_recommendations")
def refresh_account_recommendations(account_id: int) -> dict:
    db = SessionLocal()
    try:
        account = db.get(CloudAccount, account_id)
        if account is None:
            return {"account_id": account_id, "status": "missing"}

        payload = _refresh_account(db, account)
        payload["status"] = "refreshed"
        return payload
    finally:
        db.close()


@celery_app.task(name="app.tasks.refresh_user_recommendations")
def refresh_user_recommendations(user_id: int) -> dict:
    db = SessionLocal()
    try:
        accounts = db.query(CloudAccount).filter(CloudAccount.user_id == user_id).all()
        refreshed_accounts = []

        for account in accounts:
            refreshed_accounts.append(_refresh_account(db, account))

        return {
            "user_id": user_id,
            "status": "refreshed",
            "accounts": len(refreshed_accounts),
            "recommendations": sum(account["count"] for account in refreshed_accounts),
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.refresh_all_recommendations")
def refresh_all_recommendations() -> dict:
    db = SessionLocal()
    try:
        accounts = db.query(CloudAccount).all()
        refreshed_accounts = []

        for account in accounts:
            refreshed_accounts.append(_refresh_account(db, account))

        return {
            "status": "refreshed",
            "accounts": len(refreshed_accounts),
            "recommendations": sum(account["count"] for account in refreshed_accounts),
        }
    finally:
        db.close()
