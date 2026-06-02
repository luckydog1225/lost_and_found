'''
这个文件用来定义用户模型，也就是User表长什么样子
'''

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    #id:主键，整数，自增，不能为空
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    #username:用户名，字符串，不能为空，唯一
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    #email:邮箱，字符串，不能为空，唯一
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    #password_hash:密码哈希，字符串，不能为空
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    #created_at:创建时间，日期时间，不能为空，默认当前时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        #默认时间是当前时间
        server_default=func.now(),
        #不能为空
        nullable=False,
    )