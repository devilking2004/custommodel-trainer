from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import VersionStatus


class ModelVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    model_id: str
    training_job_id: str | None
    version_number: int
    name: str
    status: VersionStatus
    is_active: bool
    base_model: str | None
    artifact_file_id: str | None
    artifact_storage_key: str | None
    metrics: dict
    notes: str | None
    created_at: datetime
    updated_at: datetime
