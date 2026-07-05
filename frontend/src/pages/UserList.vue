<template>
  <section class="user-list-page">
    <div class="page-container">
      <header class="page-header">
        <h1 class="page-title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }">
          {{ isZh ? '用户列表' : 'User Directory' }}
        </h1>
        <p class="page-subtitle reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '140ms' }">
          {{ isZh ? '浏览平台所有注册用户的公开信息。' : 'Browse public profiles of all registered users.' }}
        </p>
      </header>

      <!-- Search & Filter -->
      <div class="search-bar reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '200ms' }">
        <div class="search-input-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <input
            class="search-input"
            type="text"
            v-model="searchQuery"
            :placeholder="isZh ? '搜索用户名或姓名...' : 'Search by username or name...'"
            @input="handleSearch"
          />
        </div>
      </div>

      <!-- User List -->
      <div class="user-grid">
        <div v-if="isLoading" class="loading-state">
          {{ isZh ? '加载中...' : 'Loading...' }}
        </div>

        <div v-else-if="paginatedUsers.length === 0" class="empty-state">
          {{ isZh ? '暂无用户数据' : 'No users found' }}
        </div>

        <div
          v-else
          v-for="(user, idx) in paginatedUsers"
          :key="user.id"
          class="user-card reveal"
          :class="{ 'is-in': pageEnter }"
          :style="{ '--d': `${Math.min(800, 260 + idx * 60)}ms` }"
          @click="viewUserProfile(user)"
        >
          <div class="user-avatar">
            <img v-if="user.avatar_url" :src="user.avatar_url" :alt="user.display_name || user.username" />
            <span v-else class="avatar-letter">{{ getAvatarLetter(user) }}</span>
          </div>
          <div class="user-info">
            <div class="user-name">{{ user.display_name || user.username || '—' }}</div>
            <div class="user-meta">
              <span v-if="user.title" class="user-title">{{ user.title }}</span>
              <span v-if="user.department" class="user-dept">{{ user.department }}</span>
            </div>
            <div class="user-joined">
              {{ isZh ? '加入于 ' : 'Joined ' }}{{ formatDate(user.created_at) }}
            </div>
          </div>
          <div class="user-arrow">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m9 18 6-6-6-6"></path>
            </svg>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '400ms' }">
        <button
          class="page-btn nav-btn"
          :disabled="currentPage <= 1"
          @click="goToPage(currentPage - 1)"
        >
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m15 18-6-6 6-6"/>
          </svg>
          <span>{{ isZh ? '上一页' : 'Prev' }}</span>
        </button>
        
        <div class="page-numbers">
          <button
            v-if="currentPage > 3"
            class="page-btn num-btn"
            @click="goToPage(1)"
          >1</button>
          <span v-if="currentPage > 4" class="page-ellipsis">...</span>
          
          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-btn num-btn"
            :class="{ active: page === currentPage }"
            @click="goToPage(page)"
          >{{ page }}</button>
          
          <span v-if="currentPage < totalPages - 3" class="page-ellipsis">...</span>
          <button
            v-if="currentPage < totalPages - 2"
            class="page-btn num-btn"
            @click="goToPage(totalPages)"
          >{{ totalPages }}</button>
        </div>
        
        <button
          class="page-btn nav-btn"
          :disabled="currentPage >= totalPages"
          @click="goToPage(currentPage + 1)"
        >
          <span>{{ isZh ? '下一页' : 'Next' }}</span>
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Bottom bar -->
    <div class="bottom-bar">
      <div class="bottom-inner">
        <div class="bottom-left">
          <div class="bottom-title">{{ isZh ? '用户目录' : 'User Directory' }}</div>
          <div class="bottom-sub">{{ isZh ? `共 ${totalUsers} 位用户` : `${totalUsers} users total` }}</div>
        </div>
        <div class="bottom-right">
          <button class="btn ghost" type="button" @click="router.push('/user')">
            {{ isZh ? '返回' : 'Back' }}
          </button>
          <button class="btn ghost" type="button" :disabled="isLoading" @click="loadUsers">
            {{ isZh ? '刷新' : 'Refresh' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Edit User Modal -->
    <div v-if="isEditOpen" class="modal-layer" @click.self="closeEditModal">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">{{ isZh ? '编辑用户' : 'Edit User' }}</div>
          <button class="modal-close" type="button" @click="closeEditModal">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6 6 18M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="modal-body" @click="isRoleDropdownOpen = false">
          <div class="form-row">
            <label class="form-label">{{ isZh ? '用户名' : 'Username' }}</label>
            <input class="form-input" type="text" v-model="editForm.username" />
          </div>
          <div class="form-row">
            <label class="form-label">{{ isZh ? '手机号' : 'Phone' }}</label>
            <input class="form-input" type="text" v-model="editForm.phone" />
          </div>
          <div class="form-row">
            <label class="form-label">{{ isZh ? '邮箱' : 'Email' }}</label>
            <input class="form-input" type="email" v-model="editForm.email" />
          </div>
          <div class="form-row">
            <label class="form-label">{{ isZh ? '生日' : 'Birthday' }}</label>
            <input class="form-input" type="date" v-model="editForm.birthday" />
          </div>
          <div class="form-row">
            <label class="form-label">{{ isZh ? '角色' : 'Role' }}</label>
            <div class="custom-select" :class="{ open: isRoleDropdownOpen }" @click.stop>
              <div class="custom-select-trigger" @click="isRoleDropdownOpen = !isRoleDropdownOpen">
                <span class="custom-select-value">{{ currentRoleLabel }}</span>
                <svg class="custom-select-arrow" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="m6 9 6 6 6-6"/>
                </svg>
              </div>
              <div class="custom-select-dropdown" v-if="isRoleDropdownOpen">
                <div 
                  v-for="opt in roleOptions" 
                  :key="opt.value" 
                  class="custom-select-option"
                  :class="{ selected: editForm.role === opt.value }"
                  @click="selectRole(opt.value)"
                >
                  <span>{{ opt.label }}</span>
                  <svg v-if="editForm.role === opt.value" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>
          <div class="form-row form-row--checkbox">
            <label class="checkbox-label">
              <input type="checkbox" v-model="editForm.is_active" />
              <span>{{ isZh ? '账号激活' : 'Active' }}</span>
            </label>
          </div>
          <div class="form-row">
            <label class="form-label">{{ isZh ? '重置密码（留空不修改）' : 'Reset Password (leave empty to keep)' }}</label>
            <input class="form-input" type="password" v-model="editForm.password" :placeholder="isZh ? '输入新密码' : 'Enter new password'" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn ghost" type="button" @click="closeEditModal" :disabled="isSaving">
            {{ isZh ? '取消' : 'Cancel' }}
          </button>
          <button class="btn primary" type="button" @click="saveUserEdit" :disabled="isSaving">
            {{ isSaving ? (isZh ? '保存中...' : 'Saving...') : (isZh ? '保存' : 'Save') }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'
import { useUserStore } from '@/stores/user'
import { useErrorStore } from '@/stores/error'
import { useSuccessStore } from '@/stores/success'
import { listAllUsers, updateUserByAdmin } from '@/services/adminService'
import { getUserAvatars, buildAvatarMap } from '@/services/userService'
import { getRoleOptions } from '@/utils/roles'

const router = useRouter()
const i18n = useI18nStore()
const userStore = useUserStore()
const errorStore = useErrorStore()
const successStore = useSuccessStore()

const isZh = computed(() => i18n.locale === 'zh')
const pageEnter = ref(false)

// Role options from global definition
const roleOptions = computed(() => getRoleOptions(isZh.value ? 'zh' : 'en'))

// Check if current user has manager role (role >= 3)
const isManager = computed(() => {
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
})

// Check if current user has admin role (role === 4)
const isAdmin = computed(() => {
  try {
    const token = userStore.accessToken
    if (!token) return false
    const [, payload] = String(token).split('.')
    if (!payload) return false
    const json = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    return json?.role === 4
  } catch {
    return false
  }
})

// Data
const allUsers = ref([])  // 全量用户数据
const avatarMap = ref({})
const isLoading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = 20

// Edit modal
const isEditOpen = ref(false)
const editingUser = ref(null)
const editForm = ref({})
const isSaving = ref(false)
const isRoleDropdownOpen = ref(false)

// Computed for current role label
const currentRoleLabel = computed(() => {
  const opt = roleOptions.value.find(o => o.value === editForm.value.role)
  return opt ? opt.label : ''
})

function selectRole(value) {
  editForm.value.role = value
  isRoleDropdownOpen.value = false
}

// 搜索过滤全量数据
const filteredUsers = computed(() => {
  if (!searchQuery.value.trim()) return allUsers.value
  const q = searchQuery.value.toLowerCase()
  return allUsers.value.filter(u => {
    const name = (u.display_name || u.username || '').toLowerCase()
    const realName = (u.real_name || '').toLowerCase()
    const email = (u.email || '').toLowerCase()
    const phone = (u.phone || '').toLowerCase()
    return name.includes(q) || realName.includes(q) || email.includes(q) || phone.includes(q)
  })
})

// 分页显示
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredUsers.value.slice(start, start + pageSize)
})

const totalUsers = computed(() => filteredUsers.value.length)
const totalPages = computed(() => Math.ceil(totalUsers.value / pageSize))

// 计算可见的页码
const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  let start = Math.max(1, current - 2)
  let end = Math.min(total, current + 2)
  
  // 确保至少显示 5 个页码（如果有的话）
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4)
    } else if (end === total) {
      start = Math.max(1, end - 4)
    }
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

