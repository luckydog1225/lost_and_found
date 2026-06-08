'''
统一API响应格式：{code,message,data}
所有接口成功时，都按这个外壳返回：data里才是具体业务数据
'''

from typing import Generic,Optional,TypeVar
from pydantic import BaseModel

#T是一个类型占位符
#TypeVar:创建一个 “类型占位符”，用来写泛型
#表示 “某种类型，但具体类型要到调用时才确定”
T = TypeVar("T")

#BaseModel:让这个类变成Pydantic的模型：自动校验，自动转JSON，自动生成接口文件
#Generic[T]:让这个类变成泛型类（Generic=泛型）
#这个ApiResponse可以搭配任意类型T使用
class ApiResponse(BaseModel,Generic[T]):
    '''统一响应外壳'''
    code:int = 200 #状态码：成功是200，失败是400、500等
    message:str = "success" #消息：成功是success，失败是error等
    #数据：可以是任意类型T，但具体类型要到调用时才确定，默认是None
    #表示 data 可以放任何东西：数字、字符串、字典、对象、列表、null...
    data:Optional[T] = None 

#函数助手，避免每个接口都手写ApiResponse(code=200,message="success",data=...)
#以后路由里写成return success(data=...) 就会自动变成ApiResponse(code=200,message="success",data=...)
#success是专门用来拼成功响应的快捷函数
def success(
    data=None,#业务数据，不传时默认None
    message:str="success",#消息，不传时默认success
    code:int=200,#状态码，不传时默认200
)->ApiResponse:#返回值类型：一个ApiResponse对象
    '''
    构造成功响应
    路由里面写return success(data=...) 就会自动变成ApiResponse(code=200,message="success",data=...)
    '''
    return ApiResponse(code=code,message=message,data=data)
