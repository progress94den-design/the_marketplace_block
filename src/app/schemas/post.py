import uuid

from datetime import datetime
from pydantic import BaseModel

from src.app.schemas.user import ShowUser
from src.app.schemas.category import ShowCategory


class ShowPost(BaseModel):
    post_id: uuid.UUID
    title: str
    content: str
    image: str | None  # например путь к файлу
    created_at: datetime
    updated_at: datetime
    user: ShowUser
    categories: list[ShowCategory]


class PostCreate(BaseModel):
    title: str
    content: str
    image: str | None
    category_ids: list[uuid.UUID]  = []
