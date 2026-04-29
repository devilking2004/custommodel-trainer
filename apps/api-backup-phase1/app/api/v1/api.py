from fastapi import APIRouter

from app.api.v1.routes import api_keys, auth, datasets, feedback, health, inference, models, training, uploads, usage, users, versions

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(models.router)
api_router.include_router(uploads.router)
api_router.include_router(datasets.router)
api_router.include_router(training.router)
api_router.include_router(versions.router)
api_router.include_router(api_keys.router)
api_router.include_router(inference.router)
api_router.include_router(feedback.router)
api_router.include_router(usage.router)
