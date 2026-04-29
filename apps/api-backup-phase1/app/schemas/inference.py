from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    input: str = Field(min_length=1, max_length=12000)
    parameters: dict = Field(default_factory=dict)


class InferenceResponse(BaseModel):
    request_id: str
    model_id: str
    model_version_id: str | None
    output: str | dict
    latency_ms: int
    usage: dict
