'''
发帖
想象成一个发帖办事窗口：有人在前端点【发启事】，请求会进这个文件里的函数
由它完成「验身份 → 记进数据库 → 把结果告诉对方」
'''
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.schemas.post import PostCreate, PostResponse
from app.models.user import User
from app.models.post import Post

router = APIRouter(prefix="/api/posts", tags=["帖子"])


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    payload:PostCreate,
    db:Session = Depends(get_db),
    current_user:User = Depends(get_current_user),
):
    #payload.用户填的，current_user.谁发的
    post = Post(
        user_id = current_user.id,
        post_type = payload.post_type,
        title = payload.title,
        description = payload.description,
        location = payload.location,
    )

    db.add(post)
    db.commit()
    db.refresh(post)
    return post
