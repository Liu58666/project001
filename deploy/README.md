# DAIL Tech Server Deployment

This directory is the production deployment entrypoint. It starts:

- `frontend`: Nginx serving the Vite build and proxying `/api/` to `backend:8000`
- `backend`: FastAPI application
- `mysql`: MySQL 8.4 with a persistent Docker volume

## Files To Copy

Copy the whole repository to the server. Do not copy local dependency/build/cache folders:

- keep: `frontend/`, `backend/`, `deploy/`, root docs
- skip: `frontend/node_modules/`, `frontend/dist/`, `backend/.venv*/`, `backend/.pytest_cache/`, any real `.env`

## First Deploy

From the server repository root:

```bash
cd deploy
cp .env.example .env
```

Edit `deploy/.env`:

- set `CORS_ALLOWED_ORIGINS` to the real site origin, for example `https://example.com`
- replace `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD`, and `JWT_SECRET_KEY`
- fill Tencent SMS/COS variables only if those features are enabled

Start MySQL, run migrations, then start the app:

```bash
docker compose up -d mysql
docker compose run --rm backend alembic upgrade head
docker compose up -d --build
```

Check status:

```bash
docker compose ps
docker compose logs --tail=100 backend
docker compose logs --tail=100 frontend
```

## Updates

After uploading new code:

```bash
cd deploy
docker compose build backend frontend
docker compose run --rm backend alembic upgrade head
docker compose up -d
```

## Notes

- `deploy/.env` is ignored by Git. Keep it only on the server.
- The backend is not published directly to the public host; Nginx routes browser API calls through `/api/`.
- MySQL data is stored in the named Docker volume `dail-tech_dail_mysql_data`.
- If you put another reverse proxy such as Caddy, Nginx, or a cloud load balancer in front, point it to the frontend container port.
