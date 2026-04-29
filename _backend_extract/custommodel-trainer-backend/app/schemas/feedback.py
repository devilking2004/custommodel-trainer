from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import FeedbackRating, FeedbackSource, FeedbackStatus


class FeedbackCreate(BaseModel):
    request_id: str | None = Field(default=None, max_length=80)
    source: FeedbackSource = FeedbackSource.PLAYGROUND
    input_payload: dict = Field(default_factory=dict)
    output_payload: dict = Field(default_factory=dict)
    rating: FeedbackRating
    comment: str | None = Field(default=None, max_length=2000)


class FeedbackReview(BaseModel):
    status: FeedbackStatus
    approved_for_training: bool = False


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    model_id: str
    model_version_id: str | None
    request_id: str | None
    source: FeedbackSource
    input_payload: dict
    output_payload: dict
    rating: FeedbackRating
    comment: str | None
    status: FeedbackStatus
    approved_for_training: bool
    reviewed_at: datetime | None
    reviewed_by_id: str | None
    created_at: datetime
    updated_at: datetime
