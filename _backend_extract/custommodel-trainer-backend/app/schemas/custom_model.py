from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ModelCategory, ModelStatus, ModelVisibility


class CustomModelCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    category: ModelCategory
    visibility: ModelVisibility = ModelVisibility.PRIVATE
    improve_from_feedback: bool = False


class CustomModelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    visibility: ModelVisibility | None = None
    improve_from_feedback: bool | None = None


class CustomModelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    name: str
    slug: str
    description: str | None
    category: ModelCategory
    visibility: ModelVisibility
    status: ModelStatus
    icon_url: str | None
    improve_from_feedback: bool
    readiness_score: int
    current_version_id: str | None
    created_at: datetime
    updated_at: datetime
