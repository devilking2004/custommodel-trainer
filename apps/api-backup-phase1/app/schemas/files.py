from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import FileKind


class StoredFileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_id: str | None
    dataset_id: str | None
    kind: FileKind
    original_filename: str
    content_type: str | None
    size_bytes: int
    checksum_sha256: str
    storage_bucket: str
    storage_key: str
    public_url: str | None
    created_at: datetime
