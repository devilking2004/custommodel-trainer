from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DatasetStatus, IssueSeverity
from app.schemas.files import StoredFileOut


class DatasetCreate(BaseModel):
    name: str = Field(default="Training dataset", min_length=2, max_length=160)


class DataIssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    severity: IssueSeverity
    code: str
    message: str
    row_number: int | None
    field: str | None
    details: dict
    created_at: datetime


class DatasetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    model_id: str
    name: str
    status: DatasetStatus
    readiness_score: int
    row_count: int
    valid_count: int
    invalid_count: int
    issue_summary: dict
    dataset_metadata: dict
    created_at: datetime
    updated_at: datetime


class DatasetDetailOut(DatasetOut):
    files: list[StoredFileOut] = []
    issues: list[DataIssueOut] = []


class DatasetValidationOut(BaseModel):
    dataset: DatasetOut
    issues: list[DataIssueOut]
