# DAIL Tech Maintenance Guide

Read this file before working in this repository. Keep changes scoped; source code,
migrations, and active configuration take precedence over this document.

## Project

- `frontend/`: Vue 3, Vite, Pinia, Vue Router.
- `backend/`: FastAPI, SQLAlchemy 2, Pydantic 2, Alembic, MySQL.
- External services: Tencent SMS and Tencent COS. Never commit `.env`, tokens, or
  cloud credentials.
- Roles: `0` user, `1` intern, `2` staff, `3` manager, `4` super admin. Backend
  authorization is the security boundary.

## Work Rules

1. Start with `git status --short --branch`; preserve existing changes.
2. Read only the target module, its direct callers, schemas, models, and tests.
3. Use a `codex/` branch for non-trivial changes. Do not reset, force-push, commit,
   or push unless the user authorizes that action.
4. Keep Chinese files UTF-8 and preserve the existing encoding of modified files.
5. Use `apply_patch` for source edits. Do not make unrelated formatting changes.
6. For API or database changes, update router, schema, frontend consumer, model,
   migration, and tests together.

## Key Paths

### Frontend

- App boot: `frontend/src/main.js`, `frontend/src/App.vue`
- Routes: `frontend/src/router/index.js`
- Auth state: `frontend/src/stores/user.js`
- Shared HTTP and refresh flow: `frontend/src/services/apiClient.js`
- News, image, resume services: `frontend/src/services/newsService.js`,
  `imageService.js`, `resumeService.js`, `profileService.js`
- Homepage: `frontend/src/views/Home.vue` and `frontend/src/components/page_components/`

The homepage uses native scrolling. Do not reintroduce wheel/touch/key
`preventDefault`, forced `scrollTo`, or timer-driven page-position gates in
Technology/Nemo/Wibebare scenes. Preserve mobile and reduced-motion fallbacks.

### Backend

- App and CORS/startup: `backend/app/main.py`
- Settings: `backend/app/core/config.py`
- Authentication dependencies: `backend/app/api/deps.py`
- Models and API schemas: `backend/app/db/models.py`, `backend/app/db/schemas.py`
- Routers: `backend/app/api/routers/`
- Storage cleanup: `backend/app/core/storage_cleanup.py` and
  `backend/app/cleanup_storage.py`
- Migrations: `backend/alembic/versions/`

## Security Contracts

- Production CORS must use explicitly configured origins. Never combine `*` with
  credentialed requests.
- Role 3 manages only roles 0-2. Role 4 can manage roles 0-4, but the final active
  role-4 account cannot be disabled, deleted, or downgraded.
- News-image mutation APIs require role 3+. Public image responses expose only
  images linked to published news and never COS keys, original filenames, or uploader IDs.
- Private resume directory data is limited to member-card fields; never expose email,
  phone, or full resume content.
- Refresh-token rotation must remain atomic. Frontend requests share one refresh
  promise, refresh only on 401, and treat 403 as authorization failure.
- Verification codes use `secrets` plus HMAC hashes. Do not log codes or raw phone
  numbers.
- Create news and attach requested images in one database transaction. Preserve
  requested image order with `display_order`.
- Record COS deletion work in `storage_cleanup_jobs`; process it with a separate
  session and retain failed jobs for retry. A COS 404 is a successful cleanup.

## Environment and Startup

- Copy `backend/.env.example` to ignored `backend/.env`; use a local random JWT key.
  Keep SMS/COS credentials blank unless the feature is intentionally enabled.
- `backend/docker-compose.yml` runs MySQL 8.4 and the backend. Container database
  host is `mysql`; host-run backend uses `127.0.0.1`.
- Run Alembic explicitly for production: `alembic upgrade head`. With
  `AUTO_MIGRATE=true`, migration failure must stop startup.

## Required Verification

Run the checks relevant to the change, then report any unavailable environment:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q

cd ..\frontend
npm run test
npm run build

cd ..
git diff --check
```

For schema changes, also upgrade an empty MySQL database and an existing database
at the previous migration revision. For UI changes, check desktop `1440x900` and
mobile `390x844`, including console errors and horizontal overflow.

## Completion

State the files changed, checks run and their result, and remaining risks. Update
this guide only when project structure, safety contracts, startup behavior, or the
required validation process changes.
