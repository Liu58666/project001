<template>
  <section class="task-publish-page">
    <div class="page-container">
      <header class="page-header">
        <h1 class="page-title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }">
          {{ isZh ? '发布任务' : 'Publish Task' }}
        </h1>
        <p class="page-subtitle reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '140ms' }">
          {{ isZh ? '向指定角色或用户发布任务' : 'Publish tasks to specific roles or users' }}
        </p>
      </header>

      <div class="task-layout">
        <!-- Form Section -->
        <div class="form-section reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '200ms' }">
          <!-- 2.2 表单输入区域 -->
          <div class="form-field">
            <label class="form-label">
              {{ isZh ? '任务标题' : 'Task Title' }}
              <span class="char-count">{{ form.title.length }}/200</span>
            </label>
            <input
              v-model="form.title"
              type="text"
              class="form-input"
              maxlength="200"
              :placeholder="isZh ? '请输入任务标题' : 'Enter task title'"
            />
          </div>

          <div class="form-field">
            <label class="form-label">
              {{ isZh ? '任务内容' : 'Task Content' }} *
              <span class="char-count">{{ form.content.length }}/5000</span>
            </label>
            <textarea
              v-model="form.content"
              class="form-textarea"
              maxlength="5000"
              :placeholder="isZh ? '请输入任务内容...' : 'Enter task content...'"
              rows="6"
            ></textarea>
          </div>

          <!-- 2.3 角色选择功能 -->
          <div class="form-field">
            <label class="form-label">{{ isZh ? '按角色发送' : 'Send by Role' }}</label>
            <div class="role-chips">
              <button
                v-for="role in roleOptions"
                :key="role.value"
                type="button"
                class="role-chip"
                :class="{ active: form.roles.includes(role.value) }"
                @click="toggleRole(role.value)"
              >
                {{ role.label }}
              </button>
            </div>
          </div>

          <!-- 2.4 用户选择功能 -->
          <div class="form-field">
            <label class="form-label">
              {{ isZh ? '指定用户发送' : 'Send to Specific Users' }}
              <span class="label-hint">({{ selectedUsers.length }} {{ isZh ? '已选' : 'selected' }})</span>
            </label>
            
            <!-- 已选用户标签 -->
            <div class="selected-users" v-if="selectedUsers.length > 0">
              <div 
                v-for="user in selectedUsers" 
                :key="user.id" 
                class="selected-user-tag"
              >
                <span>{{ user.display_name || user.username }}</span>
                <button type="button" class="tag-remove" @click="removeUser(user.id)">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- 选择用户卡片按钮 -->
            <div class="user-select-card" @click="openUserModal">
              <div class="user-select-icon">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </div>
              <div class="user-select-content">
                <div class="user-select-title">{{ isZh ? '点击选择用户' : 'Click to Select Users' }}</div>
                <div class="user-select-desc">
                  {{ selectedUsers.length > 0 
                    ? (isZh ? `已选择 ${selectedUsers.length} 位用户` : `${selectedUsers.length} users selected`) 
                    : (isZh ? '从用户列表中选择接收者' : 'Choose recipients from user list') 
                  }}
                </div>
              </div>
              <div class="user-select-arrow">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="m9 18 6-6-6-6"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 2.6 底部操作栏 -->
    <div class="bottom-bar">
      <div class="bottom-inner">
        <div class="bottom-left">
          <div class="bottom-title">{{ isZh ? '发布任务' : 'Publish Task' }}</div>
          <div class="bottom-sub">
            {{ form.roles.length > 0 ? `${form.roles.length} ${isZh ? '个角色' : 'roles'}` : '' }}
            {{ form.roles.length > 0 && selectedUsers.length > 0 ? ' + ' : '' }}
            {{ selectedUsers.length > 0 ? `${selectedUsers.length} ${isZh ? '位用户' : 'users'}` : '' }}
            {{ form.roles.length === 0 && selectedUsers.length === 0 ? (isZh ? '请选择发送目标' : 'Select recipients') : '' }}
          </div>
        </div>
        <div class="bottom-right">
          <button class="btn ghost" type="button" @click="router.push('/user')">
            {{ isZh ? '返回' : 'Back' }}
          </button>
          <button class="btn primary" type="button" :disabled="isSubmitting" @click="handleSubmit">
            {{ isSubmitting ? (isZh ? '发布中...' : 'Publishing...') : (isZh ? '发布任务' : 'Publish Task') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 2.5 用户选择弹窗 -->
    <div v-if="isUserModalOpen" class="modal-overlay" @click="closeUserModal">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <div class="modal-title">{{ isZh ? '选择用户' : 'Select Users' }}</div>
          <button class="modal-close" @click="closeUserModal">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <div class="modal-search">
          <svg class="search-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            :placeholder="isZh ? '搜索用户名、手机号或邮箱...' : 'Search by name, phone or email...'"
          />
        </div>

        <div class="modal-body">
          <div v-if="isLoadingUsers" class="loading-users">
            {{ isZh ? '加载中...' : 'Loading...' }}
          </div>
          <div v-else-if="filteredUsers.length === 0" class="no-users">
            {{ isZh ? '没有找到用户' : 'No users found' }}
          </div>
          <div v-else class="users-list">
            <div
              v-for="user in filteredUsers"
              :key="user.id"
              class="user-item"
              :class="{ selected: isUserSelected(user.id) }"
              @click="toggleUser(user)"
            >
              <div class="user-checkbox">
                <svg v-if="isUserSelected(user.id)" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
              <div class="user-avatar">
                <img v-if="user.avatar_url" :src="user.avatar_url" :alt="user.username" />
                <span v-else>{{ getAvatarLetter(user) }}</span>
              </div>
              <div class="user-info">
                <div class="user-name">{{ user.display_name || user.username || '—' }}</div>
                <div class="user-meta">
                  <span class="user-role">{{ getRoleNameLocal(user.role) }}</span>
                  <span v-if="user.phone" class="user-phone">{{ user.phone }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <div class="modal-footer-info">
            {{ selectedUsers.length }} {{ isZh ? '位用户已选择' : 'users selected' }}
          </div>
          <button class="btn primary" @click="closeUserModal">
            {{ isZh ? '确定' : 'Done' }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'
import { useUserStore } from '@/stores/user'
import { useErrorStore } from '@/stores/error'
import { useSuccessStore } from '@/stores/success'
import { listAllUsers } from '@/services/adminService'
import { createTask } from '@/services/taskService'
import { getUserAvatars, buildAvatarMap } from '@/services/userService'
import { getRoleOptions, getRoleName } from '@/utils/roles'

const router = useRouter()
const i18n = useI18nStore()
const userStore = useUserStore()
const errorStore = useErrorStore()
const successStore = useSuccessStore()

// 2.8 国际化
const isZh = computed(() => i18n.locale === 'zh')

// 页面进入动画
const pageEnter = ref(false)

// 表单状态
const form = reactive({
  title: '',
  content: '',
  roles: []
})

// 用户选择状态
const selectedUsers = ref([])
const users = ref([])
const avatarMap = ref({})
const searchQuery = ref('')
const isUserModalOpen = ref(false)
const isLoadingUsers = ref(false)

// 提交状态
const isSubmitting = ref(false)

// 角色选项
const roleOptions = computed(() => getRoleOptions(isZh.value ? 'zh' : 'en'))

// 2.5 过滤用户列表
const filteredUsers = computed(() => {
  if (!searchQuery.value.trim()) return users.value
  const q = searchQuery.value.toLowerCase()
  return users.value.filter(u => {
    const name = (u.display_name || u.username || '').toLowerCase()
    const phone = (u.phone || '').toLowerCase()
    const email = (u.email || '').toLowerCase()
    return name.includes(q) || phone.includes(q) || email.includes(q)
  })
})

// 2.3 切换角色选择
function toggleRole(role) {
  const idx = form.roles.indexOf(role)
  if (idx === -1) form.roles.push(role)
  else form.roles.splice(idx, 1)
}

// 检查用户是否已选中
function isUserSelected(userId) {
  return selectedUsers.value.some(u => u.id === userId)
}

// 2.5 切换用户选择
function toggleUser(user) {
  const idx = selectedUsers.value.findIndex(u => u.id === user.id)
  if (idx === -1) {
    selectedUsers.value.push(user)
  } else {
    selectedUsers.value.splice(idx, 1)
  }
}

// 2.4 移除已选用户
function removeUser(userId) {
  const idx = selectedUsers.value.findIndex(u => u.id === userId)
  if (idx !== -1) selectedUsers.value.splice(idx, 1)
}

// 获取用户头像字母
function getAvatarLetter(user) {
  const name = user.display_name || user.username || 'U'
  return (name[0] || 'U').toUpperCase()
}

// 获取角色名称
function getRoleNameLocal(role) {
  return getRoleName(role, isZh.value ? 'zh' : 'en')
}

// 2.5 打开用户选择弹窗
function openUserModal() {
  isUserModalOpen.value = true
  if (users.value.length === 0) {
    loadUsers()
  }
}

// 2.5 关闭用户选择弹窗
function closeUserModal() {
  isUserModalOpen.value = false
  searchQuery.value = ''
}

// 2.5 加载用户列表
async function loadUsers() {
  isLoadingUsers.value = true
  try {
    // 并行加载用户列表和头像
    const [usersResponse, avatarsResponse] = await Promise.all([
      listAllUsers({ limit: 200, offset: 0 }),
      getUserAvatars({ limit: 500, offset: 0 }).catch(() => [])
    ])
    
    // 构建头像映射
    avatarMap.value = buildAvatarMap(avatarsResponse)
    
    // 处理用户列表
    let userList = []
    if (Array.isArray(usersResponse)) {
      userList = usersResponse
    } else {
      userList = usersResponse.items || usersResponse.users || usersResponse.data || []
    }
    
    // 将头像映射到用户对象
    users.value = userList.map(u => ({
      ...u,
      avatar_url: avatarMap.value[u.id] || ''
    }))
  } catch (e) {
    errorStore.showError(isZh.value ? '加载用户失败' : 'Failed to load users')
    users.value = []
  } finally {
    isLoadingUsers.value = false
  }
}

// 2.7 表单提交
async function handleSubmit() {
  // 验证内容非空
  if (!form.content.trim()) {
    errorStore.showError(isZh.value ? '请输入任务内容' : 'Please enter task content')
    return
  }

  // 验证接收者非空
  const userIds = selectedUsers.value.map(u => u.id)
  if (form.roles.length === 0 && userIds.length === 0) {
    errorStore.showError(isZh.value ? '请选择发送目标' : 'Please select recipients')
    return
  }

  isSubmitting.value = true
  try {
    const result = await createTask({
      title: form.title.trim() || undefined,
      content: form.content.trim(),
      roles: form.roles.length > 0 ? form.roles : undefined,
      user_ids: userIds.length > 0 ? userIds : undefined
    })

    // 成功响应
    successStore.showSuccess(
      isZh.value 
        ? `任务已发布给 ${result.recipient_count || 0} 位用户` 
        : `Task published to ${result.recipient_count || 0} users`
    )

    // 重置表单
    form.title = ''
    form.content = ''
    form.roles = []
    selectedUsers.value = []
  } catch (err) {
    // 错误响应处理
    const message = err?.message || ''
    if (message.includes('403') || message.toLowerCase().includes('permission')) {
      errorStore.showError(isZh.value ? '无权限执行此操作' : 'Permission denied')
    } else if (message.includes('400') || message.toLowerCase().includes('no recipients')) {
      errorStore.showError(isZh.value ? '没有找到接收者' : 'No recipients found')
    } else {
      errorStore.showError(isZh.value ? '发布失败' : 'Publish failed')
    }
  } finally {
    isSubmitting.value = false
  }
}

// 权限检查：role >= 3 可访问
function checkPermission() {
  try {
    const token = userStore.accessToken
    if (!token) return false
    const [, payload] = String(token).split('.')
    if (!payload) return false
    const json = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    return json?.role >= 3
  } catch {
    return false
  }
}

onMounted(() => {
  // 权限检查
  if (!userStore.isLoggedIn || !checkPermission()) {
    router.push('/user')
    return
  }
  
  // 页面进入动画
  requestAnimationFrame(() => {
    pageEnter.value = true
  })
})
</script>


<style scoped>
/* Reveal animation */
.reveal {
  opacity: 0;
  transform: translate3d(0, 22px, 0);
  filter: blur(10px);
  transition: opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1), transform 0.9s cubic-bezier(0.16, 1, 0.3, 1), filter 0.9s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--d, 0ms);
}
.reveal.is-in { opacity: 1; transform: translate3d(0, 0, 0); filter: blur(0); }

/* Page layout */
.task-publish-page {
  min-height: 100vh;
  background: #fbfbfb;
  padding: 120px 24px 148px;
}

.page-container {
  max-width: 720px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 40px;
}

.page-title {
  font-size: 48px;
  font-weight: 700;
  color: #0b0f19;
  margin: 0 0 12px;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 16px;
  color: rgba(0, 0, 0, 0.55);
  margin: 0;
}

.task-layout {
  width: 100%;
}

.form-section {
  width: 100%;
}

/* Form fields */
.form-field {
  margin-bottom: 28px;
}

.form-field:last-child {
  margin-bottom: 0;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #000000;
  margin-bottom: 12px;
}

.label-hint {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.4);
  text-transform: none;
  letter-spacing: 0;
}

.char-count {
  margin-left: auto;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.4);
  text-transform: none;
  letter-spacing: 0;
  font-size: 12px;
}

