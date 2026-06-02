from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

#UserRegister：客户端（JSON）→后端。规定注册要传什么、怎么校验
class UserRegister(BaseModel):
    """注册时客户端提交的数据。"""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

class UserLogin(BaseModel):
    """登录时客户端提交的数据。"""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=72)


class TokenResponse(BaseModel):
    """登录成功返回的 JWT。"""

    access_token: str
    token_type: str = "bearer"


#UserResponse：后端→客户端。规定返回什么，故意不含password
class UserResponse(BaseModel):
    """返回给客户端的用户信息（不含密码）。"""

    id: int
    username: str
    email: str
    created_at: datetime

#model_config = {"from_attributes": True}：允许从User对象的属性自动填进UserResponse
    model_config = {"from_attributes": True}
