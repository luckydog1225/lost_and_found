from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

#UserRegister：客户端（JSON）→后端。规定注册要传什么、怎么校验
class UserRegister(BaseModel):
    """注册时客户端提交的数据。"""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

#定义一个叫UserLogin的类，继承自BaseModel，表示登录时客户端提交的数据
#UserLogin：客户端（JSON）→后端。规定登录要传什么、怎么校验
#BaseModel是Pydantic库中的一个类
#可以进行数据校验，自动解析 JSON，FastAPI 自动识别接口字段，自动生成文档
class UserLogin(BaseModel):
    """登录时客户端提交的数据。"""

    #Field(...):加校验规则，比如长度、类型等
    #username: str...：表示username字段必须是一个字符串，长度在3到50之间
    username: str = Field(min_length=3, max_length=50)
    #password: str...：表示password字段必须是一个字符串，长度在6到72之间
    password: str = Field(min_length=6, max_length=72)
    #不满足校验规则会直接422，不会进入login函数

#TokenResponse：后端→客户端。规定登录响应返回什么，故意不含password
#定义成功登陆是返回给客户端的数据结构
class TokenResponse(BaseModel):
    """登录成功返回的 JWT。"""

    #access_token: str：表示access_token字段必须是一个字符串
    #access_token是TWJ字符串，是通行证本身
    access_token: str
    #token_type（令牌类型）: str = "bearer"：表示token_type字段必须是一个字符串，默认值为"bearer"
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
