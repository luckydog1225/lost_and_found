from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserResponse
from app.security import hash_password

#prefix='/auth' 表示所有路由都以 /auth 开头
#tags=["认证"] 表示在swagger文档里归到【认证】分组
router = APIRouter(prefix="/auth", tags=["认证"])

#下面这一行定义：这是什么接口、成功时返回什么、状态码是多少
#/register 表示接口路径是 /auth/register
#response_model=UserResponse成功时，把返回值转成UserResponse再发给客户端。
#UserResponse只有id、username、email、created_at四个字段，不会返回password_hash（在D:\projects\lost-and-found\app\schemas\user.py）
#status_code=status.HTTP_201_CREATED 表示成功时返回201状态码
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
#payload: UserRegister：前端发过来的JSON数据，FastAPI自动帮你转成一个UserRegister对象
#并且自动校验类型和必填项，不合法会直接422，不会进入register函数
#get_db():是FastAPI的依赖注入，可以“每个请求一个数据库连接，用完就关”，既安全又高效
#比如A和B同时注册，get_db()会自动为A和B分别创建一个数据库连接，用完就关，不会互相影响
#Depends(get_db)：FastAPI 在处理这个请求时，会先调用 get_db()，把得到的 db 传进 register 函数。
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """用户注册：检查重复 → 加密密码 → 写入 users 表。"""
    #检查用户名是否已存在（在模型里设置了unique =True）
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")

    #检查邮箱是否已存在（在模型里设置了unique =True）
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    #创建一个User对象，并把前端发过来的数据赋值给User对象
    user = User(
        username=payload.username,
        email=payload.email,
        #把前端发过来的密码加密(hash_possword)后赋值给password_hash
        password_hash=hash_password(payload.password),
    )

    #写入user数据库
    #把user加入当前会话的“待提交队列”。但是此时MySQL中还没有这条数据
    db.add(user)
    #真正执行INSERT INTO users ...语句
    db.commit()
    #从数据库重新读这条记录，更新Python里的user对象（再读一遍，拿到 id、时间戳）
    db.refresh(user)

    #返回user对象，包括id、username、email、created_at四个字段
    return user
