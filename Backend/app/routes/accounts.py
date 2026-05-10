from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.database import get_db
from app.services.account_service import save_account, get_accounts
from app.routes.auth import get_current_user          # ← from auth, not utils

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
    account = save_account(db, user.id, payload.account_name, payload.role_arn)
    return {
        "id": account.id,
        "account_name": account.account_name,
        "status": "connected",
    }


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