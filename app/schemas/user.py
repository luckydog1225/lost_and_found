from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """注册时客户端提交的数据。"""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class UserResponse(BaseModel):
    """返回给客户端的用户信息（不含密码）。"""

    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
