import uuid
from typing import List

from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, UploadFile

from src.app.db.models.post import Post
from src.app.db.models.user import User
from src.app.db.models.category import Category, PostCategoryAssociation
from src.app.schemas.post import PostCreate, ShowPost, PostUpdate, PostQueryParams
from src.app.schemas.user import ShowUser
from src.app.schemas.category import ShowCategory
from src.app.core.images import upload_post_image, delete_image, generate_presigned_url


class PostService:
    @staticmethod
    def _to_show_post(post: Post, user: User, categories: List[Category]):
        image_url = generate_presigned_url(post.image) if post.image else None
        return ShowPost(
            post_id=post.post_id,
            title=post.title,
            content=post.content,
            image=image_url,
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
    async def _get_post_categories_and_associate(post: Post, category_ids: List[uuid.UUID], db_session: AsyncSession):
        if not category_ids:
            return []

        result = await db_session.execute(select(Category).where(Category.category_id.in_(category_ids)))
        categories = result.scalars().all()

        if len(categories) != len(set(category_ids)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more categories not found")

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
    async def get_posts_params(params: PostQueryParams, db_session: AsyncSession):
        stmt = select(Post).options(
            selectinload(Post.user),
            selectinload(Post.categories)
        )

        conditions = []
        if params.search:
            ts_vector = func.to_tsvector('russian', Post.title + ' ' + Post.content)
            ts_query = func.plainto_tsquery('russian', params.search)
            conditions.append(ts_vector.op('@@')(ts_query))
        if params.category_ids:
            stmt = stmt.join(PostCategoryAssociation, Post.post_id == PostCategoryAssociation.post_id)
            conditions.append(PostCategoryAssociation.category_id.in_(params.category_ids))
        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.offset(params.skip).limit(params.page_size)
        result = await db_session.execute(stmt)
        posts = result.scalars().unique().all()
        return [
            PostService._to_show_post(post=post, user=post.user, categories=post.categories)
            for post in posts
        ]

    @staticmethod
    async def create_post(data: PostCreate, user: User, db_session: AsyncSession, image: UploadFile | None = None):
        post = Post(title=data.title, content=data.content, user_id=user.user_id)

        db_session.add(post)
        await db_session.flush()

        if image:
            post.image = await upload_post_image(image, post.post_id)

        categories = await PostService._get_post_categories_and_associate(
            post=post, category_ids=data.category_ids, db_session=db_session
        )

        await db_session.commit()

        return PostService._to_show_post(post=post, user=user, categories=categories)

    @staticmethod
    async def update_post(
            post_id: uuid.UUID,
            data: PostUpdate,
            user: User,
            db_session: AsyncSession,
            image: UploadFile | None = None,
    ):
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
        if image is not None:
            if post.image:
                delete_image(post.image)
            post.image = await upload_post_image(image, post.post_id)

        categories: List[Category] = []
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

        if post.image:
            delete_image(post.image)

        await db_session.execute(
            delete(PostCategoryAssociation).where(
                PostCategoryAssociation.post_id == post.post_id
            )
        )

        await db_session.delete(post)
        await db_session.commit()

        return {"detail": "Post deleted successfully"}
