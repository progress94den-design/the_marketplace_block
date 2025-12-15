import uuid

from pydantic import BaseModel


class ShowCategory(BaseModel):
    category_id: uuid.UUID
    name: str


class CategoryCreate(BaseModel):
    name: str
