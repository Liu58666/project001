# project001

DAIL Tech 公司官网与内部管理系统（全栈）。

## 结构

```
project001/
├── backend/    # FastAPI + SQLAlchemy + Alembic + MySQL
└── frontend/   # Vue 3 + Vite + Pinia
```

## 后端 backend/

FastAPI 服务，提供鉴权（JWT access/refresh）、用户与简历、新闻、任务发布与提交评分、
站内消息、实习生申请审核等接口；对象存储与短信走腾讯云 COS / SMS。

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # 填入真实配置，切勿提交 .env
uvicorn app.main:app --reload
```

## 前端 frontend/

Vue 3 单页应用。

```bash
cd frontend
npm install
npm run dev
```

开发环境后端代理地址在 `frontend/.env.development` 的 `VITE_API_PROXY_TARGET` 配置。

## 安全说明

- 所有密钥仅通过环境变量 / `.env` 注入，源码中不含任何硬编码凭据。
- `.env` 已被 `.gitignore` 忽略，请勿提交真实密钥。
