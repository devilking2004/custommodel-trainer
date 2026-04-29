from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_owned_dataset, get_owned_model
from app.core.config import get_settings
from app.db.session import get_db
from app.models.custom_model import CustomModel
from app.models.dataset import Dataset
from app.models.enums import DatasetStatus, FileKind, ModelCategory
from app.models.stored_file import StoredFile
from app.models.user import User
from app.schemas.dataset import DatasetCreate, DatasetDetailOut, DatasetOut, DatasetValidationOut
from app.schemas.files import StoredFileOut
from app.services.dataset_validation import validate_dataset
from app.services.image_validation import ALLOWED_IMAGE_MIME_TYPES, validate_image_bytes
from app.services.storage import read_upload_file, upload_bytes

router = APIRouter(tags=["datasets"])


@router.post("/models/{model_id}/datasets", response_model=DatasetOut, status_code=status.HTTP_201_CREATED)
def create_dataset(
    payload: DatasetCreate,
    model: CustomModel = Depends(get_owned_model),
    db: Session = Depends(get_db),
) -> Dataset:
    dataset = Dataset(owner_id=model.owner_id, model_id=model.id, name=payload.name)
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@router.get("/models/{model_id}/datasets", response_model=list[DatasetOut])
def list_model_datasets(
    model: CustomModel = Depends(get_owned_model), db: Session = Depends(get_db)
) -> list[Dataset]:
    return (
        db.query(Dataset)
        .filter(Dataset.model_id == model.id)
        .order_by(Dataset.created_at.desc())
        .all()
    )


@router.get("/datasets/{dataset_id}", response_model=DatasetDetailOut)
def get_dataset(dataset: Dataset = Depends(get_owned_dataset)) -> Dataset:
    return dataset


def _detect_file_kind(model: CustomModel, upload: UploadFile) -> FileKind:
    suffix = Path(upload.filename or "").suffix.lower()
    if model.category == ModelCategory.TEXT_TO_TEXT:
        if suffix not in {".csv", ".jsonl"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text-to-Text datasets must be CSV or JSONL files.",
            )
        return FileKind.TEXT_DATASET

    if upload.content_type in ALLOWED_IMAGE_MIME_TYPES:
        return FileKind.IMAGE_FILE
    if suffix in {".csv", ".jsonl"}:
        return FileKind.IMAGE_MANIFEST
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Text-to-Image uploads must be PNG/JPEG/WEBP images or CSV/JSONL manifests.",
    )


@router.post("/datasets/{dataset_id}/files", response_model=StoredFileOut, status_code=status.HTTP_201_CREATED)
async def upload_dataset_file(
    upload: UploadFile = File(...),
    dataset: Dataset = Depends(get_owned_dataset),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StoredFile:
    model = (
        db.query(CustomModel)
        .filter(CustomModel.id == dataset.model_id, CustomModel.owner_id == current_user.id)
        .first()
    )
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")

    settings = get_settings()
    file_kind = _detect_file_kind(model, upload)
    data = await read_upload_file(upload, max_mb=settings.max_upload_mb)
    metadata = {}
    if file_kind == FileKind.IMAGE_FILE:
        metadata = validate_image_bytes(data, upload.content_type, max_mb=settings.max_upload_mb)

    stored = upload_bytes(
        data=data,
        filename=upload.filename or "dataset-file",
        content_type=upload.content_type,
        key_prefix=f"models/{model.id}/datasets/{dataset.id}",
    )
    file_record = StoredFile(
        owner_id=current_user.id,
        model_id=model.id,
        dataset_id=dataset.id,
        kind=file_kind,
        original_filename=upload.filename or "dataset-file",
        content_type=upload.content_type,
        size_bytes=stored.size_bytes,
        checksum_sha256=stored.checksum_sha256,
        storage_bucket=stored.bucket,
        storage_key=stored.key,
        public_url=stored.public_url,
    )
    db.add(file_record)
    dataset.status = DatasetStatus.UPLOADED
    dataset.dataset_metadata = {**(dataset.dataset_metadata or {}), "last_upload_metadata": metadata}
    db.add(dataset)
    db.commit()
    db.refresh(file_record)
    return file_record


@router.post("/datasets/{dataset_id}/validate", response_model=DatasetValidationOut)
def validate_dataset_endpoint(
    dataset: Dataset = Depends(get_owned_dataset),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DatasetValidationOut:
    model = (
        db.query(CustomModel)
        .filter(CustomModel.id == dataset.model_id, CustomModel.owner_id == current_user.id)
        .first()
    )
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    validated = validate_dataset(db, dataset, model)
    db.refresh(validated)
    return DatasetValidationOut(dataset=validated, issues=validated.issues)


@router.get("/datasets/{dataset_id}/readiness", response_model=DatasetValidationOut)
def get_dataset_readiness(dataset: Dataset = Depends(get_owned_dataset)) -> DatasetValidationOut:
    return DatasetValidationOut(dataset=dataset, issues=dataset.issues)
