from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_owned_model
from app.core.config import get_settings
from app.db.session import get_db
from app.models.custom_model import CustomModel
from app.models.enums import FileKind
from app.models.stored_file import StoredFile
from app.schemas.files import StoredFileOut
from app.services.image_validation import validate_image_bytes
from app.services.storage import read_upload_file, upload_bytes

router = APIRouter(tags=["uploads"])


@router.post("/models/{model_id}/icon", response_model=StoredFileOut)
async def upload_model_icon(
    upload: UploadFile = File(...),
    model: CustomModel = Depends(get_owned_model),
    db: Session = Depends(get_db),
) -> StoredFile:
    settings = get_settings()
    data = await read_upload_file(upload, max_mb=settings.max_icon_mb)
    validate_image_bytes(data, upload.content_type, max_mb=settings.max_icon_mb)
    stored = upload_bytes(
        data=data,
        filename=upload.filename or "icon.png",
        content_type=upload.content_type,
        key_prefix=f"models/{model.id}/icons",
    )
    file_record = StoredFile(
        owner_id=model.owner_id,
        model_id=model.id,
        dataset_id=None,
        kind=FileKind.ICON,
        original_filename=upload.filename or "icon.png",
        content_type=upload.content_type,
        size_bytes=stored.size_bytes,
        checksum_sha256=stored.checksum_sha256,
        storage_bucket=stored.bucket,
        storage_key=stored.key,
        public_url=stored.public_url,
    )
    db.add(file_record)
    db.flush()
    model.icon_file_id = file_record.id
    model.icon_url = file_record.public_url
    db.add(model)
    db.commit()
    db.refresh(file_record)
    return file_record
