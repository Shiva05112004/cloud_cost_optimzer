from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "cloud_cost_optimizer",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)

celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    beat_schedule={
        "refresh-recommendations-every-6-hours": {
            "task": "app.tasks.refresh_all_recommendations",
            "schedule": crontab(minute=0, hour="*/6"),
        },
    },
)
