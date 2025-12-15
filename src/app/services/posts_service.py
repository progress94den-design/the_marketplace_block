import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.db.models.post import Post
from src.app.db.models.user import User
from src.app.db.models.category import Category, PostCategoryAssociation
from src.app.schemas.post import PostCreate, ShowPost
from src.app.schemas.user import ShowUser
from src.app.schemas.category import ShowCategory


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

    @staticmethod
    async def create_post(data: PostCreate, user: User, db_session: AsyncSession):
        post = Post(
            title=data.title,
            content=data.content,
            image=data.image,
            user_id=user.user_id,
        )

        db_session.add(post)
        await db_session.flush()

        categories: list[Category] = []
        if data.category_ids:
            stmt = select(Category).where(Category.category_id.in_(data.category_ids))
            result = await db_session.execute(stmt)
            categories = result.scalars().all()

            for category in categories:
                db_session.add(
                    PostCategoryAssociation(
                        post_id=post.post_id,
                        category_id=category.category_id,
                    )
                )

        await db_session.commit()

        return ShowPost(
            post_id=post.post_id,
            title=post.title,
            content=post.content,
            image=post.image,
            created_at=post.created_at,
            updated_at=post.updated_at,
            user=ShowUser(
                user_id=user.user_id,
                email=user.email,
                phone_number=user.phone_number,
                name=user.name,
                is_active=user.is_active,
            ),
            categories=[
                ShowCategory(
                    category_id=category.category_id,
                    name=category.name
                )
                for category in categories
            ]
        )
