"""
帖子模型：失物 / 招领信息，对应 MySQL 中的 posts 表。
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PostType(str, enum.Enum):
    """帖子类型：失物 或 招领。"""

    LOST = "lost"
    FOUND = "found"


class PostStatus(str, enum.Enum):
    """帖子状态：进行中 或 已解决。"""

    OPEN = "open"
    CLOSED = "closed"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 发帖用户，关联 users.id
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    # 失物 / 招领
    post_type: Mapped[PostType] = mapped_column(
        Enum(PostType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # 丢失或拾取地点（可选）
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PostStatus.OPEN,
        server_default=PostStatus.OPEN.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    author: Mapped["User"] = relationship("User", back_populates="posts")