.form-input {
  width: 100%;
  height: 52px;
  padding: 0 18px;
  border: 1.5px solid rgba(0, 0, 0, 0.12);
  border-radius: 14px;
  font-size: 15px;
  background: #fff;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #000000;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.06);
}

.form-textarea {
  width: 100%;
  padding: 16px 18px;
  border: 1.5px solid rgba(0, 0, 0, 0.12);
  border-radius: 14px;
  font-size: 15px;
  font-family: inherit;
  background: #fff;
  resize: vertical;
  min-height: 140px;
  line-height: 1.6;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: #000000;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.06);
}

/* Role Chips */
.role-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.role-chip {
  padding: 10px 18px;
  border: 1.5px solid rgba(0, 0, 0, 0.12);
  border-radius: 999px;
  background: #fff;
  font-size: 13px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.6);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.role-chip:hover {
  border-color: #000000;
  color: #000000;
  transform: scale(1.03);
}

.role-chip:active {
  transform: scale(0.97);
}

.role-chip.active {
  background: #000000;
  border-color: #000000;
  color: #fff;
}

/* Selected Users Tags */
.selected-users {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.selected-user-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #1d4ed8;
}

.tag-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border: none;
  background: transparent;
  color: #1d4ed8;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.tag-remove:hover {
  background: rgba(59, 130, 246, 0.2);
}

