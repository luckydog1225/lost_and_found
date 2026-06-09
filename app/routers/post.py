'''
发帖
想象成一个发帖办事窗口：有人在前端点【发启事】，请求会进这个文件里的函数
由它完成「验身份 → 记进数据库 → 把结果告诉对方」
'''
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models.post import Post,PostType,PostStatus
from app.models.user import User
from app.schemas.post import PostCreate, PostListResponse, PostResponse
from app.schemas.response import success,ApiResponse

router = APIRouter(prefix="/api/posts", tags=["帖子"])

#路由装饰器
#@router.post这是一个POST端口（提交数据）
#""表示路径是/api/posts
#response_model成功时按ApiResponse[PostResponse]格式返回,也就是统一的返回外壳
#status_code=status.HTTP_201_CREATED 表示成功时返回201状态码
@router.post("", response_model=ApiResponse[PostResponse], status_code=status.HTTP_201_CREATED)
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
    return success(
        data=PostResponse.model_validate(post, from_attributes=True),
        message="发帖成功",
    )

#路由装饰器
#@router.get这是一个GET端口（获取数据）
#""表示路径是/api/posts
#response_model成功时按ApiResponse[PostListResponse]格式返回,也就是统一的返回外壳
@router.get("",response_model = ApiResponse[PostListResponse])
def get_posts(
    #Query是FastAPI里的一个函数，用来从URL中获取参数
    #1,ge = 1：表示page必须大于等于1
    #10,ge = 1,le = 50：表示page_size必须大于等于1，小于等于50。10是默认值，如果前端不传，就默认10
    page:int = Query(1,ge = 1),
    page_size:int = Query(10,ge = 1,le = 50),
    #type:Optional[PostType] = Query(None,description="按类型筛选：lost或found")
    #表示type是可选的，如果不传，就默认None。
    #description是给接口文档用的说明文字，不参与实际业务逻辑
    #在FastAPI里，Query(..., description="...") 会把这段文字写进 OpenAPI 文档（Swagger）。
    #方便前端或测试的人知道，这个参数可选，用来按【失物】或【招领】筛选帖子
    type:Optional[PostType] = Query(None,description="按类型筛选：lost或found"),
    db:Session = Depends(get_db),
):
    '''获取帖子列表'''
    #offset：跳过前offset条，从第offset+1条开始
    #比如page=1,page_size=10，则offset=0，从第1条开始
    #比如page=2,page_size=10，则offset=10，从第11条开始
    #比如page=3,page_size=10，则offset=20，从第21条开始
    offset = (page - 1) * page_size

    #query = db.query(Post)：从posts表查.posts表存的是平台上每一条启事（一条记录=一篇帖子）
    query = db.query(Post)
    #type是URL查询参数。如果前端传了type，就按type筛选。
    # 如果没传，默认为None，就查所有帖子。相当于：SELECT * FROM posts;
    if type is not None:
        #.filter(...)给查询加where条件
        #Post.post_type模型里【帖子类型】这一列，值等于type（URL传进来的）
        query = query.filter(Post.post_type == type)
    
    total = query.count() #告诉前端一共多少条帖子
    posts = (
        query   #从post表查
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

    #success会自动补上code=200,message="success",不用手动写了
    return success(
        data = PostListResponse(
            items = items,
            total = total,
            page = page,
            page_size = page_size,
        )
    )

'''
对应的SQL语句：
SELECT COUNT(*) FROM posts WHERE post_type = 'lost';
或
SELECT * FROM posts
WHERE post_type = 'lost'
ORDER BY created_at DESC
LIMIT 10 OFFSET 0;
'''



'''查看当前登陆用户自己发的帖子'''
@router.get("/mine",response_model = ApiResponse[PostListResponse])
def get_my_posts(
    page:int = Query(1,ge = 1),
    page_size:int = Query(10,ge = 1,le = 50),
    #Optional是Python typing模块里的类型标注工具
    #用来告诉Python/FastAPI：这个值可以是某种类型，也可以是None
    type:Optional[PostType] = Query(None,description="按类型筛选：lost或found"),
    db:Session = Depends(get_db),
    current_user:User = Depends(get_current_user),
):
    """查看当前登陆用户自己发的帖子"""
    offset = (page - 1) * page_size
    query = db.query(Post).filter(Post.user_id == current_user.id)

    if type is not None:
        #筛选符合前端输入的type帖子
        query = query.filter(Post.post_type == type)

    total = query.count()
    #查当前页数据
    posts = (
        #按创建时间倒序
        query.order_by(Post.created_at.desc())
        #跳过前offset条，从第offset+1条开始
        .offset(offset)
        #只取page_size条
        .limit(page_size)
        .all()
        #执行SQL语句，返回list[Post]。
        # 没有.all()，查询不会真正执行，也拿不到数据
    )
    #把list[Post]转换成list[PostResponse]
    items = []
    for post in posts:
        #把Post对象转换成PostResponse对象
        item = PostResponse.model_validate(post, from_attributes=True)
        #把PostResponse对象放进列表
    items.append(item)
    return success(
        data=PostListResponse(
            items = items,
            total = total,
            page = page,
            page_size = page_size,
        )
    )



"""帖子详情——用户点进某一条启事，看完整内容"""
#路由装饰器
#@router.get这是一个GET端口（获取数据）
#"/{post_id}"表示路径是/api/posts/{post_id}，{}是占位符，post_id是占位符的值
#可以是任何字符串，比如/api/posts/1，/api/posts/2，/api/posts/3，等等
#response_model成功时按ApiResponse[PostResponse]格式返回,也就是统一的返回外壳
@router.get("/{post_id}",response_model = ApiResponse[PostResponse])
def get_post(
    post_id:int, #前端发过来的帖子id
    db:Session = Depends(get_db), #每个请求临时开一个数据库连接，用完关闭
):
    """获取帖子详情"""
    #post_id是来自url的参数。url：网址=浏览器或Postman访问的完整地址
    #如果查到了，返回值是Post对象
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        #如果查不到，返回404错误
        raise HTTPException(status_code=404,detail="帖子不存在")
    #把Post对象转换成PostResponse对象，并返回给前端
    return success(
        data=PostResponse.model_validate(post, from_attributes=True)
    )

'''
把帖子状态标位已解决，且只有发帖本人能操作
post里面status = open（默认）
status = closed（已解决）
'''
#patch:对已有资源做部分修改。这里就是对帖子状态做部分修改
@router.patch("/{post_id}/close",response_model = ApiResponse[PostResponse])
def close_post(
    post_id:int,
    db:Session = Depends(get_db),
    current_user:User = Depends(get_current_user),
):
    """把帖子状态标位已解决"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        #HTTPException:是FastAPI里用来主动告诉前端出错了的机制
        #正常流程用return success返回成功；遇到不该继续的情况
        #raise HTTPException中断执行，并返回对应的HTTP错误
        raise HTTPException(status_code=404,detail="帖子不存在")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403,detail="无权操作他人的帖子")

    if post.status == PostStatus.CLOSED:
        raise HTTPException(status_code=400,detail="帖子已解决")

    post.status = PostStatus.CLOSED

    db.commit()
    db.refresh(post)

    return success(
        data = PostResponse.model_validate(post, from_attributes=True),
        message = "帖子已解决"
    )


'''
DELETE /api/posts/{post_id}：删除帖子，且只有发帖本人能删
'''
@router.delete("/{post_id}",response_model = ApiResponse[None])
def delete_post(
    #前端发过来的帖子id
    post_id:int,
    #每个请求临时开一个数据库连接，用完关闭
    #Depends（）：依赖注入，函数接口需要什么东西，你告诉FastAPI去调用谁，
    #FastAPI会先执行那个函数，再把返回值赋值给db
    db:Session = Depends(get_db),
    #从请求里取出token→验token→查数据库→返回当前登陆的User对象
    #get_current_user:从请求头里读token；解析token，拿到用户id；
    #按用户id查数据库，拿到User对象（数据库里某一个用户的完整信息）；返回给current_user
    current_user:User = Depends(get_current_user),
):
    """删除帖子"""
    #Post是一个类，对应的是posts表
    #post是变量名，存的是从数据库查出来的那一条帖子
    #post_id是前端发过来的帖子编号
    #query(Post)：从posts表查
    #filter(Post.id == post.id)：where条件，帖子id等于post_id。取出来赋给post
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404,detail="帖子不存在")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403,detail="无权删除他人的帖子")
    
    #删除帖子
    #标记要删掉这条。并不是立刻删，而是把这条记录放进会话的待删除队列
    #相当于告诉SQLAichemy：这条帖子我准备删掉
    db.delete(post)
    #真正执行DELETE FROM posts WHERE id = post_id;语句
    db.commit()
    #返回成功信息
    return success(
        message="删除帖子成功",
    )
