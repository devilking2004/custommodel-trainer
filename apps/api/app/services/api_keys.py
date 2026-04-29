from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_api_key
from app.models.api_key import ApiKey
from app.models.custom_model import CustomModel
from app.models.enums import ApiKeyStatus


def validate_api_key_for_model(db: Session, model_id: str, raw_api_key: str) -> tuple[ApiKey, CustomModel]:
    key_hash = hash_api_key(raw_api_key)
    api_key = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()
    if not api_key or api_key.model_id != model_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    if api_key.status != ApiKeyStatus.ACTIVE or api_key.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key has been revoked")
    if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key has expired")
    model = db.query(CustomModel).filter(CustomModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    api_key.last_used_at = datetime.now(timezone.utc)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key, model
