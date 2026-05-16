from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_env: str = "development"
    secret_key: str = "changeme"
    database_url: str = "sqlite:///./cloud_optimizer.db"

    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    aws_default_region: str = "ap-south-1"

    ses_sender_email: str = ""
    ses_region: str = "ap-south-1"

    class Config:
        env_file = ".env"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


DATABASE_URL = "sqlite:///./cloud_optimizer.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@lru_cache()
def get_settings() -> Settings:
    return Settings()