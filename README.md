# 失物招领平台 — 后端 API

基于 **FastAPI + MySQL + SQLAlchemy** 的失物招领后端服务，实现用户注册登录（JWT）、帖子发布与查询、仅作者可删除/关闭、我的帖子列表；统一响应 `{code, message, data}` 与全局错误处理（401/403/404/422）。

## 功能

| 方法 | 路径 | 需登录 | 说明 |
|------|------|--------|------|
| GET | `/health` | 否 | 健康检查 |
| POST | `/auth/register` | 否 | 用户注册（bcrypt 存密码） |
| POST | `/auth/login` | 否 | 用户登录，返回 JWT |
| GET | `/auth/me` | **是** | 获取当前用户信息 |
| POST | `/api/posts` | **是** | 发布失物/招领帖子 |
| GET | `/api/posts` | 否 | 帖子分页列表（`page`、`page_size`、`type`） |
| GET | `/api/posts/mine` | **是** | 我的帖子列表（同上查询参数） |
| GET | `/api/posts/{id}` | 否 | 帖子详情；不存在返回 404 |
| PATCH | `/api/posts/{id}/close` | **是** | 关闭帖子（仅作者）；已关闭返回 400 |
| DELETE | `/api/posts/{id}` | **是** | 删除帖子（仅作者） |

交互式文档：启动后访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 错误响应

业务错误与 HTTP 状态码一致，统一格式：

```json
{"code": 401, "message": "无效或已过期的令牌", "data": null}
```

| code | 常见场景 |
|------|----------|
| 401 | 未登录、token 无效或过期 |
| 403 | 已登录但无权操作（如删除/关闭他人帖子） |
| 404 | 资源不存在，或请求路径不存在 |
| 422 | 请求参数校验失败（`data` 为校验详情） |

成功时：`{"code": 200, "message": "...", "data": {...}}`

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

## Swagger / Postman 测试流程

1. **注册** `POST http://127.0.0.1:8000/auth/register`  
   Body (JSON)：`{"username":"test01","email":"test01@example.com","password":"123456"}`

2. **登录** `POST http://127.0.0.1:8000/auth/login`  
   Body：`{"username":"test01","password":"123456"}`  
   复制响应 `data` 中的 `access_token`。

3. **当前用户** `GET http://127.0.0.1:8000/auth/me`  
   Headers：`Authorization: Bearer <access_token>`

4. **发帖** `POST http://127.0.0.1:8000/api/posts`  
   Headers：`Authorization: Bearer <access_token>`  
   Body (JSON)：`{"post_type":"lost","title":"黑色钱包","description":"图书馆三楼丢失","location":"图书馆"}`  
   `post_type` 取值：`lost`（失物）或 `found`（招领）；`location` 可省略。

5. **帖子列表** `GET http://127.0.0.1:8000/api/posts?page=1&page_size=10&type=lost`  
   无需 Token。`type` 可选：`lost` / `found`。响应 `data` 含 `items`、`total`、`page`、`page_size`。

6. **帖子详情** `GET http://127.0.0.1:8000/api/posts/1`  
   将 `1` 换成实际帖子 `id`，无需 Token。不存在时返回 404。

7. **我的帖子** `GET http://127.0.0.1:8000/api/posts/mine?page=1&page_size=10`  
   需 Token。只返回当前用户发布的帖子。

8. **关闭帖子** `PATCH http://127.0.0.1:8000/api/posts/1/close`  
   需 Token，仅作者可操作。成功时 `data.status` 为 `closed`。

9. **删除帖子** `DELETE http://127.0.0.1:8000/api/posts/1`  
   需 Token，仅作者可操作。成功时 `data` 为 `null`。

**权限与错误自测（可选）：**

- 不带 Token 调 `/auth/me` → 401  
- 登录后删除/关闭他人帖子 → 403  
- `GET /api/posts/99999` → 404  
- `GET /not-exist` → 404，`message` 为「接口不存在」

## 项目结构

```
app/
├── main.py          # 应用入口、全局异常处理
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
