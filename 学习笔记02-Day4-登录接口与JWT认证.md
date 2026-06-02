# 失物招领（Lost and Found）— 学习笔记 02

> **本篇主题：** Day 4 — 登录接口 + JWT 认证 + 项目文档 + Git 推送  
> **计划日程：** 5/30（周六）  
> **项目路径：** `D:\projects\lost-and-found`  
> **笔记用途：** 记录登录/JWT 实现过程、踩坑、核心代码理解、简历与面试素材  

---

## 一、本篇概述（今天具体干了什么）

**今日目标（来自周计划）：**

| 任务 | 完成情况 |
|------|----------|
| 实现 `POST /auth/login`（校验密码 + 签发 JWT） | ✅ |
| 实现 `GET /auth/me`（Bearer Token 获取当前用户） | ✅ |
| Postman / Swagger 测通登录链路 | ✅ |
| 编写 `requirements.txt` | ✅ |
| 编写 `README.md` 初稿 | ✅ |
| 配置 `.env` 中 `JWT_SECRET_KEY` | ✅ |
| Git 提交并推送到 Gitee | ✅ |
| 算法：LeetCode 125 + 20 | 自行安排 |

**一句话描述：**  
在注册 + bcrypt 基础上，完成用户登录与 JWT 无状态认证，并补充项目依赖文档与版本管理。

**当前阶段（更新）：**  
用户认证模块（注册 + 登录 + JWT）已完成；下一步为 Post 表与帖子 CRUD。

---

## 二、技术栈（本篇新增）

| 类别 | 技术 | 用途 |
|------|------|------|
| JWT | python-jose | 签发与解析 `access_token` |
| 认证方式 | Bearer Token | `Authorization: Bearer <token>` |
| 依赖注入 | `HTTPBearer` + `get_current_user` | 受保护接口统一鉴权 |
| 项目文档 | README.md、requirements.txt | 协作与部署说明 |

---

## 三、项目结构（本篇变动）

```
lost-and-found/
├── app/
│   ├── security.py       # 新增：create_access_token / decode_access_token
│   ├── deps.py           # 新增：HTTPBearer、bearer_scheme、get_current_user
│   ├── routers/auth.py   # 新增：POST /login、GET /me
│   └── schemas/user.py   # 新增：UserLogin、TokenResponse
├── requirements.txt      # 新建：锁定依赖版本
├── README.md             # 新建：快速开始、接口表、Postman 流程
├── .env.example          # 新增：JWT_SECRET_KEY、JWT_EXPIRE_MINUTES
└── 使用说明.txt          # 更新：登录与 /me 测试说明
```

**仍不提交 Git：** `.env`（含数据库密码、JWT 密钥）

---

## 四、学习进度记录 — Day 4

### 4.1 新增接口一览

| 方法 | 路径 | 是否需要 Token | 成功响应 |
|------|------|----------------|----------|
| POST | `/auth/login` | 否 | `{ "access_token", "token_type": "bearer" }` |
| GET | `/auth/me` | **是** | `{ id, username, email, created_at }` |

与 Day 3 对比：

| | register | login | me |
|---|----------|-------|-----|
| 写数据库 | ✅ INSERT | ❌ | ❌ 只 SELECT |
| bcrypt | hash_password | verify_password | 不用 |
| JWT | 不用 | 签发 | 解析 + 鉴权 |

---

### 4.2 登录流程（必须能口述）

```
客户端 POST /auth/login { username, password }
    ↓
UserLogin 校验（不合法 → 422）
    ↓
get_db() 注入数据库会话
    ↓
按 username 查 users 表
    ↓
verify_password(明文, password_hash)
    ↓ 失败
401「用户名或密码错误」（故意不区分「用户不存在」和「密码错」）
    ↓ 成功
create_access_token(user.id) → 返回 TokenResponse
```

**关键代码位置：** `app/routers/auth.py` → `login()`

---

### 4.3 JWT 流程（必须能口述）

**JWT 结构（三段，用 `.` 连接）：**

```
Header.Payload.Signature
```

**本项目 Payload 只放两样：**

| 字段 | 含义 |
|------|------|
| `sub` | 用户 id（字符串形式） |
| `exp` | 过期时间（UTC） |

**签发：** `security.py` → `create_access_token(user_id)`  
**解析：** `security.py` → `decode_access_token(token)` → 成功返回 `int` 用户 id，失败返回 `None`

**环境变量（`.env`）：**

| 变量 | 说明 |
|------|------|
| `JWT_SECRET_KEY` | 签名密钥，泄露则别人可伪造 Token |
| `JWT_EXPIRE_MINUTES` | 有效期（分钟），默认 1440 = 24 小时 |

---

### 4.4 受保护接口 `/auth/me`（依赖注入链）

