# project001 项目维护指南

本文件是本项目的长期上下文。进入本项目工作的 Agent 必须先读本文件，再根据任务只检查相关文件；不要在每次新对话中默认重新全量扫描整个仓库。

## 文档使用规则

- 本文档基于 Git 提交 `2be6060`（2026-07-05 的初始全栈版本）和当时的全部源码整理。
- 接到普通维护任务时，先用本文档定位模块，再读取目标文件及其直接依赖、调用方和测试；不要无目的地重扫全部代码。
- 如果当前提交已经变化，先看 `git status`、`git log -1` 和相关 `git diff`，仅核对发生变化的模块。
- 源码、数据库迁移和实际环境配置是最终事实；本文档若与代码冲突，以当前代码为准，并在结构或约定发生变化后同步更新本文档。
- 用户要求“记住”“记录一下”“放到提示里”或表达类似意思时，将内容整理后追加到“重要提示记录”。不要记录密码、令牌、云密钥或真实数据库连接串。
- 修改前检查 Git 状态，保留用户已有改动。小范围维护优先使用独立分支；未经用户明确同意，不执行 `git reset --hard`、强推、批量删除或大范围重构。
- 新建中文文件使用 UTF-8；修改已有文件时保持原编码。

## 项目概览

这是 DAIL Tech 公司官网与内部管理系统的单仓库全栈项目：

- `frontend/`：Vue 3 单页应用，使用 Vite、Pinia、Vue Router。
- `backend/`：FastAPI API，使用 SQLAlchemy 2、Pydantic 2、Alembic 和 MySQL。
- 外部服务：腾讯云 SMS 发送验证码，腾讯云 COS 保存新闻图片、用户图片、任务图片和 PDF 简历。
- 鉴权：JWT Access Token + 可轮换的 Refresh Token；前端将登录信息放在 `localStorage` 或 `sessionStorage`。
- 角色：`0=游客/普通注册用户`、`1=实习生`、`2=职员`、`3=管理人员`、`4=最高管理员`。后端权限校验才是安全边界，前端角色判断只控制页面展示和跳转。
- 当前仓库没有自动化测试目录，也没有前端 lint/test 脚本；改动至少要执行 Python 语法/导入检查、前端构建，并手工验证相关业务流程。

## 顶层结构

```text
project001/
├─ AGENTS.md                 # 本维护指南和长期项目提示
├─ README.md                 # 项目简要启动说明
├─ .gitignore                # 忽略密钥、虚拟环境、依赖和构建产物
├─ frontend/                 # Vue 前端
└─ backend/                  # FastAPI 后端
```

## 前端结构

### 启动与全局框架

- `frontend/src/main.js`：创建 Vue 应用，注册 Pinia 和 Router，挂载全局 `$t()` 翻译函数并加载基础样式。
- `frontend/src/App.vue`：应用外壳；初始化用户状态，展示全局 Loader、错误/警告/成功通知和导航栏。通过 `provide` 暴露加载动画状态；移动设备可以正常进入应用。
- `frontend/src/router/index.js`：全部前端路由。当前没有全局 `beforeEach` 权限守卫，受限页面各自在组件内部检查登录和 JWT 中的角色。
- `frontend/src/assets/styles/base.css`：全局重置、字体和页面基础样式。
- `frontend/src/assets/images/`、`frontend/public/`：官网图片、视频、Logo 和 favicon；修改引用前检查静态资源路径和构建结果。

### 页面路由与职责

公开官网页面：

