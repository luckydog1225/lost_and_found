"""根据模型定义，在 MySQL 中创建所有表。"""

from app.database import Base, engine
from app.models import User  # noqa: F401 — 必须导入，create_all 才能发现 User 表


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")


if __name__ == "__main__":
    init_db()
