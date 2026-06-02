from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.security import decode_access_token

bearer_scheme = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """每个请求单独开一个数据库会话，用完自动关闭。"""
    #SessionLocal()：创建一个数据库会话
    #db = SessionLocal()：把会话赋值给db
    db = SessionLocal()
    #try:：尝试执行下面的代码
    try:
        #yield db：把db交给register函数使用（这里暂停，去执行register里的代码）
        #yield不是普通的return，他表示先交出db，等调用方用完，再回到函数里继续执行
        yield db
    #finally:：无论是否发生异常，都会执行下面的代码
    #db.close()：关闭会话
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """从 Authorization: Bearer <token> 解析当前登录用户。"""
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        #raise HTTPException（异常）主动中断，向客户端返回错误
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
