"""
API v1 router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import prediction, health, feedback

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(prediction.router, prefix="/predict", tags=["prediction"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])