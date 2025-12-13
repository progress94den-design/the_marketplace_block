from fastapi import APIRouter

from src.app.api.v1.user import user_router
from src.app.api.v1.auth import auth_router
from src.app.api.v1.posts import posts_router
from src.app.api.v1.categories import categories_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/users", tags=["Users"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(posts_router, prefix="/posts", tags=["Posts"])
api_router.include_router(categories_router, prefix="/categories", tags=["Categories"])
