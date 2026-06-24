from sqlalchemy import Column, Integer, Float, Boolean, DateTime, Index
from sqlalchemy.sql import func

from app.models.database import Base


class MetricFeature(Base):
    __tablename__ = "metric_features"

    id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime(timezone=True), nullable=False, index=True)

    cpu = Column(Float, nullable=False)
    memory = Column(Float, nullable=False)
    connections = Column(Float, nullable=False)

    cpu_velocity = Column(Float, nullable=True)
    memory_velocity = Column(Float, nullable=True)
    connections_velocity = Column(Float, nullable=True)

    rolling_cpu = Column(Float, nullable=True)
    rolling_memory = Column(Float, nullable=True)
    rolling_connections = Column(Float, nullable=True)

    is_failure_imminent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Index("ix_metric_features_ts", MetricFeature.ts)
