from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.response import ApiResponse, success
from app.schemas.user import TokenResponse, UserLogin, UserRegister, UserResponse
from app.security import create_access_token, hash_password, verify_password

# prefix='/auth' 表示所有路由都以 /auth 开头
# tags=["认证"] 表示在 swagger 文档里归到【认证】分组
router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """用户注册：检查重复 → 加密密码 → 写入 users 表。"""
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return success(
        data=UserResponse.model_validate(user, from_attributes=True),
        message="注册成功",
    )


@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """用户登录：校验用户名密码 → 签发 JWT。"""
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    return success(
        data=TokenResponse(access_token=create_access_token(user.id)),
        message="登录成功",
    )


@router.get("/me", response_model=ApiResponse[UserResponse])
def me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息（需携带 Bearer Token）。"""
    return success(
        data=UserResponse.model_validate(current_user, from_attributes=True),
    )
