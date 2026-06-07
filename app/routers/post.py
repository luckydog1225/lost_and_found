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
from app.schemas.post import PostListResponse
from fastapi import Query

router = APIRouter(prefix="/api/posts", tags=["帖子"])

#路由装饰器
#@router.post这是一个POST端口（提交数据）
#""表示路径是/api/posts
#response_model成功时按PostResponse格式返回
#status_code=status.HTTP_201_CREATED 表示成功时返回201状态码
@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    payload:PostCreate, #前端发过来的数据，FastAPI自动帮你转成一个PostCreate对象
    db:Session = Depends(get_db), #每个请求临时开一个数据库连接，用完关闭
    current_user:User = Depends(get_current_user), #从请求里取出token→验token→查数据库→返回当前登陆的User对象
):
    #payload.用户填的，current_user.谁发的
    """创建一个Post对象,并把前端发过来的数据赋值给Post对象"""
    post = Post(
        user_id = current_user.id,
        post_type = payload.post_type,
        title = payload.title,
        description = payload.description,
        location = payload.location,
    )

    #写入数据库
    #把post对象加入当前会话的“待提交队列”。但是此时MySQL中还没有这条数据
    db.add(post)
    #真正执行INSERT INTO posts ...语句
    db.commit()
    #从数据库重新读这条记录，更新Python里的post对象（再读一遍，拿到 id、时间戳）
    db.refresh(post)
    return post

#路由装饰器
#@router.get这是一个GET端口（获取数据）
#""表示路径是/api/posts
#response_model成功时按PostListResponse格式返回
@router.get("",response_model = PostListResponse)
def get_posts(
    page:int = Query(1,ge = 1),
    page_size:int = Query(10,ge = 1,le = 50),
    db:Session = Depends(get_db),
):
    """获取帖子列表"""
    offset = (page - 1) * page_size
    total = db.query(Post).count() #告诉前端一共多少条帖子
    posts = (
        db.query(Post)   #从post表查
        .order_by(Post.created_at.desc())  #按创建时间倒序
        .offset(offset)  #跳过前offset条，从第offset+1条开始
        .limit(page_size)  #只取page_size条
        #前面几行还没有去查数据库，他们只是在python里拼好一条查询，相当于：
        #我准备从posts表查，按创建时间倒序，跳过前offset条，只取page_size条
        .all() 
        #执行SQL语句，返回list[Post]。
        # list[Post]表示返回值是一个列表，列表里每个元素都是Post类对象
        # 没有.all()，查询不会真正执行，也拿不到数据
    )

    #把list[Post]转换成list[PostResponse]
    items = [
        #model_validate()：把Post对象转换成PostResponse对象
        #from_attributes = True：允许从Post对象的属性自动填进PostResponse
        PostResponse.model_validate(post,from_attributes = True)
        #for post in posts：遍历list[Post]
        for post in posts
    ]
    #上面这个代码等价于：
    #items = []
    #for post in posts:                                    # 先循环
    #    item = PostResponse.model_validate(post, from_attributes=True)  # 再转换
    #    items.append(item)                                 # 再放进列表

    return PostListResponse(
        items = items,
        total = total,
        page = page,
        page_size = page_size,
    )