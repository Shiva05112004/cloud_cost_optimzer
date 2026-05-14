from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.database import Base


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("cloud_accounts.id"))
    resource_id = Column(String)
    resource_type = Column(String, default="ec2")
    issue = Column(String)
    action = Column(String)
    current_cost = Column(Float, default=0.0)
    recommended_type = Column(String, nullable=True)
    estimated_savings = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    risk = Column(String, default="low")
    priority_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())