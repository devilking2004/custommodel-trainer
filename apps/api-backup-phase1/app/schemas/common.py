from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str


class TimestampedOut(ORMModel):
    id: str
    created_at: datetime
    updated_at: datetime
