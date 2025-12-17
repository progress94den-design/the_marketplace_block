import uuid

from datetime import datetime
from pydantic import BaseModel
from typing import Optional

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
    category_ids: list[uuid.UUID] = []


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_ids: Optional[list[uuid.UUID]] = None
