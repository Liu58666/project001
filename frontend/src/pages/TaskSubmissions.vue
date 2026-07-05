<template>
  <section class="task-submissions-page">
    <!-- Particle Background -->
    <div class="particles-bg">
      <div class="particle" v-for="n in 12" :key="n" :style="{ '--i': n }"></div>
    </div>

    <div class="page-container">
      <!-- Loading State -->
      <div v-if="isLoadingTask" class="loading-state">
        <div class="spinner"></div>
        <span>{{ isZh ? '加载中...' : 'Loading...' }}</span>
      </div>

      <template v-else-if="task">
        <header class="page-header">
          <div class="task-meta reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }">
            <button class="back-link" @click="router.push({ name: 'task-list' })">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m15 18-6-6 6-6"/>
              </svg>
              {{ isZh ? '返回任务列表' : 'Back to Tasks' }}
            </button>
          </div>
          <h1 class="page-title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '120ms' }">
            {{ task.title || (isZh ? '未命名任务' : 'Untitled Task') }}
          </h1>
          <p class="page-subtitle reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '160ms' }">
            {{ isZh ? '查看提交并评分' : 'View submissions and score' }} · {{ task.recipient_count || 0 }} {{ isZh ? '位接收者' : 'recipients' }}
          </p>
        </header>

        <!-- Task Content Preview -->
        <div class="task-preview-simple reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '200ms' }">
          <div class="preview-label">{{ isZh ? '任务内容' : 'Task Content' }}</div>
          <div class="preview-content">{{ truncateContent(task.content, 200) }}</div>
        </div>

        <!-- Stats Bar -->
        <div class="stats-bar reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '240ms' }" @mousemove="handleStatsMouseMove" @mouseleave="handleStatsMouseLeave">
          <div class="stats-glow" :style="statsGlowStyle"></div>
          <div class="stats-particles">
            <div class="stats-particle" v-for="n in 6" :key="n" :style="{ '--i': n }"></div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ submissions.length }}</div>
            <div class="stat-label">{{ isZh ? '已提交' : 'Submitted' }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ scoredCount }}</div>
            <div class="stat-label">{{ isZh ? '已评分' : 'Scored' }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ pendingCount }}</div>
            <div class="stat-label">{{ isZh ? '待评分' : 'Pending' }}</div>
          </div>
          <div class="stat-item" v-if="avgScore !== null">
            <div class="stat-value">{{ avgScore }}</div>
            <div class="stat-label">{{ isZh ? '平均分' : 'Avg Score' }}</div>
          </div>
        </div>

        <!-- Filter Tabs -->
        <div class="filter-tabs reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '280ms' }">
          <button class="filter-tab" :class="{ active: filter === 'all' }" @click="filter = 'all'">
            {{ isZh ? '全部' : 'All' }}
          </button>
          <button class="filter-tab" :class="{ active: filter === 'pending' }" @click="filter = 'pending'">
            {{ isZh ? '待评分' : 'Pending' }}
          </button>
          <button class="filter-tab" :class="{ active: filter === 'scored' }" @click="filter = 'scored'">
            {{ isZh ? '已评分' : 'Scored' }}
          </button>
        </div>

        <!-- Loading Submissions -->
        <div v-if="isLoadingSubmissions" class="loading-state reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '320ms' }">
          <div class="spinner"></div>
          <span>{{ isZh ? '加载提交列表...' : 'Loading submissions...' }}</span>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredSubmissions.length === 0" class="empty-state reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '320ms' }">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="12" y1="18" x2="12" y2="12"/>
              <line x1="9" y1="15" x2="15" y2="15"/>
            </svg>
          </div>
          <div class="empty-title">{{ isZh ? '暂无提交' : 'No Submissions' }}</div>
          <div class="empty-desc">{{ isZh ? '还没有用户提交此任务' : 'No users have submitted this task yet' }}</div>
        </div>

        <!-- Submissions List - Long Card Style -->
        <div v-else class="submissions-list reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '320ms' }">
          <div 
            v-for="(sub, index) in filteredSubmissions" 
            :key="sub.id" 
            class="submission-card-item"
            :class="{ 'is-scored': sub.score !== null }"
            :style="{ '--delay': `${index * 60}ms` }"
            @click="openScoreModal(sub)"
          >
            <div class="card-glow"></div>
            <div class="card-content">
              <div class="card-icon">
                <img v-if="getUserAvatar(sub)" :src="getUserAvatar(sub)" class="card-avatar-img" />
                <template v-else>
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </template>
              </div>
              <div class="card-main">
                <div class="card-top">
                  <span class="card-name">{{ sub.username || '—' }}</span>
                  <span class="card-badge" :class="{ scored: sub.score !== null }">
                    {{ sub.score !== null ? sub.score : (isZh ? '待评' : 'Pending') }}
                  </span>
                </div>
                <div class="card-bottom">
                  <span class="card-phone">{{ sub.phone || '—' }}</span>
                  <span class="card-time">
                    <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"/>
                      <polyline points="12 6 12 12 16 14"/>
                    </svg>
                    {{ formatTime(sub.updated_at || sub.created_at) }}
                  </span>
                </div>
              </div>
              <div class="card-arrow">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="m9 18 6-6-6-6"/>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Load More -->
        <div v-if="hasMore && !isLoadingSubmissions" class="load-more">
          <button class="btn ghost" @click="loadMore" :disabled="isLoadingMore">
            {{ isLoadingMore ? (isZh ? '加载中...' : 'Loading...') : (isZh ? '加载更多' : 'Load More') }}
          </button>
        </div>
      </template>
    </div>

    <!-- Bottom bar -->
    <div class="bottom-bar" v-if="task">
      <div class="bottom-inner">
        <div class="bottom-left">
          <div class="bottom-title">{{ isZh ? '提交管理' : 'Submissions' }}</div>
          <div class="bottom-sub">{{ scoredCount }}/{{ submissions.length }} {{ isZh ? '已评分' : 'scored' }}</div>
        </div>
        <div class="bottom-right">
          <button class="btn danger" @click="openDeleteModal" :disabled="isDeleting">
            {{ isZh ? '删除任务' : 'Delete' }}
          </button>
          <button class="btn ghost" @click="router.push({ name: 'task-list' })">
            {{ isZh ? '返回' : 'Back' }}
          </button>
          <button class="btn ghost" @click="loadSubmissions" :disabled="isLoadingSubmissions">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            {{ isZh ? '刷新' : 'Refresh' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Score Modal -->
    <Teleport to="body">
      <div v-if="selectedSubmission" class="modal-overlay" @click="closeModal">
        <div class="modal-container" @click.stop>
          <button class="modal-close" @click="closeModal">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>

          <!-- Modal Header -->
          <div class="modal-header">
            <div class="modal-avatar">
            <img v-if="getUserAvatar(selectedSubmission)" :src="getUserAvatar(selectedSubmission)" class="modal-avatar-img" />
            <span v-else>{{ getAvatarLetter(selectedSubmission) }}</span>
          </div>
            <div class="modal-user">
              <div class="modal-name">{{ selectedSubmission.username || '—' }}</div>
              <div class="modal-meta">
                <span>{{ selectedSubmission.phone || '—' }}</span>
                <span class="meta-divider">|</span>
                <span>{{ formatTime(selectedSubmission.updated_at || selectedSubmission.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Modal Body -->
          <div class="modal-body">
            <div v-if="selectedSubmission.text_content" class="modal-section">
              <div class="section-label">{{ isZh ? '完成情况' : 'Progress' }}</div>
              <div class="section-content">{{ selectedSubmission.text_content }}</div>
            </div>
            <div v-if="selectedSubmission.suggestion" class="modal-section">
              <div class="section-label">{{ isZh ? '建议反馈' : 'Suggestions' }}</div>
              <div class="section-content section-content--muted">{{ selectedSubmission.suggestion }}</div>
            </div>
            
            <!-- Images -->
            <div v-if="selectedSubmission.images && selectedSubmission.images.length > 0" class="modal-section">
              <div class="section-label">{{ isZh ? '附件图片' : 'Attachments' }} ({{ selectedSubmission.images.length }})</div>
              <div class="modal-images">
                <div 
                  v-for="img in selectedSubmission.images" 
                  :key="img.id" 
                  class="modal-image-thumb"
                  @click="previewImage(img)"
                >
                  <img :src="img.url || img.image_url" :alt="img.original_filename || img.filename" />
                </div>
              </div>
            </div>

            <!-- Empty content hint -->
            <div v-if="!selectedSubmission.text_content && !selectedSubmission.suggestion && (!selectedSubmission.images || selectedSubmission.images.length === 0)" class="empty-content">
              {{ isZh ? '该用户未填写任何内容' : 'No content submitted' }}
            </div>
          </div>

          <!-- Modal Footer - Score Input -->
          <div class="modal-footer">
            <div class="score-row">
              <label class="score-label">{{ isZh ? '评分' : 'Score' }}</label>
              <div class="score-input-group">
                <input
                  type="text"
                  inputmode="numeric"
                  class="score-input"
                  v-model="modalScore"
                  maxlength="3"
                  :placeholder="isZh ? '0-100' : '0-100'"
                  @keyup.enter="submitModalScore"
                />
                <span class="score-max">/ 100</span>
              </div>
            </div>
            <div class="modal-actions">
              <button class="btn ghost" @click="closeModal">{{ isZh ? '取消' : 'Cancel' }}</button>
              <button 
                class="btn primary" 
                :disabled="!isModalScoreValid || isScoring"
                @click="submitModalScore"
              >
                {{ isScoring ? '...' : (selectedSubmission.score !== null ? (isZh ? '更新评分' : 'Update') : (isZh ? '提交评分' : 'Submit')) }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Image Preview Modal -->
    <Teleport to="body">
      <div v-if="previewingImage" class="preview-overlay" @click="closePreview">
        <div class="preview-container" @click.stop>
          <img :src="previewingImage.url || previewingImage.image_url" :alt="previewingImage.original_filename || previewingImage.filename" />
          <button class="preview-close" @click="closePreview">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <WarningModal
      v-model="showDeleteModal"
      type="warning"
      :title="isZh ? '确认删除' : 'Confirm Delete'"
      :message="deleteModalMessage"
      :show-cancel="true"
      :confirm-text="isZh ? '确认删除' : 'Delete'"
      :cancel-text="isZh ? '取消' : 'Cancel'"
      @confirm="confirmDeleteTask"
    />
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'
import { useUserStore } from '@/stores/user'
import { useErrorStore } from '@/stores/error'
import { useSuccessStore } from '@/stores/success'
import { listTasks, listTaskSubmissions, scoreSubmission, deleteTask } from '@/services/taskService'
import WarningModal from '@/components/WarningModal.vue'

const router = useRouter()
const route = useRoute()
const i18n = useI18nStore()
const userStore = useUserStore()
const errorStore = useErrorStore()
const successStore = useSuccessStore()

const isZh = computed(() => i18n.locale === 'zh')
const pageEnter = ref(false)

// Task state
const task = ref(null)
const isLoadingTask = ref(true)

// Users map for avatar lookup
const avatarsMap = ref({})

// Submissions state
const submissions = ref([])
const isLoadingSubmissions = ref(false)
const isLoadingMore = ref(false)
const offset = ref(0)
const limit = 200
const hasMore = ref(true)
const filter = ref('all')

// Modal state
const selectedSubmission = ref(null)
const modalScore = ref('')
const isScoring = ref(false)

// Image preview
const previewingImage = ref(null)

// Delete task state
const showDeleteModal = ref(false)
const isDeleting = ref(false)

// Stats bar glow effect
const statsGlowX = ref(50)
const statsGlowY = ref(50)
const statsGlowOpacity = ref(0)

const statsGlowStyle = computed(() => ({
  '--glow-x': `${statsGlowX.value}%`,
  '--glow-y': `${statsGlowY.value}%`,
  '--glow-opacity': statsGlowOpacity.value
}))

function handleStatsMouseMove(e) {
  const rect = e.currentTarget.getBoundingClientRect()
  statsGlowX.value = ((e.clientX - rect.left) / rect.width) * 100
  statsGlowY.value = ((e.clientY - rect.top) / rect.height) * 100
  statsGlowOpacity.value = 1
}

function handleStatsMouseLeave() {
  statsGlowOpacity.value = 0
}

// Computed
const scoredCount = computed(() => submissions.value.filter(s => s.score !== null).length)
const pendingCount = computed(() => submissions.value.filter(s => s.score === null).length)
const avgScore = computed(() => {
  const scored = submissions.value.filter(s => s.score !== null)
  if (scored.length === 0) return null
  const sum = scored.reduce((acc, s) => acc + s.score, 0)
  return Math.round(sum / scored.length)
})

const filteredSubmissions = computed(() => {
  if (filter.value === 'all') return submissions.value
  if (filter.value === 'pending') return submissions.value.filter(s => s.score === null)
  if (filter.value === 'scored') return submissions.value.filter(s => s.score !== null)
  return submissions.value
})

const isModalScoreValid = computed(() => {
  const val = modalScore.value.trim()
  if (!val) return false
  const num = parseInt(val, 10)
  return !isNaN(num) && num >= 0 && num <= 100
})

// Helpers
function truncateContent(content, maxLen = 100) {
  if (!content) return isZh.value ? '无内容' : 'No content'
  return content.length > maxLen ? content.slice(0, maxLen) + '...' : content
}

function formatTime(dateStr) {
  if (!dateStr) return '—'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString(isZh.value ? 'zh-CN' : 'en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

function getAvatarLetter(sub) {
  const name = sub.username || 'U'
  return (name[0] || 'U').toUpperCase()
}

// Get user avatar by user_id
function getUserAvatar(sub) {
  return avatarsMap.value[sub.user_id] || ''
}

// Load user avatars (public API, no auth required)
async function loadAvatars() {
  try {
    const res = await fetch('/api/users/avatars?limit=500&offset=0')
    if (!res.ok) return
    const list = await res.json()
    const map = {}
    if (Array.isArray(list)) {
      list.forEach(item => {
        if (item.id && item.photo) map[item.id] = item.photo
      })
    }
    avatarsMap.value = map
  } catch {
    avatarsMap.value = {}
  }
}

// Modal functions
function openScoreModal(sub) {
  selectedSubmission.value = sub
  modalScore.value = sub.score !== null ? String(sub.score) : ''
  // Lock body scroll and preserve scrollbar space
  document.body.style.overflow = 'hidden'
  document.body.style.paddingRight = `${window.innerWidth - document.documentElement.clientWidth}px`
}

function closeModal() {
  selectedSubmission.value = null
  modalScore.value = ''
  // Restore body scroll
  document.body.style.overflow = ''
  document.body.style.paddingRight = ''
}

async function submitModalScore() {
  if (!isModalScoreValid.value || !selectedSubmission.value) return
  
  const score = parseInt(modalScore.value.trim(), 10)
  const taskId = route.params.taskId
  const subId = selectedSubmission.value.id

  isScoring.value = true
  try {
    const result = await scoreSubmission(taskId, subId, score)
    
    // Update local state
    const idx = submissions.value.findIndex(s => s.id === subId)
    if (idx !== -1) {
      submissions.value[idx].score = result.score
      submissions.value[idx].scored_at = result.scored_at
    }
    
    successStore.showSuccess(isZh.value ? '评分成功' : 'Score submitted')
    closeModal()
  } catch (err) {
    errorStore.showError(err?.message || (isZh.value ? '评分失败' : 'Score failed'))
  } finally {
    isScoring.value = false
  }
}

// Load task info
async function loadTask() {
  const taskId = route.params.taskId
  if (!taskId) return

  isLoadingTask.value = true
  try {
    const tasks = await listTasks({ limit: 200, offset: 0 })
    const taskList = Array.isArray(tasks) ? tasks : (tasks.items || tasks.tasks || [])
    task.value = taskList.find(t => String(t.id) === String(taskId)) || { id: taskId, title: '', content: '', recipient_count: 0 }
  } catch (err) {
    task.value = { id: taskId, title: '', content: '', recipient_count: 0 }
  } finally {
    isLoadingTask.value = false
  }
}

// Load submissions
async function loadSubmissions() {
  const taskId = route.params.taskId
  if (!taskId) return

  isLoadingSubmissions.value = true
  offset.value = 0
  try {
    const response = await listTaskSubmissions(taskId, { limit, offset: 0 })
    const list = Array.isArray(response) ? response : (response.items || response.submissions || [])
    submissions.value = list
    hasMore.value = list.length >= limit
  } catch (err) {
    errorStore.showError(isZh.value ? '加载提交列表失败' : 'Failed to load submissions')
    submissions.value = []
  } finally {
    isLoadingSubmissions.value = false
  }
}

// Load more
async function loadMore() {
  if (isLoadingMore.value || !hasMore.value) return
  
  const taskId = route.params.taskId
  isLoadingMore.value = true
  offset.value += limit
  try {
    const response = await listTaskSubmissions(taskId, { limit, offset: offset.value })
    const list = Array.isArray(response) ? response : (response.items || response.submissions || [])
    if (list.length < limit) hasMore.value = false
    submissions.value.push(...list)
  } catch (err) {
    offset.value -= limit
    errorStore.showError(isZh.value ? '加载更多失败' : 'Failed to load more')
  } finally {
    isLoadingMore.value = false
  }
}

// Preview image
function previewImage(img) {
  previewingImage.value = img
  // Lock body scroll and preserve scrollbar space
  document.body.style.overflow = 'hidden'
  document.body.style.paddingRight = `${window.innerWidth - document.documentElement.clientWidth}px`
}

function closePreview() {
  previewingImage.value = null
  // Restore body scroll
  document.body.style.overflow = ''
  document.body.style.paddingRight = ''
}

// Delete task modal message
const deleteModalMessage = computed(() => {
  const taskTitle = task.value?.title || (isZh.value ? '未命名任务' : 'Untitled Task')
  if (isZh.value) {
    return `确定要删除任务「${taskTitle}」吗？此操作将同时删除所有提交记录和图片，且无法恢复。`
  }
  return `Are you sure you want to delete task "${taskTitle}"? This will also delete all submissions and images, and cannot be undone.`
})

// Open delete confirmation modal
function openDeleteModal() {
  showDeleteModal.value = true
}

// Confirm delete task
async function confirmDeleteTask() {
  if (!task.value || isDeleting.value) return
  isDeleting.value = true
  try {
    await deleteTask(task.value.id)
    successStore.showSuccess(isZh.value ? '任务已删除' : 'Task deleted')
    router.push({ name: 'task-list' })
  } catch (err) {
    const status = err?.response?.status || err?.status
    if (status === 401) {
      errorStore.showError(isZh.value ? '未登录或登录已过期' : 'Not logged in or session expired')
    } else if (status === 403) {
      errorStore.showError(isZh.value ? '权限不足' : 'Permission denied')
    } else if (status === 404) {
      errorStore.showError(isZh.value ? '任务不存在' : 'Task not found')
      router.push({ name: 'task-list' })
    } else {
      errorStore.showError(isZh.value ? '删除任务失败' : 'Failed to delete task')
    }
  } finally {
    isDeleting.value = false
  }
}

// Check permission
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

onMounted(async () => {
  if (!userStore.isLoggedIn || !checkPermission()) {
    router.push('/user')
    return
  }
  
  // Load avatars first for avatar mapping
  await loadAvatars()
  await loadTask()
  await loadSubmissions()
  
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

/* Particle Background */
.particles-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.particle {
  position: absolute;
  width: 6px;
  height: 6px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.4) 0%, transparent 70%);
  border-radius: 50%;
  animation: float 20s infinite ease-in-out;
  animation-delay: calc(var(--i) * -1.5s);
}

.particle:nth-child(1) { left: 5%; top: 20%; width: 8px; height: 8px; }
.particle:nth-child(2) { left: 15%; top: 60%; }
.particle:nth-child(3) { left: 25%; top: 35%; width: 10px; height: 10px; }
.particle:nth-child(4) { left: 40%; top: 80%; }
.particle:nth-child(5) { left: 55%; top: 15%; width: 7px; height: 7px; }
.particle:nth-child(6) { left: 65%; top: 50%; }
.particle:nth-child(7) { left: 75%; top: 25%; width: 9px; height: 9px; }
.particle:nth-child(8) { left: 85%; top: 70%; }
.particle:nth-child(9) { left: 90%; top: 40%; width: 5px; height: 5px; }
.particle:nth-child(10) { left: 10%; top: 85%; }
.particle:nth-child(11) { left: 50%; top: 45%; width: 8px; height: 8px; }
.particle:nth-child(12) { left: 80%; top: 10%; }

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.3; }
  25% { transform: translate(20px, -30px) scale(1.2); opacity: 0.6; }
  50% { transform: translate(-10px, 20px) scale(0.8); opacity: 0.4; }
  75% { transform: translate(15px, 10px) scale(1.1); opacity: 0.5; }
}

/* Page layout */
.task-submissions-page {
  position: relative;
  min-height: 100vh;
  background: #fbfbfb;
  padding: 120px 24px 148px;
}

.page-container {
  position: relative;
  z-index: 1;
  max-width: 720px;
  margin: 0 auto;
}

.page-header { margin-bottom: 40px; }
.task-meta { margin-bottom: 12px; }

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0;
  background: transparent;
  border: none;
  font-size: 14px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.45);
  cursor: pointer;
  transition: color 0.2s ease;
}
.back-link:hover { color: #0b0f19; }

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

/* Task Preview - Simple (no card) */
.task-preview-simple {
  margin-bottom: 32px;
}

.preview-label {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.01em;
  text-transform: uppercase;
  color: rgba(0, 0, 0,);
  margin-bottom: 12px;
}

.preview-content {
  font-size: 16px;
  color: rgba(0, 0, 0, 0.75);
  line-height: 1.7;
}

/* Stats Bar */
.stats-bar {
  position: relative;
  display: flex;
  gap: 16px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  margin-bottom: 24px;
  overflow: hidden;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.stats-bar:hover {
  border-color: rgba(59, 130, 246, 0.3);
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.1);
}

/* Glow effect following mouse */
.stats-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle 150px at var(--glow-x, 50%) var(--glow-y, 50%),
    rgba(59, 130, 246, 0.15) 0%,
    transparent 70%
  );
  opacity: var(--glow-opacity, 0);
  transition: opacity 0.3s ease;
  pointer-events: none;
}

/* Floating particles */
.stats-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.stats-particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: rgba(59, 130, 246, 0.4);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stats-bar:hover .stats-particle {
  opacity: 1;
  animation: statsFloat 3s ease-in-out infinite;
  animation-delay: calc(var(--i) * 0.4s);
}

.stats-particle:nth-child(1) { left: 10%; top: 20%; }
.stats-particle:nth-child(2) { left: 25%; top: 70%; width: 3px; height: 3px; }
.stats-particle:nth-child(3) { left: 45%; top: 30%; width: 5px; height: 5px; }
.stats-particle:nth-child(4) { left: 65%; top: 60%; }
.stats-particle:nth-child(5) { left: 80%; top: 25%; width: 3px; height: 3px; }
.stats-particle:nth-child(6) { left: 90%; top: 70%; width: 5px; height: 5px; }

@keyframes statsFloat {
  0%, 100% { transform: translateY(0) scale(1); opacity: 0.4; }
  50% { transform: translateY(-8px) scale(1.2); opacity: 0.8; }
}

.stat-item { flex: 1; text-align: center; position: relative; z-index: 1; }
.stat-value { font-size: 28px; font-weight: 700; color: #0b0f19; transition: color 0.2s ease; }
.stat-label { font-size: 12px; color: rgba(0, 0, 0, 0.5); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }

.stats-bar:hover .stat-value { color: #1e40af; }

/* Filter Tabs */
.filter-tabs { display: flex; gap: 10px; margin-bottom: 24px; }

.filter-tab {
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
.filter-tab:hover { border-color: #000000; color: #000000; transform: scale(1.03); }
.filter-tab:active { transform: scale(0.97); }
.filter-tab.active { background: #0b0f19; border-color: #0b0f19; color: #fff; }

/* Loading & Empty States */
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  gap: 12px;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: #0b0f19;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty-icon { color: rgba(0, 0, 0, 0.2); }
.empty-title { font-size: 16px; font-weight: 600; color: #0b0f19; }
.empty-desc { font-size: 13px; color: rgba(0, 0, 0, 0.5); }

/* Submissions List - Long Card Style */
.submissions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.submission-card-item {
  position: relative;
  width: 100%;
  background: #ffffff;
  border: 1.5px solid rgba(0, 0, 0, 0.08);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  animation: slideIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) backwards;
  animation-delay: var(--delay, 0ms);
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.submission-card-item:hover {
  border-color: rgba(0, 0, 0, 0.15);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.submission-card-item:active {
  transform: scale(0.985) translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

.submission-card-item.is-scored {
  border-left: 3px solid #22c55e;
}

.submission-card-item:not(.is-scored) {
  border-left: 3px solid #3b82f6;
}

/* Card Glow Effect */
.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background: linear-gradient(90deg, transparent 0%, rgba(59, 130, 246, 0.03) 50%, transparent 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.submission-card-item:hover .card-glow {
  opacity: 1;
}

.card-content {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
}

.card-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f5f5f5 0%, #ebebeb 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: rgba(0, 0, 0, 0.45);
  transition: all 0.3s ease;
  overflow: hidden;
}

.card-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.submission-card-item:hover .card-icon {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #ffffff;
  transform: scale(1.05);
}

.submission-card-item.is-scored .card-icon {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: #ffffff;
}

.card-main {
  flex: 1;
  min-width: 0;
}

.card-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.card-name {
  font-size: 15px;
  font-weight: 600;
  color: #0b0f19;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-badge {
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.5);
  white-space: nowrap;
  flex-shrink: 0;
}

.card-badge.scored {
  background: rgba(34, 197, 94, 0.15);
  color: #16a34a;
}

.card-bottom {
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-phone {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.5);
}

.card-time {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: rgba(0, 0, 0, 0.45);
}

.card-time svg { opacity: 0.7; }

.card-arrow {
  color: rgba(0, 0, 0, 0.25);
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.submission-card-item:hover .card-arrow {
  color: rgba(0, 0, 0, 0.5);
  transform: translateX(4px);
}

/* Load More */
.load-more { display: flex; justify-content: center; padding: 24px 0; }

/* Bottom bar */
.bottom-bar {
  position: fixed;
  left: 0; right: 0; bottom: 0;
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

.bottom-left { min-width: 0; }
.bottom-title { font-size: 18px; font-weight: 700; letter-spacing: -0.01em; color: #000000; }
.bottom-sub { margin-top: 4px; font-size: 14px; color: rgba(0, 0, 0, 0.7); }
.bottom-right { display: inline-flex; gap: 12px; }

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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.btn:hover:not(:disabled) { background: rgba(0, 0, 0, 0.06); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.btn:active:not(:disabled) { background: #000000; color: #ffffff; transform: scale(0.97); }
.btn.primary:active:not(:disabled) { background: #ffffff; color: #000000; transform: scale(0.97); }
.btn:disabled { opacity: 0.55; cursor: not-allowed; }
.btn.primary { background: #000000; border-color: #000000; color: #ffffff; }
.btn.primary:hover:not(:disabled) { background: #1a1a1a; box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2); }
.btn.ghost { border-color: rgba(0, 0, 0, 0.2); }
.btn.danger { background: transparent; border-color: #ef4444; color: #ef4444; }
.btn.danger:hover:not(:disabled) { background: #ef4444; color: #ffffff; box-shadow: 0 6px 16px rgba(239, 68, 68, 0.25); }

/* Modal */
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

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-container {
  position: relative;
  width: 100%;
  max-width: 520px;
  max-height: 85vh;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  color: rgba(0, 0, 0, 0.5);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 1;
}
.modal-close:hover { background: rgba(0, 0, 0, 0.1); color: #0b0f19; }

.modal-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 24px 24px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.modal-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  flex-shrink: 0;
  overflow: hidden;
}

.modal-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.modal-user { flex: 1; min-width: 0; }
.modal-name { font-size: 17px; font-weight: 600; color: #0b0f19; }
.modal-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(0, 0, 0, 0.5);
  margin-top: 4px;
}
.meta-divider {
  color: rgba(0, 0, 0, 0.2);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.modal-section { margin-bottom: 20px; }
.modal-section:last-child { margin-bottom: 0; }

.section-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: rgba(0, 0, 0, 0.4);
  margin-bottom: 8px;
}

.section-content {
  font-size: 14px;
  color: #0b0f19;
  line-height: 1.6;
  white-space: pre-wrap;
}
.section-content--muted { color: rgba(0, 0, 0, 0.65); font-style: italic; }

.modal-images { display: flex; flex-wrap: wrap; gap: 8px; }

.modal-image-thumb {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease;
}
.modal-image-thumb:hover { transform: scale(1.05); }
.modal-image-thumb img { width: 100%; height: 100%; object-fit: cover; }

.empty-content {
  text-align: center;
  padding: 32px 16px;
  color: rgba(0, 0, 0, 0.4);
  font-size: 14px;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(0, 0, 0, 0.02);
  border-radius: 0 0 20px 20px;
}

.score-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.score-label {
  font-size: 14px;
  font-weight: 600;
  color: #0b0f19;
}

.score-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.score-input {
  flex: 1;
  max-width: 120px;
  height: 44px;
  padding: 0 16px;
  border: 1.5px solid rgba(0, 0, 0, 0.15);
  border-radius: 10px;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  background: #fff;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.score-input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.score-input::placeholder { color: rgba(0, 0, 0, 0.3); font-weight: 400; }

.score-max { font-size: 14px; color: rgba(0, 0, 0, 0.4); }

.modal-actions { display: flex; justify-content: flex-end; gap: 12px; }
.modal-actions .btn { height: 40px; padding: 0 24px; }

/* Image Preview Modal */
.preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.preview-container {
  position: relative;
  max-width: min(85vw, 900px);
  max-height: 75vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-container img {
  max-width: 100%;
  max-height: 70vh;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 8px;
}

.preview-close {
  position: absolute;
  top: -48px;
  right: 0;
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.preview-close:hover { background: rgba(255, 255, 255, 0.2); }
</style>
