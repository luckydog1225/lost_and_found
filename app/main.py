#引入FastAPI框架
from fastapi import FastAPI

from app.routers import auth, post

#创建FastAPI实例，设置标题为“失物招领”
app = FastAPI(title="失物招领")

# 注册路由：/auth/* 认证，/api/posts 发帖/列表/详情
app.include_router(auth.router)
app.include_router(post.router)

#给你的 “失物招领” 服务，加一个/health 接口，别人访问这个地址时
#就返回 {"status": "ok"}，用来确认服务还在正常运行。
@app.get("/health")
def health():
    return {"status": "ok"}
