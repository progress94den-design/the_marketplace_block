from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from src.app.db.models.post import Post


class PostService:
    @staticmethod
    async def get_all_posts(db_session: AsyncSession):
        stmt = (
            select(Post)
            .options(
                selectinload(Post.user),
                selectinload(Post.categories),
            )
        )
        result = await db_session.execute(stmt)
        return result.scalars().all()
