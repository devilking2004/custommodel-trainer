import time
from datetime import datetime, timezone

from sqlalchemy import func

from app.db.session import SessionLocal
from app.models.custom_model import CustomModel
from app.models.enums import FileKind, ModelCategory, ModelStatus, TrainingStatus, VersionStatus
from app.models.model_version import ModelVersion
from app.models.stored_file import StoredFile
from app.models.training_job import TrainingJob
from app.services.dataset_loader import load_text_to_text_examples
from app.services.storage import upload_bytes
from app.services.text_to_text import train_text_to_text_lora


MOCK_TRAINING_STEPS = [
    (10, "Preparing dataset"),
    (25, "Loading base model"),
    (40, "Applying LoRA adapters"),
    (60, "Running training loop"),
    (75, "Evaluating model"),
    (90, "Saving artifacts"),
    (100, "Creating model version"),
]


def _append_log(job: TrainingJob, message: str) -> None:
    entry = {"time": datetime.now(timezone.utc).isoformat(), "message": message}
    job.logs = [*(job.logs or []), entry]


def _set_progress(db, job: TrainingJob, progress: int, step: str) -> None:
    job.progress = progress
    job.current_step = step
    _append_log(job, step)
    db.add(job)
    db.commit()


def _next_version_number(db, model: CustomModel) -> int:
    max_version = (
        db.query(func.max(ModelVersion.version_number))
        .filter(ModelVersion.model_id == model.id)
        .scalar()
        or 0
    )
    return int(max_version) + 1


def _archive_existing_versions(db, model: CustomModel) -> None:
    db.query(ModelVersion).filter(ModelVersion.model_id == model.id).update(
        {"is_active": False, "status": VersionStatus.ARCHIVED}
    )


def _create_version(
    *,
    db,
    job: TrainingJob,
    model: CustomModel,
    version_number: int,
    artifact_file: StoredFile,
    base_model: str,
    metrics: dict,
    notes: str | None,
) -> ModelVersion:
    _archive_existing_versions(db, model)

    version = ModelVersion(
        owner_id=job.owner_id,
        model_id=model.id,
        training_job_id=job.id,
        version_number=version_number,
        name=f"v{version_number}",
        status=VersionStatus.ACTIVE,
        is_active=True,
        base_model=base_model,
        artifact_file_id=artifact_file.id,
        artifact_storage_key=artifact_file.storage_key,
        metrics=metrics,
        notes=notes,
    )

    db.add(version)
    db.flush()

    model.status = ModelStatus.TRAINED
    model.current_version_id = version.id

    db.add(model)
    return version


