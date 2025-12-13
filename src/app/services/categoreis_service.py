from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.models.category import Category


class CategoryService:
    @staticmethod
    async def get_all_categories(db_session: AsyncSession):
        result = await db_session.execute(select(Category))
        return result.scalars().all()
