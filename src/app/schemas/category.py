from uuid import UUID
from pydantic import BaseModel


class ShowCategory(BaseModel):
    category_id: UUID
    name: str
