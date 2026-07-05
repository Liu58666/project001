# AuthService Backend Skeleton (FastAPI + SQLAlchemy + MySQL)

## 目录结构
- `app/`
  - `main.py`：FastAPI 入口，挂载路由，启动时可创建表（开发便捷）。
  - `core/`
    - `config.py`：Pydantic Settings，读取环境变量（DB、JWT、过期时间、bcrypt 参数等）。
    - `security.py`：密码哈希、校验，JWT 生成/解析。
  - `db/`
    - `database.py`：SQLAlchemy Engine、SessionLocal、Base、会话依赖。
    - `models.py`：ORM 模型（users）。
    - `schemas.py`：Pydantic v2 模型（请求/响应）。
  - `api/`
    - `deps.py`：通用依赖（当前用户获取）。
    - `routers/auth.py`：注册、登录、`/me` 示例。
- `alembic/`
  - `env.py`：迁移环境配置，读取应用 Settings。
  - `versions/0001_create_users.py`：示例迁移，创建 users 表。
- `alembic.ini`：Alembic 配置。
- `requirements.txt`：依赖列表。

## 环境准备
1) Python 3.11  
2) 安装依赖：
```bash
pip install -r requirements.txt
```
3) 创建并配置 `.env`：
```
DATABASE_URL=mysql+pymysql://user:pass@127.0.0.1:3306/yourdb
JWT_SECRET_KEY=your-32-char-secret
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
```
## 启动配置环境
```bash
venv\Scripts\activate
```

## 数据库迁移（推荐）
初始化后直接升级到最新迁移：
```bash
alembic upgrade head
```
如需新迁移：
```bash
alembic revision --autogenerate -m "msg"
alembic upgrade head
```

## 本地快速运行
开发环境可直接让应用在启动时 `create_all` 创建表：
```bash
uvicorn app.main:app --reload
```
生产/正式环境建议使用 Alembic 迁移，而非运行时建表。

## 主要接口
- `POST /api/auth/register`：注册；字段 `username`/`email`/`password`，冲突返回 409。
- `POST /api/auth/login`：使用 `identifier`（用户名或邮箱）+ `password`；成功返回 `access_token`（默认 30 分钟）和 `refresh_token`（默认 7 天）。
- `GET /api/me`：受保护接口，需 `Authorization: Bearer <access_token>`，返回当前用户基础信息。

## 其他说明
- JWT 算法：HS256，密钥来自 `JWT_SECRET_KEY`。
- 密码加密：bcrypt，轮次由 `BCRYPT_ROUNDS` 控制。
- 会话管理：`get_db` 依赖负责提交/回滚与关闭连接。

