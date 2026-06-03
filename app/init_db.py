"""根据模型定义，在 MySQL 中创建所有表。"""

from app.database import Base, engine
from app.models import Post, User  # noqa: F401 — 必须导入，create_all 才能发现所有表


def init_db() -> None:
    #根据所有模型定义，在 MySQL 中创建对应的表（如果表已存在，不会重复创建）
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")


if __name__ == "__main__":
    init_db()
