from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_owned_model
from app.db.session import get_db
from app.models.custom_model import CustomModel
from app.models.enums import FeedbackSource, FeedbackStatus
from app.models.feedback import Feedback
from app.models.model_version import ModelVersion
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackOut, FeedbackReview
from app.services.api_keys import validate_api_key_for_model

router = APIRouter(tags=["feedback"])


@router.get("/models/{model_id}/feedback", response_model=list[FeedbackOut])
def list_feedback(
    model: CustomModel = Depends(get_owned_model), db: Session = Depends(get_db)
) -> list[Feedback]:
    return (
        db.query(Feedback)
        .filter(Feedback.model_id == model.id)
        .order_by(Feedback.created_at.desc())
        .all()
    )


@router.post("/models/{model_id}/feedback", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def create_playground_feedback(
    payload: FeedbackCreate,
    model: CustomModel = Depends(get_owned_model),
    db: Session = Depends(get_db),
) -> Feedback:
    feedback = Feedback(
        owner_id=model.owner_id,
        model_id=model.id,
        model_version_id=model.current_version_id,
        request_id=payload.request_id,
        source=FeedbackSource.PLAYGROUND,
        input_payload=payload.input_payload,
        output_payload=payload.output_payload,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.post("/inference/{model_id}/feedback", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def create_api_feedback(
    model_id: str,
    payload: FeedbackCreate,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> Feedback:
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-API-Key header is required")
    _, model = validate_api_key_for_model(db, model_id, x_api_key)
    feedback = Feedback(
        owner_id=model.owner_id,
        model_id=model.id,
        model_version_id=model.current_version_id,
        request_id=payload.request_id,
        source=FeedbackSource.API,
        input_payload=payload.input_payload,
        output_payload=payload.output_payload,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.patch("/feedback/{feedback_id}/review", response_model=FeedbackOut)
def review_feedback(
    feedback_id: str,
    payload: FeedbackReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Feedback:
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id, Feedback.owner_id == current_user.id).first()
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    if payload.status not in {FeedbackStatus.APPROVED, FeedbackStatus.REJECTED}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback review status must be approved or rejected.",
        )
    feedback.status = payload.status
    feedback.approved_for_training = payload.approved_for_training and payload.status == FeedbackStatus.APPROVED
    feedback.reviewed_at = datetime.now(timezone.utc)
    feedback.reviewed_by_id = current_user.id
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
