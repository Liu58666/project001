# Design Document: Admin Task Publish

## Overview

管理端任务发布功能允许管理员（role >= 3）创建并发布任务给指定的角色或用户。该功能参考现有的消息群发功能（BroadcastMessage.vue）的设计风格和交互模式，保持 UI/UX 一致性。

主要组件：
- `TaskPublish.vue` - 任务发布页面组件
- `taskService.js` - 任务相关 API 服务

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TaskPublish.vue                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Form Section                                        │   │
│  │  - Title Input (maxlength: 200)                     │   │
│  │  - Content Textarea (maxlength: 5000)               │   │
│  │  - Role Chips (multi-select)                        │   │
│  │  - User Selection Card → Modal                      │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Bottom Bar                                          │   │
│  │  - Summary (roles + users count)                    │   │
│  │  - Back Button                                       │   │
│  │  - Submit Button                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  User Selection Modal                                │   │
│  │  - Search Input                                      │   │
│  │  - User List with Checkboxes                        │   │
│  │  - Selected Count + Done Button                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    taskService.js                           │
│  - createTask({ title, content, roles, user_ids })         │
│  → POST /api/admin/tasks                                    │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API                              │
│  POST /api/admin/tasks                                      │
│  Response: TaskOut { id, title, content, recipient_count }  │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### TaskPublish.vue

Vue 3 Composition API 组件，使用 `<script setup>` 语法。

**依赖：**
- `vue-router` - 路由导航
- `@/stores/i18n` - 国际化
- `@/stores/user` - 用户状态和认证
- `@/stores/error` - 错误提示
- `@/stores/success` - 成功提示
- `@/services/adminService` - 用户列表 API
- `@/services/taskService` - 任务 API（新建）
- `@/utils/roles` - 角色工具函数

**状态：**
```javascript
// 表单状态
const form = reactive({
  title: '',      // 任务标题
  content: '',    // 任务内容
  roles: []       // 选中的角色 ID 数组
})

// 用户选择
const selectedUsers = ref([])      // 选中的用户对象数组
const users = ref([])              // 用户列表
const searchQuery = ref('')        // 搜索关键词
const isUserModalOpen = ref(false) // 弹窗状态
const isLoadingUsers = ref(false)  // 加载状态

// 提交状态
const isSubmitting = ref(false)

// 页面动画
const pageEnter = ref(false)
```

**计算属性：**
```javascript
const isZh = computed(() => i18n.locale === 'zh')
const roleOptions = computed(() => getRoleOptions(isZh.value ? 'zh' : 'en'))
const filteredUsers = computed(() => {
  // 根据 searchQuery 过滤用户列表
})
```

**方法：**
```javascript
function toggleRole(role)           // 切换角色选择
function toggleUser(user)           // 切换用户选择
function removeUser(userId)         // 移除已选用户
function openUserModal()            // 打开用户选择弹窗
function closeUserModal()           // 关闭用户选择弹窗
async function loadUsers()          // 加载用户列表
async function handleSubmit()       // 提交任务
function checkPermission()          // 检查管理员权限
```

### taskService.js

新建的任务服务模块。

```javascript
// src/services/taskService.js
import { apiRequest } from './apiClient'

/**
 * 管理员发布任务
 * POST /api/admin/tasks
 * @param {object} params - { title, content, roles, user_ids }
 * @returns {Promise<TaskOut>}
 */
export async function createTask({ title, content, roles, user_ids }) {
  if (!content) throw new Error('Missing content')
  if ((!roles || roles.length === 0) && (!user_ids || user_ids.length === 0)) {
    throw new Error('Must provide roles or user_ids')
  }
  return await apiRequest('POST', '/api/admin/tasks', {
    body: { title, content, roles, user_ids }
  })
}
```

## Data Models

### Request: AdminTaskCreateRequest

```typescript
interface AdminTaskCreateRequest {
  title: string       // 1-200 characters, required
  content: string     // 1-5000 characters, required
  roles?: number[]    // Optional: role IDs (0-4)
  user_ids?: number[] // Optional: specific user IDs
}
```

### Response: TaskOut

```typescript
interface TaskOut {
  id: number
  title: string
  content: string
  created_by: number
  published_at: string | null  // ISO8601 datetime
  created_at: string           // ISO8601 datetime
  updated_at: string           // ISO8601 datetime
  recipient_count: number | null
}
```

### User Object (from listAllUsers)

```typescript
interface User {
  id: number
  username: string
  display_name: string | null
  phone: string | null
  email: string | null
  role: number
  avatar_url: string | null
  is_active: boolean
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Character Limit Enforcement

*For any* input string exceeding the maximum length (200 for title, 5000 for content), the input field SHALL truncate or prevent the excess characters, ensuring the stored value never exceeds the limit.

**Validates: Requirements 1.3, 1.4**

### Property 2: Role Toggle Consistency

*For any* role in the available roles list, clicking the role chip SHALL toggle its presence in the selected roles array—if present, it is removed; if absent, it is added.

**Validates: Requirements 2.2**

### Property 3: User Search Filter

*For any* search query string, the filtered user list SHALL contain only users whose name, phone, or email contains the query string (case-insensitive).

**Validates: Requirements 3.3**

### Property 4: User Removal Consistency

*For any* selected user, clicking the remove button SHALL remove that user from the selectedUsers array, and the user count SHALL decrease by exactly one.

**Validates: Requirements 3.5, 3.6**

### Property 5: Authorization Header Presence

*For any* API request made by taskService, the request SHALL include an Authorization header with the format "Bearer {token}".

**Validates: Requirements 5.3**

### Property 6: Locale Text Consistency

*For any* supported locale (zh, en), all displayed text elements SHALL be in the corresponding language without mixing languages.

**Validates: Requirements 6.2**

## Error Handling

| Scenario | HTTP Status | User Message (zh) | User Message (en) |
|----------|-------------|-------------------|-------------------|
| Empty content | Client-side | 请输入任务内容 | Please enter task content |
| No recipients | Client-side | 请选择发送目标 | Please select recipients |
| No recipients (API) | 400 | 没有找到接收者 | No recipients found |
| Permission denied | 403 | 无权限执行此操作 | Permission denied |
| Network error | - | 发布失败 | Publish failed |

## Testing Strategy

### Unit Tests

使用 Vitest 进行单元测试：

1. **taskService.js 测试**
   - 测试 createTask 参数验证
   - 测试 API 请求格式
   - 测试错误处理

2. **组件逻辑测试**
   - 测试 toggleRole 函数
   - 测试 filteredUsers 计算属性
   - 测试表单验证逻辑

### Property-Based Tests

使用 fast-check 进行属性测试：

1. **Property 1**: 生成随机长字符串，验证截断行为
2. **Property 2**: 生成随机角色序列，验证 toggle 一致性
3. **Property 3**: 生成随机用户列表和搜索词，验证过滤结果
4. **Property 4**: 生成随机用户选择/移除序列，验证计数一致性

### Integration Tests

1. 测试完整的任务发布流程
2. 测试权限检查和重定向
3. 测试成功/失败响应处理