- `/` → `Home.vue`：首页容器，按顺序组合 `page_components/Main.vue`、`DailOverview.vue`、`Second.vue`、`NemoOneShowcase.vue`、`CompanyOrbitTransition.vue`、`Third.vue`、`End.vue`；其中 `DailOverview.vue` 使用纯白背景、黑色错落文字和进入视口后的遮罩揭字动画介绍 DAIL，随后由 `Second.vue` 的中央黑色区域扩张完成白转黑；Nemo One 区块使用单张主产品图、边缘渐隐、轻微漂浮和高光扫过形成动态展示，后续公司过渡区再承接到白色 CTA。
- `/about` → `About.vue`：关于页，组合 `About_one.vue` 到 `About_four.vue`。
- `/technology` → `Technology.vue`：AI 原生技术体系页面；同一全屏深色纯文字关系图也由首页 `Second.vue` 直接复用，展示数据治理、模型工程、智能体开发和平台构建。
- `/technology/:topicId` → `TechnologyTopic.vue`：四项技术能力的独立纯白详情页，使用大标题与简短介绍，并复用全局顶部导航和 `End.vue` 页尾；进入页面时序号、逐字/逐词标题、说明和按钮按顺序从下方浮现，直接打开页面时等待全局 Loader 完成后播放；`Listen to more hard questions` 按钮进入已有 `/coming-soon` 开发中页面。
- `/team` → `Team.vue`：从公开简历目录加载团队成员，按角色分组并进入个人公开简历。
- `/career` → `Career.vue`：招聘入口，根据登录状态和角色决定进入实习申请等页面。
- `/career/intern-apply` → `InternApply.vue`：实习申请表及 PDF 简历上传；直接调用申请 API。
- `/career/join` → `JoinUs.vue`：加入我们/联系信息。
- `/news` → `News.vue`：新闻列表。
- `/news/:slug` → `NewsDetail.vue`：按 slug 获取和展示新闻详情。
- `/coming-soon` → `ComingSoon.vue`：未开放功能占位页。

认证和个人中心：

- `/login` → `Login.vue`：登录，直接调用 `/api/auth/login`，成功后写入用户 Store。
- `/register` → `Register.vue`：发送短信验证码并注册，直接调用 `/api/auth/send-code`、`/api/auth/register`。
- `/user` → `User.vue`：个人中心主页面，包含资料、头像、消息、管理入口；文件很大且存在多处直接 `fetch`，修改个人资料或消息时必须同时检查此页和服务层。
- `/user/resume` → `ResumeSettings.vue`：编辑结构化简历和富文本/图片块。
- `/user/resume-pdf` → `ResumePdf.vue`：上传和查看当前用户最新 PDF 简历。
- `/user/resume/:userId` → `ResumeView.vue`：查看公开简历。
- `/user/my-tasks` → `MyTasks.vue`：当前用户收到的任务。
- `/user/task/:taskId` → `TaskDetail.vue`：任务详情、文字提交、建议、图片上传与删除。

管理页面（通常要求 `role>=3`，最终以对应后端接口为准）：

- `/news/preview` → `preview_news.vue`：新闻编辑、图片块上传、预览和发布。
- `/news/delete` → `delete_news.vue`：新闻选择和删除。
- `/user/list` → `UserList.vue`：用户查询和编辑；前端区分管理人员与最高管理员，但后端当前允许角色 3、4 调用用户管理接口。
- `/user/interns` → `InternManage.vue`：申请列表、PDF 预览、接受或拒绝申请。
- `/user/broadcast` → `BroadcastMessage.vue`：按角色和指定用户的并集群发/撤回站内消息。
- `/user/task-publish` → `TaskPublish.vue`：按角色和指定用户发布任务。
- `/user/tasks` → `TaskList.vue`：管理员任务列表。
- `/user/tasks/:taskId/submissions` → `TaskSubmissions.vue`：查看提交、评分和删除任务。

### 前端公共组件

- `NavBar.vue`：Logo、导航、登录入口、用户头像和中英文切换。
- `LoaderOverlay.vue`：全局加载过场。
- `ErrorAlert.vue`、`WarningAlert.vue`、`SuccessAlert.vue`：读取对应 Pinia Store 的全局提示。
- `WarningModal.vue`、`AcceptModal.vue`：通用确认/接受弹窗。
- `newscard.vue`：新闻卡片和最新新闻加载。
- `NewsPublishForm.vue`、`NewsDeleteForm.vue`：新闻表单组件；主要新闻编辑逻辑仍在页面中。