function getAvatarLetter(user) {
  const name = user.display_name || user.username || user.real_name || 'U'
  return (name[0] || 'U').toUpperCase()
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return '—'
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function handleSearch() {
  // 搜索时重置到第一页
  currentPage.value = 1
}

function viewUserProfile(user) {
  if (isManager.value) {
    openEditModal(user)
  }
}

function openEditModal(user) {
  editingUser.value = user
  editForm.value = {
    username: user.username || '',
    phone: user.phone || '',
    email: user.email || '',
    birthday: user.birthday || '',
    is_active: user.is_active !== false,
    role: user.role ?? 1,
    password: ''
  }
  isEditOpen.value = true
}

function closeEditModal() {
  isEditOpen.value = false
  editingUser.value = null
  editForm.value = {}
  isRoleDropdownOpen.value = false
}

async function saveUserEdit() {
  if (!editingUser.value || isSaving.value) return
  
  isSaving.value = true
  try {
    const updates = {}
    if (editForm.value.username?.trim()) updates.username = editForm.value.username.trim()
    if (editForm.value.phone?.trim()) updates.phone = editForm.value.phone.trim()
    if (editForm.value.email?.trim()) updates.email = editForm.value.email.trim()
    if (editForm.value.birthday?.trim()) updates.birthday = editForm.value.birthday.trim()
    updates.is_active = editForm.value.is_active
    updates.role = editForm.value.role
    if (editForm.value.password?.trim()) updates.password = editForm.value.password.trim()

    await updateUserByAdmin(editingUser.value.id, updates)
    successStore.showSuccess(isZh.value ? '用户信息已更新' : 'User updated')
    closeEditModal()
    await loadUsers()
  } catch (e) {
    let msg = ''
    // 尝试解析错误消息
    try {
      if (typeof e?.message === 'string') {
        const parsed = JSON.parse(e.message)
        // 处理常见的错误格式
        if (parsed.detail) {
          if (Array.isArray(parsed.detail)) {
            // FastAPI 验证错误格式
            msg = parsed.detail.map(d => d.msg || d.message || d).join(', ')
          } else {
            msg = parsed.detail
          }
        } else if (parsed.message) {
          msg = parsed.message
        } else {
          msg = e.message
        }
      } else {
        msg = e?.message || String(e)
      }
    } catch {
      msg = e?.message || String(e)
    }
    
    // 友好错误提示映射
    const friendlyMessages = {
      zh: {
        password_short: '密码长度至少需要6个字符',
        username_exists: '用户名已被使用',
        phone_exists: '手机号已被使用',
        email_exists: '邮箱已被使用',
        email_invalid: '邮箱格式不正确',
        phone_invalid: '手机号格式不正确',
        permission_denied: '无权限执行此操作',
        not_found: '用户不存在',
        validation_failed: '输入信息有误，请检查后重试',
        network_error: '网络连接失败，请稍后重试',
        server_error: '服务器错误，请稍后重试',
        default: '更新失败，请稍后重试'
      },
      en: {
        password_short: 'Password must be at least 6 characters',
        username_exists: 'Username already taken',
        phone_exists: 'Phone number already in use',
        email_exists: 'Email already in use',
        email_invalid: 'Invalid email format',
        phone_invalid: 'Invalid phone number format',
        permission_denied: 'Permission denied',
        not_found: 'User not found',
        validation_failed: 'Invalid input, please check and try again',
        network_error: 'Network error, please try again',
        server_error: 'Server error, please try again',
        default: 'Update failed, please try again'
      }
    }
    
    const lang = isZh.value ? 'zh' : 'en'
    const msgLower = msg.toLowerCase()
    
    // 根据错误内容匹配友好提示
    let friendlyMsg = ''
    if (msgLower.includes('password') && (msgLower.includes('short') || msgLower.includes('least') || msgLower.includes('min') || msgLower.includes('characters'))) {
      friendlyMsg = friendlyMessages[lang].password_short
    } else if (e?.status === 409 || msgLower.includes('already') || msgLower.includes('exists') || msgLower.includes('duplicate')) {
      if (msgLower.includes('username')) {
        friendlyMsg = friendlyMessages[lang].username_exists
      } else if (msgLower.includes('phone')) {
        friendlyMsg = friendlyMessages[lang].phone_exists
      } else if (msgLower.includes('email')) {
        friendlyMsg = friendlyMessages[lang].email_exists
      } else {
        friendlyMsg = isZh.value ? '用户名或手机号已存在' : 'Username or phone already exists'
      }
    } else if (msgLower.includes('email') && (msgLower.includes('invalid') || msgLower.includes('format'))) {
      friendlyMsg = friendlyMessages[lang].email_invalid
    } else if (msgLower.includes('phone') && (msgLower.includes('invalid') || msgLower.includes('format'))) {
      friendlyMsg = friendlyMessages[lang].phone_invalid
    } else if (e?.status === 403 || msgLower.includes('permission') || msgLower.includes('forbidden')) {
      friendlyMsg = friendlyMessages[lang].permission_denied
    } else if (e?.status === 404 || msgLower.includes('not found')) {
      friendlyMsg = friendlyMessages[lang].not_found
    } else if (e?.status === 422) {
      friendlyMsg = friendlyMessages[lang].validation_failed
    } else if (e?.status >= 500 || msgLower.includes('server')) {
      friendlyMsg = friendlyMessages[lang].server_error
    } else if (msgLower.includes('network') || msgLower.includes('fetch')) {
      friendlyMsg = friendlyMessages[lang].network_error
    } else {
      friendlyMsg = friendlyMessages[lang].default
    }
    
    errorStore.showError(friendlyMsg)
  } finally {
    isSaving.value = false
  }
}

function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  // 不再需要重新加载，因为数据已全部在前端
}

