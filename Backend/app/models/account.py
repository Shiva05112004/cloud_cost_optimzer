from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.database import Base


class CloudAccount(Base):
    __tablename__ = "cloud_accounts"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_name = Column(String, nullable=False)
    role_arn     = Column(String, nullable=False)   # stored as-is for MVP
    provider     = Column(String, default="aws")
    created_at   = Column(DateTime(timezone=True), server_default=func.now())