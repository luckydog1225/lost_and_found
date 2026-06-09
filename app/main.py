"""
FastAPI 应用入口：注册路由、统一错误响应、健康检查。
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routers import auth, post
from app.schemas.response import ApiResponse, success

app = FastAPI(title="失物招领")

app.include_router(auth.router)
app.include_router(post.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """接住 HTTPException 及 Starlette 404 等，统一为 {code, message, data}。"""
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    if exc.status_code == 404 and message == "Not Found":
        message = "接口不存在"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": message,
            "data": None,
        },
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """接住 FastAPI/Pydantic 自动抛出的 422 参数校验错误。"""
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "请求参数校验失败",
            "data": exc.errors(),
        },
    )


@app.get("/health", response_model=ApiResponse[dict[str, Any]])
def health():
    """健康检查，确认服务正常运行。"""
    return success(data={"status": "ok"})