def _run_mock_training(db, job: TrainingJob, model: CustomModel) -> ModelVersion:
    for progress, step in MOCK_TRAINING_STEPS:
        time.sleep(1)
        job = db.query(TrainingJob).filter(TrainingJob.id == job.id).first()
        if not job:
            raise RuntimeError("Training job disappeared during processing")
        _set_progress(db, job, progress, step)

    version_number = _next_version_number(db, model)

    artifact_text = (
        f"CustomModel Trainer mock artifact\n"
        f"model_id={model.id}\n"
        f"training_job_id={job.id}\n"
        f"version={version_number}\n"
    ).encode("utf-8")

    uploaded = upload_bytes(
        data=artifact_text,
        filename=f"{model.slug}-v{version_number}.txt",
        content_type="text/plain",
        key_prefix=f"models/{model.id}/versions/v{version_number}",
    )

    artifact_file = StoredFile(
        owner_id=job.owner_id,
        model_id=model.id,
        dataset_id=job.dataset_id,
        kind=FileKind.MODEL_ARTIFACT,
        original_filename=f"{model.slug}-v{version_number}.txt",
        content_type="text/plain",
        size_bytes=uploaded.size_bytes,
        checksum_sha256=uploaded.checksum_sha256,
        storage_bucket=uploaded.bucket,
        storage_key=uploaded.key,
        public_url=uploaded.public_url,
    )

    db.add(artifact_file)
    db.flush()

    metrics = {
        "engine": "mock",
        "readiness_score": model.readiness_score,
        "mock_loss": round(0.18 / version_number, 4),
        "mock_quality_score": min(98, 70 + model.readiness_score // 3),
    }

    return _create_version(
        db=db,
        job=job,
        model=model,
        version_number=version_number,
        artifact_file=artifact_file,
        base_model=(job.training_config or {}).get("base_model") or "mock-base-model",
        metrics=metrics,
        notes=(job.training_config or {}).get("notes"),
    )


def _run_real_text_to_text_training(db, job: TrainingJob, model: CustomModel) -> ModelVersion:
    if not job.dataset:
        raise RuntimeError("Training job has no dataset.")

    _set_progress(db, job, 10, "Loading text-to-text dataset")
    examples = load_text_to_text_examples(db, job.dataset)

    if not examples:
        raise RuntimeError("No valid text-to-text examples found in dataset.")

    config = job.training_config or {}
    base_model = config.get("base_model") or "google/flan-t5-small"
    epochs = int(config.get("epochs") or 1)
    learning_rate = float(config.get("learning_rate") or 0.0002)

    def log_training(message: str) -> None:
        fresh_job = db.query(TrainingJob).filter(TrainingJob.id == job.id).first()
        if fresh_job:
            _append_log(fresh_job, message)
            db.add(fresh_job)
            db.commit()

    _set_progress(db, job, 25, f"Starting real Text-to-Text LoRA training with {base_model}")

    artifact_bytes, metrics = train_text_to_text_lora(
        examples=examples,
        base_model=base_model,
        epochs=epochs,
        learning_rate=learning_rate,
        log=log_training,
    )

    _set_progress(db, job, 85, "Uploading trained LoRA artifact")

    version_number = _next_version_number(db, model)

    uploaded = upload_bytes(
        data=artifact_bytes,
        filename=f"{model.slug}-v{version_number}-text-to-text-lora.zip",
        content_type="application/zip",
        key_prefix=f"models/{model.id}/versions/v{version_number}",
    )

    artifact_file = StoredFile(
        owner_id=job.owner_id,
        model_id=model.id,
        dataset_id=job.dataset_id,
        kind=FileKind.MODEL_ARTIFACT,
        original_filename=f"{model.slug}-v{version_number}-text-to-text-lora.zip",
        content_type="application/zip",
        size_bytes=uploaded.size_bytes,
        checksum_sha256=uploaded.checksum_sha256,
        storage_bucket=uploaded.bucket,
        storage_key=uploaded.key,
        public_url=uploaded.public_url,
    )

    db.add(artifact_file)
    db.flush()

    metrics = {
        **metrics,
        "readiness_score": model.readiness_score,
    }

    version = _create_version(
        db=db,
        job=job,
        model=model,
        version_number=version_number,
        artifact_file=artifact_file,
        base_model=metrics.get("base_model") or base_model,
        metrics=metrics,
        notes=config.get("notes"),
    )

    _set_progress(db, job, 100, f"Created real Text-to-Text model version v{version_number}")

    return version


def run_training_job(training_job_id: str) -> str:
    db = SessionLocal()

    try:
        job = db.query(TrainingJob).filter(TrainingJob.id == training_job_id).first()
        if not job:
            raise RuntimeError(f"Training job {training_job_id} not found")

        model = db.query(CustomModel).filter(CustomModel.id == job.model_id).first()
        if not model:
            raise RuntimeError(f"Model {job.model_id} not found")

        job.status = TrainingStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        model.status = ModelStatus.TRAINING

        _append_log(job, "Training job started.")
        db.add(job)
        db.add(model)
        db.commit()

        if model.category == ModelCategory.TEXT_TO_TEXT:
            version = _run_real_text_to_text_training(db, job, model)
        else:
            version = _run_mock_training(db, job, model)

        job = db.query(TrainingJob).filter(TrainingJob.id == training_job_id).first()
        if not job:
            raise RuntimeError("Training job disappeared before completion")

        job.status = TrainingStatus.SUCCEEDED
        job.progress = 100
        job.current_step = "Completed"
        job.completed_at = datetime.now(timezone.utc)
        _append_log(job, f"Created model version {version.name}.")

        db.add(job)
        db.commit()

        return version.id

    except Exception as exc:
        job = db.query(TrainingJob).filter(TrainingJob.id == training_job_id).first()

        if job:
            job.status = TrainingStatus.FAILED
            job.error_message = str(exc)
            job.completed_at = datetime.now(timezone.utc)
            _append_log(job, f"Training failed: {exc}")
            db.add(job)
            db.commit()

        raise

    finally:
        db.close()