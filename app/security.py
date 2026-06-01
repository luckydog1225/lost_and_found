import bcrypt


def hash_password(password: str) -> str:
    """把明文密码加密成哈希，存入数据库。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """校验明文密码是否和哈希匹配（Day 4 登录时会用到）。"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )
