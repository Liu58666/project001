# 当前功能清单（后端）

> 本文档是对当前 FastAPI 后端已实现功能的“模块/接口概览”。更细的参数与响应结构请以 FastAPI OpenAPI 为准（服务启动后访问 `/docs` 或 `/openapi.json`）。

## 通用约定

- **鉴权**：除标注“公开接口（无需登录）”外，其余接口需要 Header：`Authorization: Bearer <access_token>`
- **角色**：`users.role`，常用：`role>=3` 管理员，`role=4` 超级管理员

## 认证与用户资料（Auth / Me）

功能：
- 手机验证码注册/登录
- Access/Refresh Token 刷新
- 获取/更新当前用户资料
- 上传/更新当前用户头像（写入 `users.photo`）

接口（`app/api/routers/auth.py`）：
- **POST** `/api/auth/send-code`：发送短信验证码
- **POST** `/api/auth/register`：注册
- **POST** `/api/auth/login`：登录，返回 token pair
- **POST** `/api/auth/refresh`：刷新 token（refresh token rotation）
- **GET** `/api/me`：获取当前用户信息（需登录）
- **GET** `/api/me/profile`：获取当前用户 profile（需登录）
- **PATCH** `/api/me/profile`：更新当前用户 profile（需登录）
- **POST** `/api/me/photo`：上传/更新当前用户头像（需登录）

## 用户（Users）

功能：
- 获取所有用户头像列表（用于前端做 id→头像 映射）

接口（`app/api/routers/users.py`）：
- **GET** `/api/users/avatars`：获取所有用户头像（**公开接口，无需登录**），返回 `[{id, photo}]`

## 站内消息（Messages）

功能：
- 用户查询自己的站内消息
- 标记已读、删除消息

接口（`app/api/routers/messages.py`）：
- **GET** `/api/messages/me`：我的消息列表（需登录）
- **POST** `/api/messages/{message_id}/read`：标记已读（需登录，仅本人）
- **DELETE** `/api/messages/{message_id}`：删除消息（需登录，仅本人）

## 站内消息（管理员）（Admin Messages）

功能：
- 超级管理员群发系统消息（支持按 roles / user_ids 并集筛选）
- 撤回群发批次

接口（`app/api/routers/admin_messages.py`）：
- **POST** `/api/admin/messages/broadcast`：群发（仅 `role in {3,4}`）
- **POST** `/api/admin/messages/broadcast/{batch_id}/revoke`：撤回（仅 `role in {3,4}`）

## 用户管理（管理员）（Admin Users）

功能：
- 超级管理员查询用户列表
- 超级管理员更新用户（role/active/密码等）

接口（`app/api/routers/admin_users.py`）：
- **GET** `/api/admin/users`：用户列表（仅 `role in {3,4}`）
- **PATCH** `/api/admin/users/{user_id}`：更新用户（仅 `role in {3,4}`）

## 报名表单（Applications）

功能：
- 用户提交报名表单（每用户仅一次）
- 管理员查看/接受/拒绝报名
- 接受报名会给用户发送站内消息

接口（`app/api/routers/applications.py`）：
- **POST** `/api/applications`：提交报名（需登录）
- **GET** `/api/admin/applications`：查看所有报名（仅 `role>=3`）
- **POST** `/api/admin/applications/{application_id}/accept`：接受报名（仅 `role>=3`）
- **POST** `/api/admin/applications/{application_id}/reject`：拒绝报名（仅 `role>=3`）

## 新闻（News）

功能：
- 新闻列表/详情
- 管理员发布/删除新闻
- 新闻内容支持 `[IMAGE:n]` 占位符，图片上传由图片模块完成

接口（`app/api/routers/news.py`）：
- **GET** `/api/news`：新闻列表（公开）
- **GET** `/api/news/{news_id}`：新闻详情（公开）
- **POST** `/api/news`：发布新闻（需登录，`role>=3`）
- **DELETE** `/api/news/{news_id}`：删除新闻（需登录，`role>=3`）

## 新闻图片（Images / News Images）

功能：
- 上传新闻图片到腾讯云 COS，并落库 `news_images`
- 图片列表/详情
- 上传者或管理员可删除/修改说明/关联新闻

