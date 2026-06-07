"""
帖子模型：失物 / 招领信息，对应 MySQL 中的 posts 表。
属于Model层：不处理HTTP，只定义表结构
跑init_db是SQLAIchemy根据它生成CREATE TABLE posts
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

#类名（父类1，父类2）表示的含义：类名继承了父类1和父类2的属性和方法
#enum.Enum:枚举基类
#枚举：固定可选值的清单，帖子类型只能是失物/招领两种，不能填别的
#用来约束数据，防止随便乱写字符串（比如写错los、foun）
#不用枚举：写type=‘lost’容易手敲错字母，数据库乱数据
#用枚举：只能用PostType.LOST或者PostType.FOUND，写错直接代码报错
#继承str。普通枚举calss A(Enum)：PostType.LOST是枚举对象，不等于普通字符串
#存数据库、前后端传JSON回报错
#加str后，PostType.LOST本质=字符串‘lost’，可以直接存入数据库字段、接口返回json，和普通字符串无缝使用
class PostType(str, enum.Enum):
    """帖子类型：失物 或 招领。"""

    #左边大写：枚举名称（代码里写的常亮名）→程序员写代码用：PostType.LOST
    #右边小写：枚举值（存数据库的实际值）→数据库里存：‘lost’
    LOST = "lost"  #表示发帖人说自己丢了东西
    FOUND = "found" #表示发帖人说自己捡到了东西


class PostStatus(str, enum.Enum):
    """帖子状态：进行中 或 已解决。"""

    OPEN = "open"   #默认open。表示进行中
    CLOSED = "closed" #表示已解决

'''
用python类描述MYSQL里一张叫posts的表
'''
#类名Post
#继承Base：告诉SQLAIchemy这是一个数据库表模型
'''运行init_db时，SQLAIchemy会根据这个类生成类似：
CREATE TABLE posts (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  ...
);
'''
class Post(Base):
    __tablename__ = "posts" #真正在MYSQL里创建的表名
    
    #几乎每一列都长这样：
    #字段名: Mapped[类型] = mapped_column(SQL类型, 约束)
    #id,title是python里访问属性用的名字
    #Mapped[int]：这列在MYSQL里是int类型
    #mapped_column()：真正定义列：主键、长度、能不能为空等
    
    #id列：主键
    #autoincrement=True：插入新行时，自动递增，不用自己填id
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 发帖用户，关联 users.id
    #user_id是外键，关联users表的id字段
    #ForeignKey("users.id")：这一列的值必须能在users表的id里找到；不能凭空写一个不存在的用户
    #nullable=False：不能为空
    #index=True：在MYSQL里创建索引，加速查询
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # 失物 / 招领
    #PostType是枚举类，定义了两个值：PostType.LOST和PostType.FOUND
    post_type: Mapped[PostType] = mapped_column(
        #Enum(PostType, values_callable=lambda x: [e.value for e in x])：这一列的值只能是PostType枚举里的两个值：PostType.LOST和PostType.FOUND
        Enum(PostType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    #标题
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # 丢失或拾取地点（可选）
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)

    status: Mapped[PostStatus] = mapped_column(
        #Enum(PostStatus, values_callable=lambda x: [e.value for e in x])：这一列的值只能是PostStatus枚举里的两个值：PostStatus.OPEN和PostStatus.CLOSED
        Enum(PostStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        #default=PostStatus.OPEN：默认值为PostStatus.OPEN
        default=PostStatus.OPEN,
        #server_default=PostStatus.OPEN.value：在MYSQL里创建时（数据库层面），默认值为PostStatus.OPEN
        server_default=PostStatus.OPEN.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,      #存日期+时间，用datetime类型
        #server_default=func.now()：在MYSQL里创建时（数据库层面），默认值为当前时间
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        #onupdate=func.now()：每次更新时，自动更新为当前时间
        #例如：帖子从open变成closed，updated_at会自动更新为当前时间，但是created_at不会变
        onupdate=func.now(),
        nullable=False,
    )

    #这不是数据库里的一列，而是ORM关系：
    #Mapped["User"]：这个属性应该是一个User对象
    #relationship（）：声明ORM关系，不是mapped_column
    #第一个参数“User”：关联到哪个模型（User表）
    #back_populates = 'posts'：和Users上的posts成对；改一边，另一边也知道怎么连
    author: Mapped["User"] = relationship("User", back_populates="posts")