```
客户端 GET /auth/me
Header: Authorization: Bearer <access_token>
    ↓
HTTPBearer 从 Header 取出 token 字符串
    ↓
decode_access_token → user_id
    ↓ 失败
401「无效或已过期的令牌」
    ↓ 成功
get_db() + 按 id 查 User
    ↓ 用户已删
401「用户不存在」
    ↓
me() 收到 current_user，转成 UserResponse 返回
```

**为什么要 decode 之后还查库？**

1. Token 只证明「签发时是谁」，用户可能已被删除  
2. 需要返回最新的 username、email 等  
3. 以后封号、改资料也要以数据库为准  

**关键代码位置：** `app/deps.py` → `get_current_user()`  
**路由写法模板（Day 5+ 发帖会复用）：**

```python
def some_api(current_user: User = Depends(get_current_user)):
    author_id = current_user.id
```

---

### 4.5 新增 Schema

| 类名 | 方向 | 字段 | 说明 |
|------|------|------|------|
| `UserLogin` | 请求 | username, password | 比注册少 email |
| `TokenResponse` | 响应 | access_token, token_type | 不返回用户信息 |
| `UserResponse` | 响应 | id, username, email, created_at | `/me` 与注册共用 |

---

### 4.6 Postman / Swagger 测通步骤

**1. 注册（若还没有测试账号）**

```
POST http://127.0.0.1:8000/auth/register
Body (JSON):
{
  "username": "test01",
  "email": "test01@example.com",
  "password": "123456"
}
```

**2. 登录**

```
POST http://127.0.0.1:8000/auth/login
Body:
{
  "username": "test01",
  "password": "123456"
}
```

复制响应中的 `access_token`。

**3. 当前用户**

```
GET http://127.0.0.1:8000/auth/me
Headers:
  Authorization: Bearer <粘贴 access_token>
```

**Swagger 快捷方式：**  
打开 http://127.0.0.1:8000/docs → 先调 `/auth/login` → 点右上角 **Authorize** → 填入 token（可只填 token，Swagger 会自动加 Bearer）→ 再调 `/auth/me`。

---

### 4.7 Git 提交记录（今天）

| 提交 | 说明 |
|------|------|
| `40486ee` | `feat: 实现登录接口与 JWT 认证，添加 requirements.txt 和 README` |
| `2bd580a` | `docs: 补充登录与 JWT 相关代码注释` |

**常用命令：**

```powershell
git status
git add .env.example app/ README.md requirements.txt 使用说明.txt
git commit -m "feat: 实现登录接口与 JWT 认证，添加 requirements.txt 和 README"
git push origin master
```

**commit 怎么写：**

- 新功能 → `feat: ...`
- 只改注释/文档 → `docs: ...`
- 不要提交 `.env`

---

### 4.8 关键命令

```powershell
# 安装 JWT 依赖（已写入 requirements.txt）
pip install "python-jose[cryptography]"

# 启动服务
.\venv\Scripts\uvicorn.exe app.main:app --reload

# API 文档
# http://127.0.0.1:8000/docs
```

---

## 五、遇到的问题与解决方法

### 问题 1：登录返回 500，提示设置 JWT_SECRET_KEY

**现象：** `POST /auth/login` 密码正确仍 500。  
**原因：** `.env` 里只有 `DATABASE_URL`，没有 `JWT_SECRET_KEY`。  
**解决：** 参照 `.env.example` 添加：

```env
JWT_SECRET_KEY=一串足够长的随机字符
JWT_EXPIRE_MINUTES=1440
```

保存后**重启 uvicorn**（改 `.env` 后建议重启，不要只依赖 reload）。

**收获：** 密钥不进 Git；功能依赖的配置要在 `.env.example` 里写清楚。

---

### 问题 2：Postman 调 `/auth/me` 返回 403

**原因：** 未带 `Authorization` 头，或没写 `Bearer ` 前缀。  
**解决：** Header 必须是：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**收获：** `HTTPBearer` 要求标准 Bearer 格式；403 多半是「没带 token」，401 多半是「token 错/过期」。

---

### 问题 3：Token 无效 / 401

**常见原因：**

| 原因 | 处理 |
|------|------|
| token 复制少了或多了一个字符 | 重新从 login 响应复制 |
| token 已过期 | 重新 login |
| 改了 `JWT_SECRET_KEY` | 旧 token 全部失效，需重新登录 |
| 用了别人的 token | 重新 login |

---

### 问题 4：Git 提交说明不知道写什么

**原则：** `-m` 后写「这次完成了什么」，不是「更新代码」。

- 功能：`feat: 实现登录接口与 JWT 认证，添加 requirements.txt 和 README`
- 注释：`docs: 补充登录与 JWT 相关代码注释`

---

## 六、核心知识点速查

### 6.1 认证三件套分工

