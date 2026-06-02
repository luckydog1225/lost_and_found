'''
这个文件用来连接数据库
'''


import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

#os.getenv("DATABASE_URL") 从 .env 文件中获取变量名为DATABASE_URL的值
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("请在 .env 文件中设置 DATABASE_URL")

#engine是python和MySQL之间的桥梁
#engine本身一般不直接写业务SQL，而是：把pythoh里的操作（增删改查）转换成MySQL
#create_engine()用链接地址创建一个引擎，之后所有数据库操作都通过engine来完成
#echo=True 表示在控制台打印出所有执行的SQL语句，方便调试
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
