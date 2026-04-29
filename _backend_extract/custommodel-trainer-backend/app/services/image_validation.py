from io import BytesIO

from fastapi import HTTPException, status
from PIL import Image, UnidentifiedImageError

ALLOWED_IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}


def validate_image_bytes(data: bytes, content_type: str | None, *, max_mb: int) -> dict:
    if content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PNG, JPEG, and WEBP images are supported.",
        )
    if len(data) > max_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image is too large. Max allowed size is {max_mb} MB.",
        )
    try:
        with Image.open(BytesIO(data)) as image:
            width, height = image.size
            fmt = image.format
    except UnidentifiedImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded image is invalid or corrupted."
        ) from exc
    return {"width": width, "height": height, "format": fmt}
