# Requirements Document

## Introduction

管理端任务发布功能，允许管理员（role 3/4）创建并发布任务给指定角色或用户。任务发布后，接收者会被快照到 task_recipients 表，后续角色变化不影响该任务的接收者列表。

## Glossary

- **Task_Publisher**: 管理员用户（role in {3, 4}），具有发布任务的权限
- **Task**: 包含标题、内容的任务实体，由管理员创建并发布给指定接收者
- **Task_Recipient**: 任务接收者，通过角色或用户ID指定，发布时快照存储
- **Admin_Service**: 管理端服务层，处理任务相关的 API 请求
- **Task_Publish_Page**: 任务发布页面组件，提供任务创建和发布的用户界面

## Requirements

### Requirement 1: 任务发布表单

**User Story:** As a Task_Publisher, I want to create a task with title and content, so that I can assign work to team members.

#### Acceptance Criteria

1. THE Task_Publish_Page SHALL display a form with title input field (1-200 characters)
2. THE Task_Publish_Page SHALL display a content textarea field (1-5000 characters)
3. WHEN the title exceeds 200 characters, THE Task_Publish_Page SHALL prevent further input
4. WHEN the content exceeds 5000 characters, THE Task_Publish_Page SHALL prevent further input
5. THE Task_Publish_Page SHALL display character count indicators for both fields

### Requirement 2: 接收者选择 - 按角色

**User Story:** As a Task_Publisher, I want to select recipients by role, so that I can quickly assign tasks to groups of users.

#### Acceptance Criteria

1. THE Task_Publish_Page SHALL display role selection chips for all available roles (0-4)
2. WHEN a role chip is clicked, THE Task_Publish_Page SHALL toggle the role's selection state
3. THE Task_Publish_Page SHALL visually distinguish selected roles from unselected roles
4. THE Task_Publish_Page SHALL allow multiple roles to be selected simultaneously

### Requirement 3: 接收者选择 - 按用户

**User Story:** As a Task_Publisher, I want to select specific users as recipients, so that I can assign tasks to individuals.

#### Acceptance Criteria

1. THE Task_Publish_Page SHALL provide a user selection modal accessible via a card button
2. WHEN the user selection modal opens, THE Task_Publish_Page SHALL load and display the user list
3. THE Task_Publish_Page SHALL support searching users by name, phone, or email
4. WHEN a user is selected, THE Task_Publish_Page SHALL display the user as a tag below the selection area
5. THE Task_Publish_Page SHALL allow removing selected users by clicking the tag's remove button
6. THE Task_Publish_Page SHALL display the count of selected users

### Requirement 4: 任务发布提交

**User Story:** As a Task_Publisher, I want to submit the task, so that recipients can view and complete it.

#### Acceptance Criteria

1. WHEN the content field is empty, THE Task_Publish_Page SHALL prevent submission and show an error
2. WHEN no roles and no users are selected, THE Task_Publish_Page SHALL prevent submission and show an error
3. WHEN the form is valid, THE Task_Publish_Page SHALL send a POST request to /api/admin/tasks
4. WHILE the request is in progress, THE Task_Publish_Page SHALL disable the submit button and show loading state
5. WHEN the request succeeds, THE Task_Publish_Page SHALL show a success message with recipient count
6. WHEN the request succeeds, THE Task_Publish_Page SHALL reset the form to initial state
7. IF the request fails with 400, THEN THE Task_Publish_Page SHALL display the error message from response
8. IF the request fails with 403, THEN THE Task_Publish_Page SHALL display a permission denied message

### Requirement 5: 权限控制

**User Story:** As a system, I want to restrict task publishing to authorized users, so that only administrators can create tasks.

#### Acceptance Criteria

1. WHEN a non-admin user (role < 3) accesses the page, THE Task_Publish_Page SHALL redirect to user page
2. THE Task_Publish_Page SHALL verify user role on page mount
3. THE Admin_Service SHALL include Authorization header with Bearer token in all requests

### Requirement 6: 国际化支持

**User Story:** As a user, I want to see the interface in my preferred language, so that I can use the system comfortably.

#### Acceptance Criteria

1. THE Task_Publish_Page SHALL support Chinese (zh) and English (en) languages
2. THE Task_Publish_Page SHALL display all labels, placeholders, and messages in the current locale
3. WHEN the locale changes, THE Task_Publish_Page SHALL update all displayed text accordingly
