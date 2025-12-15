import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from src.app.db.models.post import Post
from src.app.db.models.user import User
from src.app.db.models.category import Category, PostCategoryAssociation
from src.app.schemas.post import PostCreate, ShowPost, PostUpdate
from src.app.schemas.user import ShowUser
from src.app.schemas.category import ShowCategory


class PostService:
    @staticmethod
    def _to_show_post(post: Post, user: User, categories: list[Category]):
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

    @staticmethod
    async def _get_post_categories_and_associate(post: Post, category_ids: list[uuid.UUID], db_session: AsyncSession):
        if not category_ids:
            return []

        stmt = select(Category).where(Category.category_id.in_(category_ids))
        result = await db_session.execute(stmt)
        categories = result.scalars().all()

        for category in categories:
            db_session.add(
                PostCategoryAssociation(
                    post_id=post.post_id,
                    category_id=category.category_id,
                )
            )

        return categories

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
        post = Post(title=data.title, content=data.content, image=data.image, user_id=user.user_id, )

        db_session.add(post)
        await db_session.flush()

        categories = await PostService._get_post_categories_and_associate(
            post=post, category_ids=data.category_ids, db_session=db_session
        )

        await db_session.commit()

        return PostService._to_show_post(post=post, user=user, categories=categories)

    @staticmethod
    async def update_post(post_id: uuid.UUID, data: PostUpdate, user: User, db_session: AsyncSession):
        result = await db_session.execute(select(Post).where(Post.post_id == post_id))
        post = result.scalar_one_or_none()

        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        if post.user_id != user.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the author of this post")

        if data.title is not None:
            post.title = data.title
        if data.content is not None:
            post.content = data.content
        if data.image is not None:
            post.image = data.image

        categories: list[Category] = []
        if data.category_ids is not None:
            await db_session.execute(
                delete(PostCategoryAssociation).where(
                    PostCategoryAssociation.post_id == post.post_id
                )
            )

            categories = await PostService._get_post_categories_and_associate(
                post=post, category_ids=data.category_ids, db_session=db_session
            )

        await db_session.commit()

        return PostService._to_show_post(post=post, user=user, categories=categories)

    @staticmethod
    async def delete_post(post_id: uuid.UUID, user: User, db_session: AsyncSession):
        result = await db_session.execute(select(Post).where(Post.post_id == post_id))
        post = result.scalar_one_or_none()

        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        if post.user_id != user.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the author of this post")

        await db_session.execute(
            delete(PostCategoryAssociation).where(
                PostCategoryAssociation.post_id == post.post_id
            )
        )

        await db_session.delete(post)
        await db_session.commit()

        return {"detail": "Post deleted successfully"}