/* User Select Card Button */
.user-select-card {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
  padding: 18px 20px;
  background: #ffffff;
  border: 1.5px solid rgba(0, 0, 0, 0.12);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-sizing: border-box;
}

.user-select-card:hover {
  border-color: rgba(0, 0, 0, 0.25);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.user-select-card:active {
  transform: scale(0.985);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.user-select-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f5f5f5 0%, #ebebeb 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: rgba(0, 0, 0, 0.45);
  transition: all 0.3s ease;
}

.user-select-card:hover .user-select-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #ffffff;
}

.user-select-content {
  flex: 1;
  min-width: 0;
}

.user-select-title {
  font-size: 15px;
  font-weight: 600;
  color: #0b0f19;
  margin-bottom: 4px;
}

.user-select-desc {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.5);
}

.user-select-arrow {
  color: rgba(0, 0, 0, 0.25);
  transition: all 0.2s ease;
}

.user-select-card:hover .user-select-arrow {
  color: rgba(0, 0, 0, 0.5);
  transform: translateX(4px);
}

/* Modal Overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-container {
  width: 100%;
  max-width: 520px;
  max-height: 80vh;
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #0b0f19;
}

.modal-close {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 0, 0, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.1);
  color: rgba(0, 0, 0, 0.8);
}

.modal-search {
  position: relative;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.modal-search .search-icon {
  position: absolute;
  left: 40px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(0, 0, 0, 0.35);
}

.modal-search .search-input {
  width: 100%;
  height: 44px;
  padding: 0 16px 0 44px;
  border: 1.5px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  font-size: 14px;
  background: #fafafa;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.modal-search .search-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  min-height: 200px;
  max-height: 400px;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  background: #fafafa;
  border-radius: 0 0 20px 20px;
}

.modal-footer-info {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.5);
  font-weight: 500;
}

.modal-footer .btn {
  height: 40px;
  padding: 0 24px;
}

/* Users List in Modal */
.users-list {
  padding: 8px 0;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.user-item:hover {
  background: rgba(0, 0, 0, 0.03);
}

.user-item.selected {
  background: rgba(59, 130, 246, 0.08);
}

.user-item:active {
  background: rgba(59, 130, 246, 0.12);
}

.user-checkbox {
  width: 22px;
  height: 22px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s ease;
}

.user-item.selected .user-checkbox {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #fff;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  font-size: 16px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.4);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #0b0f19;
  margin-bottom: 2px;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.user-role {
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.no-users,
.loading-users {
  padding: 48px 24px;
  text-align: center;
  color: rgba(0, 0, 0, 0.4);
  font-size: 14px;
}

/* Bottom bar */
.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 40;
  background: #ffffff;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 -6px 32px rgba(0, 0, 0, 0.08);
  padding: 0 30px;
}

.bottom-inner {
  max-width: 1400px;
  margin: 0 auto;
  min-height: 72px;
  padding: 20px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.bottom-left {
  min-width: 0;
}

.bottom-title {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #000000;
}

.bottom-sub {
  margin-top: 4px;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.7);
  max-width: 720px;
}

.bottom-right {
  display: inline-flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

/* Buttons */
.btn {
  height: 36px;
  padding: 0 16px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  cursor: pointer;
  border: 1px solid #000000;
  background: transparent;
  color: #000000;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn:active:not(:disabled) {
  background: #000000;
  color: #ffffff;
  transform: scale(0.97);
}

.btn.primary:active:not(:disabled) {
  background: #ffffff;
  color: #000000;
  transform: scale(0.97);
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn.primary {
  background: #000000;
  border-color: #000000;
  color: #ffffff;
}

.btn.primary:hover:not(:disabled) {
  background: #1a1a1a;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.btn.ghost {
  border-color: rgba(0, 0, 0, 0.2);
}
</style>
