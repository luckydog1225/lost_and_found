# 失物招领平台 — 后端 API

基于 **FastAPI + MySQL + SQLAlchemy** 的失物招领后端服务，当前已实现用户注册、登录（JWT）、发帖（失物/招领）与基础健康检查。

## 功能

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/auth/register` | 用户注册（bcrypt 存密码） |
| POST | `/auth/login` | 用户登录，返回 JWT |
| GET | `/auth/me` | 获取当前用户（需 Bearer Token） |
| POST | `/api/posts` | 发布失物/招领帖子（需 Bearer Token） |

交互式文档：启动后访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 环境要求

- Python 3.11+
- MySQL 8.x（数据库名建议：`lost_and_found`）

## 快速开始

```bash
# 1. 创建虚拟环境并安装依赖
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 2. 配置环境变量
copy .env.example .env
# 编辑 .env：填写 DATABASE_URL、JWT_SECRET_KEY

# 3. 初始化数据库表（首次）
.\venv\Scripts\python.exe -m app.init_db

# 4. 启动服务
.\venv\Scripts\uvicorn.exe app.main:app --reload
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | SQLAlchemy 连接串，如 `mysql+pymysql://root:密码@localhost:3306/lost_and_found` |
| `JWT_SECRET_KEY` | JWT 签名密钥，请使用足够长的随机字符串 |
| `JWT_EXPIRE_MINUTES` | 令牌有效期（分钟），默认 `1440` |

## Postman 测试流程

1. **注册** `POST http://127.0.0.1:8000/auth/register`  
   Body (JSON)：`{"username":"test01","email":"test01@example.com","password":"123456"}`

2. **登录** `POST http://127.0.0.1:8000/auth/login`  
   Body：`{"username":"test01","password":"123456"}`  
   复制响应中的 `access_token`。

3. **当前用户** `GET http://127.0.0.1:8000/auth/me`  
   Headers：`Authorization: Bearer <access_token>`

4. **发帖** `POST http://127.0.0.1:8000/api/posts`  
   Headers：`Authorization: Bearer <access_token>`  
   Body (JSON)：`{"post_type":"lost","title":"黑色钱包","description":"图书馆三楼丢失","location":"图书馆"}`  
   `post_type` 取值：`lost`（失物）或 `found`（招领）；`location` 可省略。

## 项目结构

```
app/
├── main.py          # 应用入口
├── database.py      # 数据库连接
├── deps.py          # 依赖注入（会话、当前用户）
├── security.py      # 密码哈希与 JWT
├── models/          # SQLAlchemy 模型（users、posts）
├── schemas/         # Pydantic 请求/响应
└── routers/         # API 路由（auth、post）
```

## 技术栈

Python · FastAPI · MySQL · SQLAlchemy · Pydantic · bcrypt · JWT (python-jose) · Uvicorn

## 许可证

个人学习项目，暂未指定开源协议。
