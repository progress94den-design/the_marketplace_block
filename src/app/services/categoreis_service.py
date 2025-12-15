import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.app.db.models.category import Category, PostCategoryAssociation
from src.app.schemas.category import CategoryCreate, ShowCategory


class CategoryService:
    @staticmethod
    async def get_all_categories(db_session: AsyncSession):
        result = await db_session.execute(select(Category))
        return result.scalars().all()

    @staticmethod
    async def create_category(data: CategoryCreate, db_session: AsyncSession):
        result = await db_session.execute(
            select(Category).where(Category.name == data.name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Category with this name already exists")

        category = Category(name=data.name)
        db_session.add(category)

        await db_session.commit()

        return ShowCategory(
            category_id=category.category_id,
            name=category.name
        )

    @staticmethod
    async def delete_category(category_id: uuid.UUID, db_session: AsyncSession):
        result = await db_session.execute(
            select(Category).where(Category.category_id == category_id)
        )
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        await db_session.execute(
            delete(PostCategoryAssociation).where(
                PostCategoryAssociation.category_id == category_id
            )
        )

        await db_session.delete(category)
        await db_session.commit()

        return {"detail": "Category deleted successfully"}
