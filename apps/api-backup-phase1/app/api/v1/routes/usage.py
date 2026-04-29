from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_owned_model
from app.db.session import get_db
from app.models.custom_model import CustomModel
from app.models.usage_log import UsageLog
from app.schemas.usage import UsageLogOut

router = APIRouter(tags=["usage"])


@router.get("/models/{model_id}/usage", response_model=list[UsageLogOut])
def list_model_usage(
    model: CustomModel = Depends(get_owned_model), db: Session = Depends(get_db)
) -> list[UsageLog]:
    return (
        db.query(UsageLog)
        .filter(UsageLog.model_id == model.id)
        .order_by(UsageLog.created_at.desc())
        .limit(200)
        .all()
    )
