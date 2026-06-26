from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict   


class Settings(BaseSettings):
    app_env: str = "development"
    secret_key: str = "changeme"
    database_url: str = "sqlite:///./cloud_optimizer.db"

    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_default_region: str = "eu-north-1"

    ses_sender_email: str = ""
    ses_region: str = "eu-north-1"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # class Config:
    #     env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
     settings = Settings()
     settings.aws_default_region = "eu-north-1"
     return settings