### 状态、服务与工具

- `stores/user.js`：登录态、用户资料、存储策略、Token 到期判断、定时刷新和登出清理。`remember_me=true` 使用 `localStorage`，否则使用 `sessionStorage`。
- `stores/i18n.js`：本地中英文字典；语言保存在 `localStorage.locale`，`t()` 按路径取值并回退英文。它是纯前端实现，不调用翻译接口。
- `stores/error.js`、`warning.js`、`success.js`：全局提示消息与自动关闭状态。
- `services/apiClient.js`：推荐的统一请求入口；自动加 Bearer Token，支持 JSON/FormData，遇到 401/403 时刷新一次并重试。
- `services/adminService.js`：用户管理、接受申请、群发和撤回消息。
- `services/taskService.js`：任务发布、列表、提交、图片、评分和删除。
- `services/resumeService.js`：结构化简历、公开简历、PDF 上传和管理员 PDF 列表。
- `services/profileService.js`：当前用户资料与头像。
- `services/userImageService.js`：用户图片上传、列表、说明、排序和删除。
- `services/newsService.js`：新闻列表/详情/发布/删除；内部另有一套 Token 刷新请求逻辑。
- `services/imageService.js`：新闻图片上传、列表、删除和关联新闻；主要使用直接 `fetch`。
- `services/messageService.js`：我的消息、标记已读和删除。
- `services/userService.js`：公开用户头像列表和 `userId -> avatar` 映射。
- `utils/roles.js`：0 到 4 的角色常量和中英文名称。
- `utils/imagePreloader.js`：页面图片预加载。

维护认证或网络错误处理时，不要只改 `apiClient.js`：`Login.vue`、`Register.vue`、`InternApply.vue`、`InternManage.vue`、`BroadcastMessage.vue`、`User.vue`、`newsService.js` 和 `imageService.js` 仍有直接请求或独立封装。

## 后端结构

### 应用入口与基础设施

- `backend/app/main.py`：创建 FastAPI、开放 CORS、注册全部 Router。启动时尝试 `alembic upgrade head`，失败会记录异常但继续执行 `Base.metadata.create_all()`；后者只能补表，不能可靠修改已有表结构。
- `backend/app/core/config.py`：Pydantic Settings，从 `.env` 读取数据库、JWT、bcrypt、短信、验证码和 COS 配置。
- `backend/app/db/database.py`：SQLAlchemy Engine、`SessionLocal`、Base 和请求级 `get_db()`；成功提交，异常回滚，最后关闭。
- `backend/app/api/deps.py`：Bearer Token 鉴权。`get_current_user` 验证 access token 并从数据库重新读取启用用户；`get_current_user_optional` 用于可匿名接口。
- `backend/app/core/security.py`：密码哈希/校验、Token 哈希、JWT 创建和解码。
- `backend/app/core/verification_code.py`：验证码生成、发送间隔、过期和一次性使用逻辑。
- `backend/app/core/sms_service.py`：腾讯云短信发送。
- `backend/app/core/cos_service.py`：COS 上传、删除、URL 和图片处理的集中封装。
- `backend/app/db/schemas.py`：全部 API 请求/响应 Pydantic Schema；改接口字段时要同步前端消费方。

### API Router

