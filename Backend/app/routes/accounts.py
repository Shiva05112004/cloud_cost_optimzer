from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.database import get_db
from app.services.account_service import save_account, get_accounts, verify_account_connection

from app.routes.auth import get_current_user

router = APIRouter()

class ConnectPayload(BaseModel):
    account_name: str
    role_arn: str

@router.post("/connect")
def connect(
    payload: ConnectPayload,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        account = save_account(db, user.id, payload.account_name, payload.role_arn)
        verification = verify_account_connection(payload.role_arn)

        if "error" in verification:
            raise HTTPException(status_code=400, detail=verification["error"])

        return {
            "id": account.id,
            "account_name": account.account_name,
            "status": "connected",
            "aws_account": verification["account"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
def list_accounts(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    accounts = get_accounts(db, user.id)
    return {
        "accounts": [
            {"id": a.id, "name": a.account_name, "provider": a.provider}
            for a in accounts
        ]
    }

@router.get("/status")
def get_connection_status(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Check if user has any connected AWS accounts."""
    accounts = get_accounts(db, user.id)
    has_connected_account = len(accounts) > 0
    
    return {
        "connected": has_connected_account,
        "account_count": len(accounts),
        "accounts": [
            {"id": a.id, "name": a.account_name, "provider": a.provider}
            for a in accounts
        ] if has_connected_account else []
    }