接口（`app/api/routers/images.py`）：
- **POST** `/api/images/upload`：上传新闻图片（需登录）
- **GET** `/api/images`：查询图片列表（公开）
- **GET** `/api/images/{image_id}`：图片详情（公开）
- **DELETE** `/api/images/{image_id}`：删除图片（需登录：上传者本人或 `role>=3`）
- **PUT** `/api/images/{image_id}/link-news`：关联到新闻（需登录：上传者本人或 `role>=3`）
- **PATCH** `/api/images/{image_id}/caption`：更新图片说明（需登录：上传者本人或 `role>=3`）

## 简历（Resumes）

功能：
- 用户创建/更新自己的简历
- 简历目录：返回基础信息；若简历公开则返回完整简历内容
- 查看自己的简历/更新
- 查看他人公开简历
- 简历图片使用 `user_images`，支持 `bio` 中 `[IMAGE:n]` 占位符映射上传顺序

接口（`app/api/routers/resumes.py`）：
- **POST** `/api/resumes`：创建或覆盖更新我的简历（需登录）
- **GET** `/api/resumes`：简历目录（公开）
- **GET** `/api/resumes/me`：我的简历（需登录）
- **PATCH** `/api/resumes/me`：更新我的简历（需登录）
- **GET** `/api/resumes/{user_id}`：查看他人公开简历（公开，仅 `is_public=true`）

## PDF 简历（Resume PDFs）

功能：
- 用户上传/覆盖自己的 PDF 简历（每用户仅保留最新一份），上传至腾讯云 COS 并落库 `user_resume_pdfs`
- 管理员（`role>=3`）查询所有用户上传的 PDF 简历

接口：
- 用户侧（`app/api/routers/resumes.py`）：
  - **POST** `/api/resumes/me/pdf`：上传/覆盖我的 PDF 简历（需登录，仅 `.pdf`，最大 20MB）
  - **GET** `/api/resumes/me/pdf`：获取我的 PDF 简历信息（需登录）
- 管理员侧（`app/api/routers/admin_resume_pdfs.py`）：
  - **GET** `/api/admin/resume-pdfs`：查询所有用户 PDF 简历列表（需登录，`role>=3`）

## 用户图片（User Images）

功能：
- 用户上传各类图片到腾讯云 COS（avatar/certificate/project/portfolio/bio），并落库 `user_images`
- 查询图片列表：查询他人时要求对方简历公开
- 删除/修改说明/修改展示顺序（仅本人）

接口（`app/api/routers/user_images.py`）：
- **POST** `/api/user-images/upload`：上传用户图片（需登录）
- **GET** `/api/user-images`：图片列表（登录可查自己；查他人需对方简历公开）
- **DELETE** `/api/user-images/{image_id}`：删除图片（需登录，仅本人）
- **PATCH** `/api/user-images/{image_id}/caption`：更新说明（需登录，仅本人）
- **PATCH** `/api/user-images/{image_id}/order`：更新展示顺序（需登录，仅本人）

## 任务系统（Tasks / Submissions / Scoring）

功能：
- 管理员发布任务（发布对象：`roles + user_ids` 并集，发布时生成接收者快照 `task_recipients`）
- 接收者提交任务：支持提交纯文本/建议，并可上传多张图片（腾讯云 COS）
- 管理员查看提交列表并评分（0-100，覆盖更新）

接口（`app/api/routers/tasks.py`）：

管理员端（需登录）：
- **POST** `/api/admin/tasks`：发布任务（仅 `role in {3,4}`）
- **GET** `/api/admin/tasks`：任务列表（仅 `role>=3`）
- **DELETE** `/api/admin/tasks/{task_id}`：删除任务（仅 `role>=3`，一键删除该任务及其提交/图片等关联数据）
- **GET** `/api/admin/tasks/{task_id}/submissions`：该任务所有提交（仅 `role>=3`）
- **POST** `/api/admin/tasks/{task_id}/submissions/{submission_id}/score`：评分（仅 `role>=3`）

用户端（需登录）：
- **GET** `/api/tasks/me`：我被指派的任务列表（仅接收者数据）
- **GET** `/api/tasks/{task_id}`：任务详情（接收者本人或 `role>=3`）
- **PUT** `/api/tasks/{task_id}/submission`：提交/更新提交（仅接收者本人；同任务同用户一份提交，覆盖更新）
- **POST** `/api/tasks/{task_id}/submission/images`：上传提交图片（仅接收者本人；多张）
- **DELETE** `/api/tasks/{task_id}/submission/images/{image_id}`：删除提交图片（本人或 `role>=3`）


