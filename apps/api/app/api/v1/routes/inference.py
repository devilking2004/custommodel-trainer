from time import perf_counter
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.model_version import ModelVersion
from app.models.usage_log import UsageLog
from app.schemas.inference import InferenceRequest, InferenceResponse
from app.services.api_keys import validate_api_key_for_model
from app.services.inference import run_model_inference

router = APIRouter(tags=["inference"])


@router.post("/inference/{model_id}", response_model=InferenceResponse)
def run_inference(
    model_id: str,
    payload: InferenceRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> InferenceResponse:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is required",
        )

    api_key, model = validate_api_key_for_model(db, model_id, x_api_key)

    request_id = f"req_{uuid4().hex}"
    start = perf_counter()

    active_version = None

    if model.current_version_id:
        active_version = (
            db.query(ModelVersion)
            .filter(
                ModelVersion.id == model.current_version_id,
                ModelVersion.model_id == model.id,
            )
            .first()
        )

    output = run_model_inference(db, model, active_version, payload.input)

    latency_ms = int((perf_counter() - start) * 1000)
    input_units = max(1, len(payload.input.split()))
    output_units = max(1, len(str(output).split()))

    usage_log = UsageLog(
        owner_id=model.owner_id,
        model_id=model.id,
        model_version_id=active_version.id if active_version else None,
        api_key_id=api_key.id,
        request_id=request_id,
        endpoint=f"/api/v1/inference/{model.id}",
        status_code=200,
        latency_ms=latency_ms,
        input_units=input_units,
        output_units=output_units,
    )

    db.add(usage_log)
    db.commit()

    return InferenceResponse(
        request_id=request_id,
        model_id=model.id,
        model_version_id=active_version.id if active_version else None,
        output=output,
        latency_ms=latency_ms,
        usage={
            "input_units": input_units,
            "output_units": output_units,
            "mode": "dataset_lookup",
        },
    )