from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UsageLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    model_id: str
    model_version_id: str | None
    api_key_id: str | None
    request_id: str
    endpoint: str
    status_code: int
    latency_ms: int
    input_units: int
    output_units: int
    error_message: str | None
    created_at: datetime