async function loadUsers() {
  if (!isManager.value) {
    errorStore.showError(isZh.value ? '无权限访问此页面' : 'Permission denied')
    return
  }
  
  isLoading.value = true
  try {
    // 分批加载全部用户（API 限制每次最多 200）
    const batchSize = 200
    let allUserList = []
    let offset = 0
    let hasMore = true
    
    // 先加载头像
    if (!avatarMap.value || Object.keys(avatarMap.value).length === 0) {
      const avatarsResponse = await getUserAvatars({ limit: 200, offset: 0 }).catch(() => [])
      avatarMap.value = buildAvatarMap(avatarsResponse)
    }
    
    // 分批加载用户
    while (hasMore) {
      const response = await listAllUsers({ limit: batchSize, offset })
      
      let userList = []
      if (Array.isArray(response)) {
        userList = response
      } else {
        userList = response.items || response.users || response.data || []
      }
      
      allUserList = allUserList.concat(userList)
      
      // 如果返回数量小于请求数量，说明没有更多了
      if (userList.length < batchSize) {
        hasMore = false
      } else {
        offset += batchSize
      }
    }
    
    // 将头像映射到用户对象
    allUsers.value = allUserList.map(u => ({
      ...u,
      avatar_url: avatarMap.value[u.id] || ''
    }))
    
    // 重置到第一页
    currentPage.value = 1
  } catch (e) {
    if (e?.status === 403) {
      errorStore.showError(isZh.value ? '无权限访问用户列表' : 'Permission denied')
    } else {
      errorStore.showError(isZh.value ? `加载用户失败：${e?.message || e}` : `Failed to load users: ${e?.message || e}`)
    }
    allUsers.value = []
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  requestAnimationFrame(() => {
    pageEnter.value = true
  })
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  loadUsers()
})
</script>

