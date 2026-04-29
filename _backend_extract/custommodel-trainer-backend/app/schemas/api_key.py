from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ApiKeyStatus


class ApiKeyCreate(BaseModel):
    name: str = Field(default="Default API key", min_length=2, max_length=120)
    expires_at: datetime | None = None


class ApiKeyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_id: str
    name: str
    key_prefix: str
    status: ApiKeyStatus
    last_used_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime


class ApiKeyCreatedOut(BaseModel):
    api_key: str
    record: ApiKeyOut
