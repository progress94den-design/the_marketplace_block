from fastapi import APIRouter

from src.app.api.v1.user import user_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/users", tags=["Users"])
