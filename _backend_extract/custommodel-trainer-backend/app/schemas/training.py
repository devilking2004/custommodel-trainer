from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TrainingJobType, TrainingStatus


class TrainingStartRequest(BaseModel):
    dataset_id: str | None = None
    base_model: str | None = Field(default=None, max_length=160)
    epochs: int = Field(default=1, ge=1, le=10)
    learning_rate: float = Field(default=0.0002, gt=0, le=1)
    notes: str | None = Field(default=None, max_length=2000)


class TrainingJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    model_id: str
    dataset_id: str | None
    job_type: TrainingJobType
    status: TrainingStatus
    progress: int
    current_step: str | None
    rq_job_id: str | None
    logs: list
    error_message: str | None
    training_config: dict
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
