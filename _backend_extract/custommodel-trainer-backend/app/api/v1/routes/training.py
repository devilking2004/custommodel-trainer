from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_owned_model
from app.db.session import get_db
from app.models.custom_model import CustomModel
from app.models.dataset import Dataset
from app.models.enums import DatasetStatus, FeedbackStatus, TrainingJobType
from app.models.feedback import Feedback
from app.models.training_job import TrainingJob
from app.models.user import User
from app.schemas.training import TrainingJobOut, TrainingStartRequest
from app.services.training_queue import enqueue_training_job

router = APIRouter(tags=["training"])


def _resolve_dataset(db: Session, model: CustomModel, dataset_id: str | None) -> Dataset:
    query = db.query(Dataset).filter(Dataset.model_id == model.id, Dataset.owner_id == model.owner_id)
    if dataset_id:
        dataset = query.filter(Dataset.id == dataset_id).first()
    else:
        dataset = query.order_by(Dataset.created_at.desc()).first()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    if dataset.status != DatasetStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset is not ready. Validate the dataset and fix errors before training.",
        )
    return dataset


@router.post("/models/{model_id}/train", response_model=TrainingJobOut, status_code=status.HTTP_202_ACCEPTED)
def start_training_job(
    payload: TrainingStartRequest,
    model: CustomModel = Depends(get_owned_model),
    db: Session = Depends(get_db),
) -> TrainingJob:
    dataset = _resolve_dataset(db, model, payload.dataset_id)
    job = TrainingJob(
        owner_id=model.owner_id,
        model_id=model.id,
        dataset_id=dataset.id,
        job_type=TrainingJobType.INITIAL,
        training_config=payload.model_dump(),
        current_step="Queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return enqueue_training_job(db, job)


@router.post("/models/{model_id}/retrain", response_model=TrainingJobOut, status_code=status.HTTP_202_ACCEPTED)
def request_retraining(
    payload: TrainingStartRequest,
    model: CustomModel = Depends(get_owned_model),
    db: Session = Depends(get_db),
) -> TrainingJob:
    approved_feedback_count = (
        db.query(Feedback)
        .filter(
            Feedback.model_id == model.id,
            Feedback.status == FeedbackStatus.APPROVED,
            Feedback.approved_for_training.is_(True),
        )
        .count()
    )
    if model.improve_from_feedback and approved_feedback_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No approved feedback is available for retraining yet.",
        )
    dataset = _resolve_dataset(db, model, payload.dataset_id)
    config = payload.model_dump()
    config["approved_feedback_count"] = approved_feedback_count
    job = TrainingJob(
        owner_id=model.owner_id,
        model_id=model.id,
        dataset_id=dataset.id,
        job_type=TrainingJobType.RETRAIN,
        training_config=config,
        current_step="Queued retraining job",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return enqueue_training_job(db, job)


@router.get("/training-jobs/{job_id}", response_model=TrainingJobOut)
def get_training_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TrainingJob:
    job = db.query(TrainingJob).filter(TrainingJob.id == job_id, TrainingJob.owner_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training job not found")
    return job
