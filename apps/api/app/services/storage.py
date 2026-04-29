from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings


@dataclass
class UploadedObject:
    bucket: str
    key: str
    public_url: str | None
    size_bytes: int
    checksum_sha256: str
    content_type: str | None


def _safe_filename(filename: str) -> str:
    name = Path(filename or "file").name.replace(" ", "-")
    return "".join(ch for ch in name if ch.isalnum() or ch in {"-", "_", "."}) or "file"


def get_s3_client():
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        region_name=settings.s3_region,
        use_ssl=settings.s3_use_ssl,
    )


def ensure_bucket_exists() -> None:
    settings = get_settings()
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.s3_bucket_name)
    except ClientError:
        client.create_bucket(Bucket=settings.s3_bucket_name)


def build_public_url(key: str) -> str | None:
    settings = get_settings()
    if not settings.s3_public_base_url:
        return None
    base = settings.s3_public_base_url.rstrip("/")
    return f"{base}/{settings.s3_bucket_name}/{key}"


async def read_upload_file(upload_file: UploadFile, max_mb: int) -> bytes:
    data = await upload_file.read()
    max_bytes = max_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File is too large. Max allowed size is {max_mb} MB.",
        )
    if len(data) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
    return data


def upload_bytes(
    *,
    data: bytes,
    filename: str,
    content_type: str | None,
    key_prefix: str,
) -> UploadedObject:
    settings = get_settings()
    ensure_bucket_exists()
    safe_name = _safe_filename(filename)
    key = f"{key_prefix.strip('/')}/{uuid4()}-{safe_name}"
    checksum = sha256(data).hexdigest()
    client = get_s3_client()
    extra_args = {"ContentType": content_type or "application/octet-stream"}
    client.upload_fileobj(BytesIO(data), settings.s3_bucket_name, key, ExtraArgs=extra_args)
    return UploadedObject(
        bucket=settings.s3_bucket_name,
        key=key,
        public_url=build_public_url(key),
        size_bytes=len(data),
        checksum_sha256=checksum,
        content_type=content_type,
    )


def download_bytes(key: str) -> bytes:
    settings = get_settings()
    client = get_s3_client()
    obj = client.get_object(Bucket=settings.s3_bucket_name, Key=key)
    return obj["Body"].read()