- `auth.py`：`/api/auth/send-code|register|login|refresh` 与 `/api/me|me/profile|me/photo`。登录 Token 带 `role` 和 `roles` claims；Refresh Token 原文不落库，只保存哈希并执行轮换。
- `users.py`：公开的 `/api/users/avatars`。
- `admin_users.py`：`/api/admin/users` 查询与修改，角色 3/4；修改用户角色时同步 `user_resumes.role`。
- `applications.py`：用户提交申请；管理员查询、接受、拒绝。接受会把用户设为角色 1、同步简历角色并发送消息；拒绝会清空表单隐私数据但保留记录，阻止重复申请。
- `messages.py`：当前用户消息列表、已读、删除，仅可操作自己的消息。
- `admin_messages.py`：按 `roles + user_ids` 并集生成接收者，逐用户写消息；批次 ID 用于撤回。
- `news.py`：公开新闻列表/详情，角色 3+ 发布和删除；新闻正文是段落 JSON，可含 `[IMAGE:n]`。
- `images.py`：新闻图片上传至 COS、公开查询、关联新闻、改说明和删除；修改/删除要求上传者本人或角色 3+。
- `resumes.py`：结构化简历创建/更新、公开目录、自己的简历、他人公开简历和个人 PDF 上传/查询。
- `admin_resume_pdfs.py`：角色 3+ 查询所有用户 PDF 简历。
- `user_images.py`：用户头像/证书/项目/作品集/bio 图片；自己的图片可维护，查询他人图片要求对方简历公开。
- `tasks.py`：管理员任务发布/列表/删除/查看提交/评分，以及接收者任务详情、提交和图片维护。

服务启动后以 `/docs` 或 `/openapi.json` 为接口参数和响应的快速核对入口。

## 数据库模型与迁移

`backend/app/db/models.py` 中的 13 个模型：

- `User` → `users`：账号、手机号、密码哈希、启用状态、角色和个人资料。
- `VerificationCode` → `verification_codes`：短信验证码、过期时间和使用状态。
- `RefreshToken` → `refresh_tokens`：Refresh Token 哈希、有效期、撤销和轮换链。
- `UserApplicationForm` → `user_application_forms`：每用户一份申请及审核状态。
- `UserMessage` → `user_messages`：个人消息、群发批次、已读和撤回状态。
- `News` → `news`：slug、分类、日期、标题和段落 JSON。
- `NewsImage` → `news_images`：新闻图片 COS 元数据和关联新闻。
- `UserResume` → `user_resumes`：每用户一份结构化简历、公开状态和 bio JSON。
- `UserResumePDF` → `user_resume_pdfs`：每用户最新一份 PDF 的 COS 元数据。
- `UserImage` → `user_images`：用户各类图片、说明和展示顺序。
- `Task` → `tasks`：任务正文、创建人和发布时间。
- `TaskRecipient` → `task_recipients`：任务发布时的接收者快照。
- `TaskSubmission` → `task_submissions`，`TaskSubmissionImage` → `task_submission_images`：每个用户每个任务一份提交、评分及多张图片。

`backend/alembic/versions/0001` 到 `0015` 是连续迁移历史，依次覆盖用户、验证码、资料字段、新闻、Refresh Token、新闻图片、简历、用户图片、简历扩展、申请/消息、任务系统和 PDF 简历。修改表结构必须新增 Alembic 迁移并验证升级路径，不要只改 `models.py` 或依赖 `create_all()`。

## 关键业务链路

### 注册与登录

1. `Register.vue` 请求发送验证码。
2. 后端创建验证码记录并通过腾讯云 SMS 发送。
3. 注册时后端校验验证码，创建角色 0 用户并哈希密码。
4. `Login.vue` 登录后获得 Access/Refresh Token，再取用户资料写入 `stores/user.js`。
5. 普通 API 使用 Bearer Access Token；过期后前端刷新，后端轮换 Refresh Token。

### 实习申请

1. 角色 0 的登录用户在 `InternApply.vue` 上传 PDF、提交申请。
2. `applications.py` 保证每个用户只能有一条申请记录。
3. 管理人员在 `InternManage.vue` 审核。
4. 接受：用户角色变为 1并收到站内消息；拒绝：申请内容清空但保留拒绝记录。

### 新闻发布

1. `preview_news.vue` 编辑正文和图片块，图片先上传 COS/`news_images`。
2. 正文保存为字符串数组，图片位置用 `[IMAGE:n]` 占位。
3. 发布新闻后再将已上传图片关联到新闻 ID。
4. `News.vue` 和 `NewsDetail.vue` 公开读取并渲染。

