from sqlalchemy.orm import Session
from app.models.account import CloudAccount


def save_account(db: Session, user_id: int, account_name: str, role_arn: str) -> CloudAccount:
    account = CloudAccount(
        user_id=user_id,
        account_name=account_name,
        role_arn=role_arn,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_accounts(db: Session, user_id: int) -> list:
    return db.query(CloudAccount).filter(CloudAccount.user_id == user_id).all()