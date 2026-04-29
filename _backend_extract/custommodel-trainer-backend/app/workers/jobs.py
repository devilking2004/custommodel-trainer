import time
from datetime import datetime, timezone

from sqlalchemy import func

from app.db.session import SessionLocal
from app.models.custom_model import CustomModel
from app.models.enums import FileKind, ModelStatus, TrainingStatus, VersionStatus
from app.models.model_version import ModelVersion
from app.models.stored_file import StoredFile
from app.models.training_job import TrainingJob
from app.services.storage import upload_bytes


TRAINING_STEPS = [
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


def run_training_job(training_job_id: str) -> str:
    """Mock training job.

    This gives the product a real asynchronous workflow without requiring GPUs yet.
    Replace the sleep/mock artifact section with Transformers/PEFT or Diffusers/LoRA later.
    """
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

        for progress, step in TRAINING_STEPS:
            time.sleep(1)
            job = db.query(TrainingJob).filter(TrainingJob.id == training_job_id).first()
            if not job:
                raise RuntimeError("Training job disappeared during processing")
            job.progress = progress
            job.current_step = step
            _append_log(job, step)
            db.add(job)
            db.commit()

        max_version = (
            db.query(func.max(ModelVersion.version_number))
            .filter(ModelVersion.model_id == model.id)
            .scalar()
            or 0
        )
        version_number = max_version + 1

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

        db.query(ModelVersion).filter(ModelVersion.model_id == model.id).update(
            {"is_active": False, "status": VersionStatus.ARCHIVED}
        )
        version = ModelVersion(
            owner_id=job.owner_id,
            model_id=model.id,
            training_job_id=job.id,
            version_number=version_number,
            name=f"v{version_number}",
            status=VersionStatus.ACTIVE,
            is_active=True,
            base_model=(job.training_config or {}).get("base_model") or "mock-base-model",
            artifact_file_id=artifact_file.id,
            artifact_storage_key=uploaded.key,
            metrics={
                "readiness_score": model.readiness_score,
                "mock_loss": round(0.18 / version_number, 4),
                "mock_quality_score": min(98, 70 + model.readiness_score // 3),
            },
            notes=(job.training_config or {}).get("notes"),
        )
        db.add(version)
        db.flush()

        job.status = TrainingStatus.SUCCEEDED
        job.progress = 100
        job.current_step = "Completed"
        job.completed_at = datetime.now(timezone.utc)
        _append_log(job, f"Created model version v{version_number}.")
        model.status = ModelStatus.TRAINED
        model.current_version_id = version.id

        db.add(job)
        db.add(model)
        db.commit()
        return version.id
    except Exception as exc:  # noqa: BLE001 - worker must persist failure details
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
