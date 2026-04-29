from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_owned_model
from app.db.session import get_db
from app.models.custom_model import CustomModel
from app.models.enums import ModelStatus, VersionStatus
from app.models.model_version import ModelVersion
from app.schemas.model_version import ModelVersionOut

router = APIRouter(tags=["versions"])


@router.get("/models/{model_id}/versions", response_model=list[ModelVersionOut])
def list_versions(
    model: CustomModel = Depends(get_owned_model), db: Session = Depends(get_db)
) -> list[ModelVersion]:
    return (
        db.query(ModelVersion)
        .filter(ModelVersion.model_id == model.id)
        .order_by(ModelVersion.version_number.desc())
        .all()
    )


@router.post("/models/{model_id}/versions/{version_id}/rollback", response_model=ModelVersionOut)
def rollback_version(
    version_id: str,
    model: CustomModel = Depends(get_owned_model),
    db: Session = Depends(get_db),
) -> ModelVersion:
    version = (
        db.query(ModelVersion)
        .filter(ModelVersion.id == version_id, ModelVersion.model_id == model.id)
        .first()
    )
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model version not found")

    db.query(ModelVersion).filter(ModelVersion.model_id == model.id).update(
        {"is_active": False, "status": VersionStatus.ARCHIVED}
    )
    version.is_active = True
    version.status = VersionStatus.ACTIVE
    model.current_version_id = version.id
    model.status = ModelStatus.TRAINED
    db.add(version)
    db.add(model)
    db.commit()
    db.refresh(version)
    return version
