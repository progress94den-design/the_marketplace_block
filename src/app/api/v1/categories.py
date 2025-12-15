import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.app.db.session import get_async_session
from src.app.core.jwt import get_current_user
from src.app.db.models import User
from src.app.schemas.category import ShowCategory, CategoryCreate
from src.app.services.categoreis_service import CategoryService

categories_router = APIRouter()


@categories_router.get("/", response_model=list[ShowCategory])
async def get_categories(db_session: AsyncSession = Depends(get_async_session)):
    return await CategoryService.get_all_categories(db_session)


@categories_router.post("/", response_model=ShowCategory)
async def create_category(
        data: Annotated[CategoryCreate, Depends()],
        current_user: User = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_async_session)
):
    return await CategoryService.create_category(data, db_session)


@categories_router.delete("/{category_id}")
async def delete_category(
        category_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db_session: AsyncSession = Depends(get_async_session)
):
    return await CategoryService.delete_category(category_id, db_session)
