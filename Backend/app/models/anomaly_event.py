from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.sql import func
from app.models.database import Base


class AnomalyEvent(Base):
    __tablename__ = 'anomaly_events'

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('cloud_accounts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    cost_date = Column(Date, nullable=False)
    service = Column(String, nullable=True)
    cost_value = Column(Float, default=0.0)
    expected_low = Column(Float, nullable=True)
    expected_high = Column(Float, nullable=True)
    deviation_pct = Column(Float, default=0.0)
    reason = Column(String, default='')
    is_false_positive = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FalsePositivePattern(Base):
    __tablename__ = 'false_positive_patterns'

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('cloud_accounts.id'), nullable=False)
    service = Column(String, nullable=True)
    day_of_week = Column(Integer, nullable=True)
    magnitude_bucket = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