<style scoped>
.reveal {
  opacity: 0;
  transform: translate3d(0, 22px, 0);
  filter: blur(10px);
  transition: opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1), transform 0.9s cubic-bezier(0.16, 1, 0.3, 1), filter 0.9s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--d, 0ms);
  will-change: opacity, transform, filter;
}
.reveal.is-in { opacity: 1; transform: translate3d(0, 0, 0); filter: blur(0); }

.user-list-page {
  min-height: 100vh;
  background: #ffffff;
  padding: 120px 24px 148px;
}

.page-container {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 40px;
}

.page-title {
  font-size: 48px;
  font-weight: 700;
  color: #000000;
  margin: 0 0 12px;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 16px;
  color: rgba(0, 0, 0, 0.6);
  margin: 0;
}

/* Search */
.search-bar {
  margin-bottom: 32px;
}

.search-input-wrapper {
  position: relative;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(0, 0, 0, 0.4);
}

.search-input {
  width: 100%;
  height: 48px;
  padding: 0 16px 0 48px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 12px;
  font-size: 15px;
  color: #000000;
  background: #ffffff;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.search-input:focus {
  border-color: #000000;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.08);
}

.search-input::placeholder {
  color: rgba(0, 0, 0, 0.4);
}

/* User Grid */
.user-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.loading-state,
.empty-state {
  padding: 48px 24px;
  text-align: center;
  color: rgba(0, 0, 0, 0.5);
  font-size: 15px;
}

