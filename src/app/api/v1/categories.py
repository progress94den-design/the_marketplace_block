from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.category import ShowCategory
from src.app.services.categoreis_service import CategoryService
from src.app.db.session import get_async_session


categories_router = APIRouter()


@categories_router.get("/", response_model=list[ShowCategory])
async def get_categories(db_session: AsyncSession = Depends(get_async_session)):
    return await CategoryService.get_all_categories(db_session)
