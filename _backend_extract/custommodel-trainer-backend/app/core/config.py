from functools import lru_cache
from typing import Annotated

from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_csv(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        return value
    return [item.strip() for item in value.split(",") if item.strip()]


CsvList = Annotated[list[str], BeforeValidator(_split_csv)]


class Settings(BaseSettings):
    app_name: str = "CustomModel Trainer API"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: CsvList = Field(default_factory=lambda: ["http://localhost:3000"])

    api_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    api_key_pepper: str = "dev-api-key-pepper-change-me"

    database_url: str = "sqlite:///./custommodel.db"
    redis_url: str = "redis://localhost:6379/0"
    rq_queue_name: str = "custommodel-training"

    s3_endpoint_url: str | None = "http://localhost:9000"
    s3_public_base_url: str | None = "http://localhost:9000"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_bucket_name: str = "custommodel-trainer"
    s3_region: str = "us-east-1"
    s3_use_ssl: bool = False

    max_upload_mb: int = 100
    max_icon_mb: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
