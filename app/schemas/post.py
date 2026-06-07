'''
这个文件用来定义帖子接口的JSON结构长什么样子
可以理解成：在HTTP层定义两份JSON说明书
一份是客户端发帖的时候要发什么，另一份是后端返回什么
'''

from datetime import datetime

from pydantic import BaseModel, Field
from app.models.post import PostType, PostStatus

class PostCreate(BaseModel):
    """客户端发帖时提交的数据。"""

    post_type: PostType
    title:str = Field(min_length = 1,max_length = 100)
    description: str = Field(min_length=1)
    location:str | None = Field(default = None,max_length = 200)

class PostResponse(BaseModel):
    """后端返回的帖子信息。"""
    id:int 
    user_id:int 
    post_type:PostType 
    title:str = Field(min_length = 1,max_length = 100)
    description:str = Field(min_length=1)
    location:str | None = Field(default = None,max_length = 200)
    status:PostStatus 
    created_at:datetime 
    updated_at:datetime 

    model_config = {"from_attributes": True}
    
class PostListResponse(BaseModel):
    """后端返回的帖子列表信息。这一页里面返回一行行帖子信息。"""
    items:list[PostResponse]              #列表里装的是PostResponse对象，每项是一个帖子
    total:int                      #总帖子数
    #ge在Pydantic的Field里=greater than or equal,大于等于.le表示小于等于
    page:int = Field(ge = 1)      #当前页码
    page_size:int = Field(ge = 1,le = 50) #每页帖子数，每页最小1条，最大50条