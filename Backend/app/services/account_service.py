from sqlalchemy.orm import Session
import logging

from app.models.account import CloudAccount

logger = logging.getLogger(__name__)


def save_account(db: Session, user_id: int, account_name: str, role_arn: str) -> CloudAccount:
    """Save a cloud account after validating the role ARN format.

    Performs a DB rollback on failure to avoid partial commits.
    """
    # Basic validation for ARN format
    if not isinstance(role_arn, str) or not role_arn.startswith("arn:"):
        raise ValueError("Invalid role ARN format")

    account = CloudAccount(
        user_id=user_id,
        account_name=account_name,
        role_arn=role_arn,
    )
    try:
        db.add(account)
        db.commit()
        db.refresh(account)
        return account
    except Exception as e:
        logger.error(f"Failed to save account {account_name} for user {user_id}: {e}")
        db.rollback()
        raise


def get_accounts(db: Session, user_id: int) -> list:
    return db.query(CloudAccount).filter(CloudAccount.user_id == user_id).all()