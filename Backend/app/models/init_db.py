"""
Run this once to create all SQLite tables.
Usage: python -m app.models.init_db
"""
from app.models.database import engine, Base
import app.models.user           # noqa: F401 — registers User table
import app.models.account        # noqa: F401 — registers CloudAccount table
import app.models.recommendation # noqa: F401 — registers RecommendationLog table
import app.models.anomaly_event  # noqa: F401 — registers AnomalyEvent + patterns
import app.models.event          # noqa: F401 — registers Event table
import app.models.metric_features  # noqa: F401 — registers MetricFeature table


def init():
    Base.metadata.create_all(bind=engine)
    print("SQLite tables created at ./cloud_optimizer.db")


if __name__ == "__main__":
    init()