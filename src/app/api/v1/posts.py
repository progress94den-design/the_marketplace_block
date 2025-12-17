import uuid

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.app.schemas.post import ShowPost, PostCreate, PostUpdate
from src.app.services.posts_service import PostService
from src.app.db.models.user import User
from src.app.db.session import get_async_session
from src.app.core.jwt import get_current_user

posts_router = APIRouter()


@posts_router.get("/", response_model=list[ShowPost])
async def get_posts(db_session: AsyncSession = Depends(get_async_session)):
    return await PostService.get_all_posts(db_session)


@posts_router.post("/", response_model=ShowPost)
async def create_post(
        data: Annotated[PostCreate, Depends()],
        current_user: User = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_async_session),
        image: UploadFile | None = File(None),
):
    return await PostService.create_post(data=data, user=current_user, db_session=db_session, image=image)


@posts_router.put("/{post_id}", response_model=ShowPost)
async def update_post(
        post_id: uuid.UUID,
        data: Annotated[PostUpdate, Depends()],
        current_user: User = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_async_session),
        image: UploadFile | None = File(None),
):
    return await PostService.update_post(
        post_id=post_id, data=data, user=current_user, db_session=db_session, image=image
    )


@posts_router.delete("/{post_id}")
async def delete_post(
        post_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_async_session),
):
    return await PostService.delete_post(post_id=post_id, user=current_user, db_session=db_session)