### 简历与团队

1. `ResumeSettings.vue` 保存结构化简历，bio 使用段落数组和图片占位符。
2. 用户图片单独存 `user_images`；PDF 单独存 `user_resume_pdfs`。
3. `Team.vue` 读取公开简历目录，过滤角色大于 0 的成员并按角色排序。
4. `ResumeView.vue` 只展示公开简历；隐私判断必须以后端为准。

### 任务分发与评分

1. `TaskPublish.vue` 提交 `title`、`content`、`roles`、`user_ids`。
2. `tasks.py` 查询匹配角色的启用用户，与指定用户取并集并去重。
3. 发布时为每个接收者写一条 `task_recipients`；以后任务可见性以该快照为准，不随用户角色变化而追溯改变。
4. 接收者在 `TaskDetail.vue` 覆盖更新自己的唯一提交，可附多张 COS 图片。
5. 管理人员在 `TaskSubmissions.vue` 查看并给 0–100 分；删除任务会级联清理接收者、提交和图片数据库记录，代码还负责删除对应 COS 对象。

## 运行与部署

前端：

```powershell
cd frontend
npm ci
npm run dev
```

- Node 要求 `^20.19.0` 或 `>=22.12.0`。
- Vite 将 `/api` 代理到 `VITE_API_PROXY_TARGET`，默认 `http://127.0.0.1:8000`。
- `npm run build` 生成生产文件；生产 Docker 使用 Node 22 构建，再由 Nginx 提供 SPA 和静态缓存。
- `frontend/nginx.conf` 将 `/api/` 代理到 Docker 网络中的 `backend:8000`，并用 `try_files ... /index.html` 支持前端 History 路由。

