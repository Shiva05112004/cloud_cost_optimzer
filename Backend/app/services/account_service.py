import boto3
from botocore.exceptions import ClientError
from sqlalchemy.orm import Session
import logging
from app.models.account import CloudAccount
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def save_account(db: Session, user_id: int, account_name: str, role_arn: str) -> CloudAccount:
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

        # 🔎 Verify AWS connectivity
        verify_account_connection(role_arn)

        return account
    except Exception as e:
        logger.error(f"Failed to save account {account_name} for user {user_id}: {e}")
        db.rollback()
        raise

def verify_account_connection(role_arn: str) -> dict:
    """Try to assume the role and log AWS account identity."""
    sts = boto3.client(
        "sts",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_default_region,
    )
    try:
        response = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName="CloudCostVerifier"
        )
        creds = response["Credentials"]
        assumed = boto3.client(
            "sts",
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )
        identity = assumed.get_caller_identity()
        logger.info(f"Verified AWS account {identity['Account']} for role {role_arn}")
        return {"account": identity['Account']}
    except ClientError as e:
        logger.error(f"Failed to verify AWS account {role_arn}: {e}")
        return {"error": str(e)}

def get_accounts(db: Session, user_id: int) -> list:
    return db.query(CloudAccount).filter(CloudAccount.user_id == user_id).all()