| 模块 | 文件 | 职责 |
|------|------|------|
| 密码 | `security.py` | `verify_password`（登录时）、`hash_password`（注册时） |
| 令牌 | `security.py` | `create_access_token` / `decode_access_token` |
| 当前用户 | `deps.py` | `get_current_user`（Header → User 对象） |

### 6.2 注册 vs 登录 vs /me 记忆表

```
注册：明文密码 → bcrypt 哈希 → 存库
登录：明文密码 → bcrypt 校验 → 对则签发 JWT
/me：  只认 JWT → 解析 id → 查库 → 返回用户信息
```

### 6.3 JWT 安全要点（面试用）

1. Payload **不要**放密码等敏感信息（JWT 可解码，只是防篡改）  
2. 安全靠 **HTTPS** + **密钥保密** + **过期时间**  
3. `sub` 用 **user id** 比 username 稳定（改用户名不用重新发 token）  
4. 登录错误信息合并为一句，防**用户名枚举**  

### 6.4 本篇必背函数/类

| 符号 | 作用 |
|------|------|
| `UserLogin` | 登录请求体 |
| `TokenResponse` | 登录返回 token |
| `verify_password` | 校验密码 |
| `create_access_token` | 签发 JWT |
| `decode_access_token` | 解析 JWT → user_id |
| `HTTPBearer` | 从 Header 取 token |
| `get_current_user` | 依赖：token → ORM User |
| `login()` | 登录路由 |
| `me()` | 受保护路由示例 |

---

## 七、自检清单（能答即过关）

1. 登录成功后返回什么？为什么不直接返回用户信息？  
2. JWT 的 `sub` 和 `exp` 各表示什么？  
3. `get_current_user` 里为什么要先 decode 再查数据库？  
4. `Depends(get_current_user)` 在 FastAPI 里什么时候执行？  
5. `.env` 里哪两个变量是 JWT 必需的？  
6. Postman 测 `/auth/me` 要设哪个 Header？  
7. bcrypt 和 JWT 各解决什么问题？（一个管「密码对不对」，一个管「之后请求是不是已登录」）  

---

## 八、简历项目描述（更新版）

### 版本 A：精简版

> 失物招领后端 API | Python, FastAPI, MySQL, JWT  
> 实现用户注册、登录与 JWT 认证，bcrypt 存储密码，RESTful API + Swagger 测试。

### 版本 B：可追加的一条 bullet

- 基于 JWT 实现无状态用户认证，通过 FastAPI 依赖注入封装 `get_current_user`，供受保护接口复用

### 版本 C：技能关键词（追加）

`JWT` `python-jose` `Bearer Token` `依赖注入`

---

## 九、面试可能问到的问题（本篇）

1. **Session 和 JWT 区别？**  
   Session 状态在服务端；JWT 状态主要在客户端，服务端只验签。本项目用 JWT，便于扩展、符合常见 API 实践。

2. **Token 放哪里？**  
   Header：`Authorization: Bearer <token>`（也可放 Cookie，但有 XSS/CSRF 权衡）。

3. **JWT 丢了怎么办？**  
   在过期前拾取者可冒充用户；缓解：HTTPS、短过期、后续可做 Refresh Token / 登出黑名单。

4. **`Depends` 是什么？**  
   声明处理请求前需要先得到的依赖；可嵌套（`get_current_user` 依赖 `get_db` 和 `HTTPBearer`）。

5. **为什么登录和注册 Schema 分开？**  
   字段不同（登录不需要 email）；接口文档更清晰。

---

## 十、后续学习计划

| 阶段 | 内容 | 状态 |
|------|------|------|
| Day 4 | 登录 + JWT + README + requirements | ✅ 本篇 |
| Day 5 | Post 表、建表、帖子 CRUD | 待做 |
| 进阶 | 单元测试、Docker、前端联调 | 规划中 |

**Day 5 预习：** 创建帖子接口大概率会写：

```python
def create_post(..., current_user: User = Depends(get_current_user)):
    ...
```

---

## 十一、相关文件索引

| 文件 | 本篇改动要点 |
|------|----------------|
| `app/routers/auth.py` | `login()`、`me()` |
| `app/security.py` | JWT 配置、`create_access_token`、`decode_access_token` |
| `app/deps.py` | `bearer_scheme`、`get_current_user` |
| `app/schemas/user.py` | `UserLogin`、`TokenResponse` |
| `requirements.txt` | 含 `python-jose[cryptography]` |
| `README.md` | 接口表、环境变量、Postman 流程 |
| `.env.example` | JWT 配置模板 |

---

*最后更新：2026-06-02*  
*当前进度：Day 4 完成（登录 + JWT + 项目文档 + Git）*  
*上一篇：[学习笔记01.md](./学习笔记01.md)（Day 1～3）*
