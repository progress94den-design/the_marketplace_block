from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.post import ShowPost
from src.app.services.posts_service import PostService
from src.app.db.session import get_async_session


posts_router = APIRouter()


@posts_router.get("/", response_model=list[ShowPost])
async def get_users(db_session: AsyncSession = Depends(get_async_session)):
    return await PostService.get_all_posts(db_session)
