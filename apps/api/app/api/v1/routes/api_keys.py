from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_owned_model
from app.core.security import generate_api_key
from app.db.session import get_db
from app.models.api_key import ApiKey
from app.models.custom_model import CustomModel
from app.models.enums import ApiKeyStatus
from app.models.user import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreatedOut, ApiKeyOut

router = APIRouter(tags=["api-keys"])


@router.post("/models/{model_id}/api-keys", response_model=ApiKeyCreatedOut, status_code=status.HTTP_201_CREATED)
def create_model_api_key(
    payload: ApiKeyCreate,
    model: CustomModel = Depends(get_owned_model),
    db: Session = Depends(get_db),
) -> ApiKeyCreatedOut:
    raw_key, prefix, key_hash = generate_api_key()
    record = ApiKey(
        owner_id=model.owner_id,
        model_id=model.id,
        name=payload.name,
        key_prefix=prefix,
        key_hash=key_hash,
        expires_at=payload.expires_at,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return ApiKeyCreatedOut(api_key=raw_key, record=record)


@router.get("/models/{model_id}/api-keys", response_model=list[ApiKeyOut])
def list_model_api_keys(
    model: CustomModel = Depends(get_owned_model), db: Session = Depends(get_db)
) -> list[ApiKey]:
    return (
        db.query(ApiKey)
        .filter(ApiKey.model_id == model.id)
        .order_by(ApiKey.created_at.desc())
        .all()
    )


@router.delete("/api-keys/{api_key_id}", response_model=ApiKeyOut)
def revoke_api_key(
    api_key_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiKey:
    record = db.query(ApiKey).filter(ApiKey.id == api_key_id, ApiKey.owner_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    record.status = ApiKeyStatus.REVOKED
    record.revoked_at = datetime.now(timezone.utc)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