后端：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python -m uvicorn app.main:app --reload
```

- 目标 Python 版本为 3.11。
- `.env` 至少需要有效 `DATABASE_URL` 和长度不少于 32 的 `JWT_SECRET_KEY`；短信/COS 功能还需要对应腾讯云配置。
- 不提交 `.env`。`.env.example` 只能保存占位符。
- `backend/docker-compose.yml` 当前只定义 backend 服务，没有定义 MySQL；数据库必须由外部/本机另行提供，且容器中的 `127.0.0.1` 指向容器自身。

## 修改与验证清单

1. 开始前执行 `git status --short --branch`，确认分支和已有改动。
2. 先从本文件找到目标模块，再阅读：入口/页面 → Service/Router → Schema → Model/迁移 → 调用方。
3. API 字段变化要同时检查 `schemas.py`、对应 Router、前端 Service 和页面。
4. 权限变化要同时检查后端强制校验、JWT claims 和前端可见性逻辑，但不能依赖前端完成授权。
5. 数据表变化必须新增 Alembic 迁移，检查外键级联和 COS 文件清理。
6. 图片/PDF 改动要验证文件类型、大小限制、数据库记录和 COS 对象的一致性。
7. 前端至少执行 `npm run build`；后端至少做编译/导入检查，并在有可用 `.env`、MySQL 时启动服务检查 `/docs`。
8. 手工验证本次涉及的完整用户链路和不同角色，特别是未登录、角色不足、Token 过期、空数据和上传失败。
9. 完成后检查 `git diff --check` 和 `git status`，向用户说明修改文件、验证结果和剩余风险。

## 已知维护注意事项

- 前端权限检查分散在页面里，Router 没有统一守卫；新增受限页面时必须补前端入口控制，但真正权限仍在后端。
- 前端网络层尚未完全统一，多处直接 `fetch`；全局修改 Token、错误解析或 API 前缀时要搜索所有 `/api/` 调用。
- `main.py` 的迁移失败不会阻止服务启动，可能出现“服务在线但数据库结构旧”的状态；维护环境应单独确认 Alembic 已到 `head`。
- 后端 CORS 当前为 `allow_origins=["*"]` 且允许 credentials；上线前应按真实域名收紧并验证浏览器行为。
- 部分注释仍把 role 3 写成最高管理员，但实际代码和前端角色表支持 role 4；判断权限以具体后端条件为准。
- 大型 Vue 页面（尤其 `User.vue`、`preview_news.vue`、`InternApply.vue`、`TaskSubmissions.vue`）同时包含模板、业务逻辑和大量样式，小改动要限定范围，避免无关格式化。

## 重要提示记录

- 2026-07-13：后续对话先阅读本文件，默认做任务相关的定向核对，不再无目的地全量扫描全部源码。结构、关键业务链路或运行方式变化后同步更新本文件。
- 2026-07-13：已解除 `App.vue` 的移动设备访问限制，并为公共导航和基础样式加入 `900px` 手机断点；除首页外，各页面内部的固定宽度和多栏布局仍需分批适配。
- 2026-07-13：首页 `Main.vue`、`Second.vue`、`Third.vue`、`End.vue` 已完成 `900px` 响应式适配；手机端使用单列内容、完整能力卡片、纵向 CTA 和双列页脚，桌面端保留原有多栏布局。
- 2026-07-13：关于页面 `About.vue` 及 `About_one.vue` 到 `About_four.vue` 已完成 `900px` 响应式适配；手机和平板改为四区块自然纵向滚动，桌面继续使用原有全屏翻页和页面指示器。
- 2026-07-13：前端其余公开、认证、招聘、个人中心、简历、新闻管理、实习审核、站内消息和任务系统页面均已补齐移动端响应式布局；统一以 `900px` 为主断点，窄屏表单、卡片、弹窗和固定操作栏改为单列或可滚动布局，桌面端原布局保持不变。
- 2026-07-13：首页原 `Second.vue` AI 原生能力卡片区已直接替换为 `Technology.vue` 的深色纯文字关系图，首页与 `/technology` 复用同一实现，不再要求先点击入口；首页桌面端在该区块顶部进入视口约 `58%` 高度时，全屏深色层就通过中央横向圆角矩形遮罩提前缓慢打开，只有已经进入整屏停驻位置且扩散尚未完成时才屏蔽继续向下滚动；完成后停留在约 `155svh` 的全屏 sticky 浏览段，继续向下移动约 `30%` 屏高后，才用约 `760ms` 的固定时长自动淡出四个能力标题、连接线和中央说明，退场过程不绑定滚动进度且结束后才释放后续下滑，只保留中央大标题；反向回到该屏时这些内容按固定时长重新浮现；中央“探索我们的技术”按钮已从首页和独立技术页移除；深色扩散层本身向下浏览不会收回，只有页面返回顶部才平滑收回到首次打开时的中央黑色圆角框并允许下次重新播放；`900px` 以下与减少动画模式不启用停驻锁定，独立 `/technology` 页面保持原单屏布局；四个能力标题统一为白色，已移除中央眉题、装饰方框和标题下边框，关系图外层使用纯白背景；点击能力节点进入 `/technology/:topicId` 独立详情页，详情页使用纯白大标题布局并保留顶部导航与 `End.vue` 页尾。
- 2026-07-14：首页在 `Second.vue` 与 `Third.vue` 之间新增 `NemoOneShowcase.vue` 产品介绍区；Technology 关系图保留从中央黑色圆角矩形向全屏扩散的入场效果，外层使用白色承接面保证动画可见，展开后的关系图与 Nemo One 均为纯黑并无缝衔接；Nemo One 取消多图转圈、进度条、sticky 和超长滚动空间，只保留单张主产品图，通过边缘渐隐、轻微漂浮、蓝色环境光和周期高光形成动态效果，并保留中英文文案、`900px` 移动端布局、减少动画降级及区块内深色导航外观。
- 2026-07-14：首页在 `NemoOneShowcase.vue` 与 `Third.vue` 之间新增 `CompanyOrbitTransition.vue`；桌面端保持 Git 提交 `dcd17d4` 中约 132vh 的原始设计参数，固定大小的中央 Logo 上方展示中英文总结标题，并由完整的白色核心、冷青过渡和两层柔化雾光从背景下方扩散覆盖；桌面端虚化目标进度继续由该区块的正反向滚动位置决定，不使用定时播放或滚动锁定，但渲染进度增加约 105ms 的轻量惯性跟随，各阶段使用起止导数为零的五次平滑曲线，减少滚轮分段造成的跳动且保持相同阶段阈值与最终画面。圆弧照片及其代码仍完整保留，但当前通过 `showPhotos=false` 关闭显示。首页向 `Third.vue` 传入 `home-handoff`，只在首页把 CTA 视频色带上提并缩短色带顶部的纯白渐隐，使下方彩色图像更早进入视口，从 `Third.vue` 图像层缩短纯白空档，同时保留 CTA 原有文字位置、区块高度和新闻详情页的默认布局；`900px` 以下改用独立的紧凑静态渐变场景，不运行 sticky 和滚动擦除，标题与 Logo 固定在深色区域，下半段从冷青自然过渡到纯白后直接衔接 CTA。
- 2026-07-15：首页在彩色首屏 `Main.vue` 与黑色技术关系图 `Second.vue` 之间新增 `DailOverview.vue`；该区块始终保持纯白背景和官网现有系统无衬线字体，以左上主标题、右上说明、左下“构建/治理/落地”与右下理念句形成错落排版，只保留主要文案，不显示小字号标签、编号或英文注释，也不使用图片、数据卡片、下划线、分隔线、扫线动画或白转黑背景；从首页向下进入区块时播放遮罩揭字、轮廓残影和错峰滑入动画，播放后无论继续向下还是从下往上返回都保持文字可见，只有回到首页顶部 `scrollY<=8` 时才在屏幕外立即复位，下一次向下进入时完整重播；真正的白转黑仍由下一页 `Second.vue` 的中央黑色区域放大完成，并提供 `900px` 移动布局与减少动画降级。
- 2026-07-15：首页完成一轮真实手机视口复核：`390x844` 与 `320x568` 下无页面级横向溢出，移动导航、首页各区块、CTA 与页脚均保持可用；首屏新闻胶囊在窄屏固定单行并省略过长标题，双按钮维持紧凑横排；`DailOverview.vue` 手机端不再照搬桌面错落四区，而改为标题、介绍、三项能力词和总结句的紧凑编辑式阅读流；`900px` 以下的 Technology 使用中央大标题连接 2x2 四个轻量能力节点，首页嵌入模式高度只包住实际内容，独立 `/technology` 仍保持满屏；`CompanyOrbitTransition.vue` 手机端使用约 `78svh` 的纯垂直静态渐变，从纯黑依次经过石墨灰、雾灰过渡到珍珠白，不使用径向光晕、中心亮斑或动画，并用 1px 黑色端重叠消除与 Nemo One 之间的半像素白线；CTA 保持纵向双按钮，页脚订阅标题在窄屏使用自适应字号；桌面 SVG、四角节点、sticky 光晕动画和布局全部保持不变。
- 2026-07-16：首页原 `Second.vue` 与 `NemoOneShowcase.vue` 已由 `TechnologyNemoTransition.vue` 统一替代；桌面端使用约 `185svh` 的单一纯黑 sticky 场景，中央黑框扩张完成后，下一次向下输入会触发约 `980ms` 的固定时长交接：技术文案上滑模糊淡出，Nemo 文案与 `nemo-cooling.png` 产品图同步上滑淡入，完成前屏蔽继续下滑，完成后再按滚动进度保留产品视差展示。导航栏保持透明，并在实际深色背景进入导航高度时切换前景色；`900px` 以下与减少动画模式降级为技术介绍和 Nemo 产品上下两段自然滚动。
