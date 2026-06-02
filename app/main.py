#引入FastAPI框架
from fastapi import FastAPI

from app.routers import auth

#创建FastAPI实例，设置标题为“失物招领”
app = FastAPI(title="失物招领")

#把auth.router（包含所有路由）注册到app上，这样就可以访问/auth/register了
app.include_router(auth.router)

#给你的 “失物招领” 服务，加一个/health 接口，别人访问这个地址时
#就返回 {"status": "ok"}，用来确认服务还在正常运行。
@app.get("/health")
def health():
    return {"status": "ok"}
