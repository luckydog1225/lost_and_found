'''
这个文件用来定义帖子接口的JSON结构长什么样子
可以理解成：在HTTP层定义两份JSON说明书
一份是客户端发帖的时候要发什么，另一份是后端返回什么
'''

from datetime import datetime

from pydantic import BaseModel, Field,field_validator
from app.models.post import PostType, PostStatus

#BaseModel是Pydantic库中的一个类
#可以进行数据校验，自动解析 JSON，FastAPI 自动识别接口字段，自动生成文档
class PostCreate(BaseModel):
    """客户端发帖时提交的数据。"""

    post_type: PostType
    title:str = Field(min_length = 1,max_length = 100)
    description:str = Field(min_length=1)
    location:str | None = Field(default = None,max_length = 200)

    '''去掉标题和描述两端空白字符，并检查是否为空'''
    #@在python里表示装饰器。作用可以理解为：
    #在定义函数/方法时，顺便告诉python：还要用另一个东西来“包装”或“增强”这个函数
    #@field_validator("title","description")：表示校验title和description两个字段
    #@classmethod：表示这是一个类方法
    @field_validator("title","description")
    @classmethod
    def strip_andcheck_not_empty(cls,v:str)->str:
        #v.strip():去掉首尾空格
        value = v.strip()
        #value：去掉空格后的值，if value表示value非空，raise
        #if not value:表示value为空，则抛出ValueError异常
        #如果去掉空格后为空，则抛出ValueError异常
        if not value:
            raise ValueError("不能为空")
        #如果去掉空格后不为空，则返回去掉空格后的值
        return value



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