import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import HTTPException, status
from jose import JWTError, jwt


'''读.env配置的标准写法'''
#从环境变量里取名为JWT_SECRET_KEY的值，赋值给JWT_SECRET_KEY
#getenv：get environment variable，获取环境变量
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
#JWT_ALGORITHM：变量名：JWT用什么算法签名
#“HS256”：HMAC-SHA256算法，使用一个密钥进行签名和验证
JWT_ALGORITHM = "HS256"
#“1440”默认值：.env文件里没有JWT_EXPIRE_MINUTES，则默认值为1440分钟
#int()：把字符串转换为整数
#getenv（名，默认值）
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))


def hash_password(password: str) -> str:
    """把明文密码加密成哈希，存入数据库。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

#verify（校验核验），verify_password：验证密码
#plain（明文）_password: str：用户刚输入的明文密码（如‘123456’）
#password_hash（哈希）: str：数据库里存的加密后的密码/哈希字符串（如‘$2b$12$...’）
#-> bool：返回一个布尔值，True表示密码正确，False表示密码错误
def verify_password(plain_password: str, password_hash: str) -> bool:
    """校验明文密码是否和哈希匹配（Day 4 登录时会用到）。"""
    #bcrypt:第三方库，专门做密码哈希与校验
    #checkpw：检查密码是否和哈希匹配
    #bcrypt.checkpw它内部会：从password_hash里取出盐
    #盐：一段随机数据，在加密密码之前混进去，让同样的密码算出来的结果每次都不同。
    #用同样的方式把plain_password加密（此时盐和上一次是一样的），再和password_hash比较，如果一样就返回True，不一样就返回False
    #plain_password.encode("utf-8")：把明文密码转换为字节串
    #password_hash.encode("utf-8")：把哈希字符串转换为字节串
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )

'''签发和解析JWT的函数'''
#create_access_token：创建访问令牌
#user_id: int：当前登录用户的ID
#-> str：返回一个字符串，是JWT令牌本身
def create_access_token(user_id: int) -> str:
    """签发 JWT，payload 里放用户 id（sub）和过期时间（exp）。"""

    if not JWT_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="请在 .env 文件中设置 JWT_SECRET_KEY",
        )

    #datetime.now(timezone.utc)：获取当前时间，并转换为UTC时区
    #timedelta(minutes=JWT_EXPIRE_MINUTES)：计算过期时间，JWT_EXPIRE_MINUTES是.env文件里设置的过期时间（分钟）
    #expire：过期时间
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    #组装payload：payload是JWT的第二部分，里面放用户id和过期时间
    #sub（subject）：JWT标准字段，这里表示这是哪个用户
    #str(user_id)：把用户id转换为字符串
    #exp：JWT标准字段，这里表示过期时间
    payload = {"sub": str(user_id), "exp": expire}
    #jwt.encode():把payload签名成完整的JWT字符串
    #JWT_SECRET_KEY：JWT_SECRET_KEY是.env文件里设置的密钥
    #algorithm=JWT_ALGORITHM：使用JWT_ALGORITHM算法签名
    #返回值：返回一个字符串，是完整的JWT令牌
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

'''这是create_access_token的反函数，把JWT令牌解析成用户id'''
#decode_access_token：解析访问令牌
#token: str：参数：JWT整串
#-> int | None：返回一个整数，是用户id，如果解析失败则返回None
def decode_access_token(token: str) -> int | None:
    """解析 JWT，成功返回用户 id，失败返回 None。"""
    #如果JWT_SECRET_KEY不存在，则返回None
    if not JWT_SECRET_KEY:
        return None
    #try：尝试解析JWT令牌。出错走except
    try:
        #jwt.decode():把JWT整串解析成payload
        #token: JWT整串
        #JWT_SECRET_KEY: JWT_SECRET_KEY是.env文件里设置的密钥
        #algorithms=[JWT_ALGORITHM]:使用JWT_ALGORITHM算法解析
        #返回值：返回一个字典，是payload
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        #payload.get("sub")：从payload里取出sub字段，即用户id
        #user_id：用户id
        #int(user_id)：把用户id转换为整数
        #if user_id is not None else None：如果user_id不为None，则返回user_id，否则返回None
        user_id = payload.get("sub")
        #return int(user_id) if user_id is not None else None：返回用户id
        return int(user_id) if user_id is not None else None
    #except (JWTError, ValueError):：如果解析失败，则返回None
    #JWTError：JWT解析错误
    #ValueError：JWT值错误
    #return None：返回None
    except (JWTError, ValueError):
        return None
