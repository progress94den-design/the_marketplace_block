import uuid

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.app.db.base import Base


class Post(Base):
    __tablename__ = "posts"

    post_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    image = Column(String(255), nullable=True)  # например путь к файлу
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    user = relationship("User", back_populates="posts")

    categories = relationship("Category", secondary="post_category_associations", back_populates="posts")
