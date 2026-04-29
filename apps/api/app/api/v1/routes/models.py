from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_owned_model
from app.db.session import get_db
from app.models.custom_model import CustomModel
from app.models.user import User
from app.schemas.custom_model import CustomModelCreate, CustomModelOut, CustomModelUpdate
from app.utils.text import slugify

router = APIRouter(prefix="/models", tags=["models"])


def _make_unique_slug(db: Session, owner_id: str, name: str) -> str:
    base_slug = slugify(name)
    slug = base_slug
    counter = 2
    while db.query(CustomModel).filter(CustomModel.owner_id == owner_id, CustomModel.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


@router.get("", response_model=list[CustomModelOut])
def list_models(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[CustomModel]:
    return (
        db.query(CustomModel)
        .filter(CustomModel.owner_id == current_user.id)
        .order_by(CustomModel.created_at.desc())
        .all()
    )


@router.post("", response_model=CustomModelOut, status_code=status.HTTP_201_CREATED)
def create_model(
    payload: CustomModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CustomModel:
    model = CustomModel(
        owner_id=current_user.id,
        name=payload.name,
        slug=_make_unique_slug(db, current_user.id, payload.name),
        description=payload.description,
        category=payload.category,
        visibility=payload.visibility,
        improve_from_feedback=payload.improve_from_feedback,
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@router.get("/{model_id}", response_model=CustomModelOut)
def get_model(model: CustomModel = Depends(get_owned_model)) -> CustomModel:
    return model


@router.patch("/{model_id}", response_model=CustomModelOut)
def update_model(
    payload: CustomModelUpdate,
    model: CustomModel = Depends(get_owned_model),
    db: Session = Depends(get_db),
) -> CustomModel:
    if payload.name is not None:
        model.name = payload.name
        # Keep the old slug stable for API URLs. Change this only if you need editable slugs.
    if payload.description is not None:
        model.description = payload.description
    if payload.visibility is not None:
        model.visibility = payload.visibility
    if payload.improve_from_feedback is not None:
        model.improve_from_feedback = payload.improve_from_feedback

    db.add(model)
    db.commit()
    db.refresh(model)
    return model

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(
    model: CustomModel = Depends(get_owned_model),
    db: Session = Depends(get_db),
) -> Response:
    db.delete(model)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)