/* User Card */
.user-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: #ffffff;
  border: 1.5px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.user-card:hover {
  border-color: #000000;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.user-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-letter {
  font-size: 22px;
  font-weight: 700;
  color: rgba(0, 0, 0, 0.5);
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
  color: #000000;
  margin-bottom: 4px;
}

.user-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}

.user-title,
.user-dept {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.6);
}

.user-title::after {
  content: '·';
  margin-left: 8px;
  color: rgba(0, 0, 0, 0.3);
}

.user-dept {
  color: rgba(0, 0, 0, 0.5);
}

.user-joined {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.4);
}

.user-arrow {
  color: rgba(0, 0, 0, 0.3);
  transition: color 0.2s ease, transform 0.2s ease;
}

.user-card:hover .user-arrow {
  color: #000000;
  transform: translateX(4px);
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 40px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 16px;
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 8px;
}

.page-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.6);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-btn.nav-btn {
  height: 40px;
  padding: 0 16px;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.page-btn.nav-btn:hover:not(:disabled) {
  background: #000000;
  color: #ffffff;
  border-color: #000000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.page-btn.nav-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.page-btn.num-btn {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  font-weight: 600;
}

.page-btn.num-btn:hover:not(:disabled):not(.active) {
  background: rgba(0, 0, 0, 0.06);
  color: #000000;
}

.page-btn.num-btn.active {
  background: #000000;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.page-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.page-ellipsis {
  width: 32px;
  text-align: center;
  color: rgba(0, 0, 0, 0.3);
  font-weight: 500;
  letter-spacing: 2px;
}

.page-info {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.6);
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
}

.bottom-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.bottom-left { min-width: 0; }
.bottom-title { font-size: 18px; font-weight: 700; color: #000000; letter-spacing: -0.01em; }
.bottom-sub { font-size: 14px; color: rgba(0, 0, 0, 0.7); margin-top: 4px; }
.bottom-right { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }

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

/* Modal */
.modal-layer {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.modal {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #000000;
}

.modal-close {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 0, 0, 0.5);
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.06);
  color: #000000;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.form-row {
  margin-bottom: 16px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
  margin-bottom: 6px;
}

.form-input,
.form-select {
  width: 100%;
  height: 44px;
  padding: 0 14px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  font-size: 15px;
  color: #000000;
  background: #ffffff;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-input:focus,
.form-select:focus {
  border-color: #000000;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.08);
}

.form-row--checkbox {
  margin-top: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 14px;
  color: #000000;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #000000;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
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

/* Custom Select */
.custom-select {
  position: relative;
  width: 100%;
}

.custom-select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 44px;
  padding: 0 14px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  font-size: 15px;
  color: #000000;
  background: #ffffff;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.custom-select-trigger:hover {
  border-color: rgba(0, 0, 0, 0.3);
}

.custom-select.open .custom-select-trigger {
  border-color: #000000;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.08);
}

.custom-select-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.custom-select-arrow {
  flex-shrink: 0;
  color: rgba(0, 0, 0, 0.4);
  transition: transform 0.2s ease;
}

.custom-select.open .custom-select-arrow {
  transform: rotate(180deg);
}

.custom-select-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: 10;
  overflow: hidden;
  animation: dropdownFadeIn 0.15s ease;
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.custom-select-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  font-size: 14px;
  color: #000000;
  cursor: pointer;
  transition: background 0.15s ease;
}

.custom-select-option:hover {
  background: rgba(0, 0, 0, 0.04);
}

.custom-select-option.selected {
  background: rgba(0, 0, 0, 0.06);
  font-weight: 600;
}

.custom-select-option svg {
  color: #000000;
}
</style>
