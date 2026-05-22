from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.sql import func
from app.models.database import Base


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('cloud_accounts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    event_time = Column(DateTime(timezone=True), nullable=False)
    metric_name = Column(String, nullable=True)
    value = Column(Float, nullable=True)
    resource = Column(String, nullable=True)
    service = Column(String, nullable=True)
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Index('ix_events_account_time', Event.account_id, Event.event_time)
