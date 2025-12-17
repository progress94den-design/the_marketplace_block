import uuid

from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional, ClassVar, List
from fastapi import Query

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
    categories: List[ShowCategory]


class PostCreate(BaseModel):
    title: str
    content: str
    category_ids: List[uuid.UUID] = []


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_ids: Optional[List[uuid.UUID]] = None


class PostQueryParams(BaseModel):
    MAX_PAGE_SIZE: ClassVar[int] = 10

    search: Optional[str] = Query(default=None, description="Полнотекстовый поиск по заголовку и контенту")
    category_ids: Optional[List[uuid.UUID]] = Query(
        default=None, description="Фильтрация по категориям", alias="category_ids"
    )
    page_number: int = Query(default=1, ge=1, description="Номер страницы")
    page_size: int = Query(
        default=5, ge=1, le=MAX_PAGE_SIZE, description=f"Количество элементов на странице (максимум {MAX_PAGE_SIZE})"
    )

    @property
    def skip(self) -> int:
        return (self.page_number - 1) * self.page_size

    @field_validator("page_size")
    @classmethod
    def validate_page_size(cls, value: int) -> int:
        if value > cls.MAX_PAGE_SIZE:
            return cls.MAX_PAGE_SIZE
        return value
