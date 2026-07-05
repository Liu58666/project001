<template>
  <section class="my-tasks-page">
    <div class="page-container">
      <header class="page-header">
        <h1 class="page-title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }">
          {{ isZh ? '我的任务' : 'My Tasks' }}
        </h1>
        <p class="page-subtitle reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '140ms' }">
          {{ isZh ? '查看分配给我的任务并提交完成情况' : 'View assigned tasks and submit your progress' }}
        </p>
      </header>

      <!-- Filter Tabs -->
      <div class="filter-tabs reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '200ms' }">
        <button 
          class="filter-tab" 
          :class="{ active: filter === 'all' }"
          @click="filter = 'all'"
        >
          {{ isZh ? '全部' : 'All' }}
          <span class="tab-count">{{ tasks.length }}</span>
        </button>
        <button 
          class="filter-tab" 
          :class="{ active: filter === 'pending' }"
          @click="filter = 'pending'"
        >
          {{ isZh ? '待完成' : 'Pending' }}
          <span class="tab-count">{{ pendingCount }}</span>
        </button>
        <button 
          class="filter-tab" 
          :class="{ active: filter === 'submitted' }"
          @click="filter = 'submitted'"
        >
          {{ isZh ? '已提交' : 'Submitted' }}
          <span class="tab-count">{{ submittedCount }}</span>
        </button>
        <button 
          class="filter-tab" 
          :class="{ active: filter === 'scored' }"
          @click="filter = 'scored'"
        >
          {{ isZh ? '已评分' : 'Scored' }}
          <span class="tab-count">{{ scoredCount }}</span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading && tasks.length === 0" class="loading-state reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '260ms' }">
        <div class="spinner"></div>
        <span>{{ isZh ? '加载中...' : 'Loading...' }}</span>
      </div>

      <!-- Empty State -->
      <div v-else-if="!isLoading && filteredTasks.length === 0" class="empty-state reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '260ms' }">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="currentColor" stroke-width="1.2">
            <path d="M9 11l3 3L22 4"/>
            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
          </svg>
        </div>
        <div class="empty-title">{{ isZh ? '暂无任务' : 'No Tasks' }}</div>
        <div class="empty-desc">{{ isZh ? '当前没有分配给你的任务' : 'No tasks assigned to you yet' }}</div>
      </div>

      <!-- Task List -->
      <div v-else class="task-list reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '260ms' }">
        <div 
          v-for="(task, index) in filteredTasks" 
          :key="task.id" 
          class="task-card"
          :class="{ 
            'task-card--pending': !task.my_submission,
            'task-card--submitted': task.my_submission && task.my_submission.score === null,
            'task-card--scored': task.my_submission && task.my_submission.score !== null
          }"
          :style="{ '--delay': `${index * 60}ms` }"
          @click="openTaskDetail(task)"
        >
          <div class="task-card-content">
            <div class="task-status-indicator">
              <!-- Pending -->
              <div v-if="!task.my_submission" class="status-icon status-icon--pending">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <!-- Submitted but not scored -->
              <div v-else-if="task.my_submission.score === null" class="status-icon status-icon--submitted">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
              </div>
              <!-- Scored -->
              <div v-else class="status-icon status-icon--scored">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              </div>
            </div>
            <div class="task-main">
              <div class="task-top">
                <span class="task-title">{{ task.title || (isZh ? '未命名任务' : 'Untitled Task') }}</span>
                <span v-if="task.my_submission && task.my_submission.score !== null" class="task-badge task-badge--scored">
                  {{ isZh ? '已评分' : 'Scored' }}
                </span>
                <span v-else-if="task.my_submission" class="task-badge task-badge--submitted">
                  {{ isZh ? '已提交' : 'Submitted' }}
                </span>
                <span v-else class="task-badge task-badge--pending">
                  {{ isZh ? '待完成' : 'Pending' }}
                </span>
              </div>
              <div class="task-content-preview">{{ truncateContent(task.content) }}</div>
              <div class="task-bottom">
                <span class="task-time">
                  <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  {{ formatTime(task.published_at || task.created_at) }}
                </span>
                <span v-if="task.my_submission" class="task-submission-time">
                  <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 11l3 3L22 4"/>
                  </svg>
                  {{ isZh ? '提交于' : 'Submitted' }} {{ formatTime(task.my_submission.updated_at || task.my_submission.created_at) }}
                </span>
              </div>
            </div>
            <div class="task-arrow">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m9 18 6-6-6-6"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- Load More -->
        <div v-if="hasMore" class="load-more">
          <button class="btn ghost" @click="loadMore" :disabled="isLoadingMore">
            {{ isLoadingMore ? (isZh ? '加载中...' : 'Loading...') : (isZh ? '加载更多' : 'Load More') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Bottom bar -->
    <div class="bottom-bar">
      <div class="bottom-inner">
        <div class="bottom-left">
          <div class="bottom-title">{{ isZh ? '我的任务' : 'My Tasks' }}</div>
          <div class="bottom-sub">
            {{ pendingCount }} {{ isZh ? '待完成' : 'pending' }} · {{ submittedCount }} {{ isZh ? '已提交' : 'submitted' }}
          </div>
        </div>
        <div class="bottom-right">
          <button class="btn ghost" type="button" @click="loadTasks" :disabled="isLoading">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            {{ isZh ? '刷新' : 'Refresh' }}
          </button>
          <button class="btn ghost" type="button" @click="router.push('/user')">
            {{ isZh ? '返回' : 'Back' }}
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
import { getMyTasks } from '@/services/taskService'

const router = useRouter()
const i18n = useI18nStore()
const userStore = useUserStore()
const errorStore = useErrorStore()

const isZh = computed(() => i18n.locale === 'zh')
const pageEnter = ref(false)

// Task list state
const tasks = ref([])
const isLoading = ref(false)
const isLoadingMore = ref(false)
const offset = ref(0)
const limit = 50
const hasMore = ref(true)
const filter = ref('all')

// Computed counts
const pendingCount = computed(() => tasks.value.filter(t => !t.my_submission).length)
const submittedCount = computed(() => tasks.value.filter(t => t.my_submission && t.my_submission.score === null).length)
const scoredCount = computed(() => tasks.value.filter(t => t.my_submission && t.my_submission.score !== null).length)

// Filtered tasks
const filteredTasks = computed(() => {
  if (filter.value === 'all') return tasks.value
  if (filter.value === 'pending') return tasks.value.filter(t => !t.my_submission)
  if (filter.value === 'submitted') return tasks.value.filter(t => t.my_submission && t.my_submission.score === null)
  if (filter.value === 'scored') return tasks.value.filter(t => t.my_submission && t.my_submission.score !== null)
  return tasks.value
})

// Truncate content for preview
function truncateContent(content) {
  if (!content) return isZh.value ? '无内容' : 'No content'
  return content.length > 80 ? content.slice(0, 80) + '...' : content
}

// Format time
function formatTime(dateStr) {
  if (!dateStr) return '—'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString(isZh.value ? 'zh-CN' : 'en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

// Load tasks
async function loadTasks() {
  isLoading.value = true
  offset.value = 0
  try {
    const response = await getMyTasks({ limit, offset: 0 })
    if (Array.isArray(response)) {
      tasks.value = response
      hasMore.value = response.length >= limit
    } else {
      tasks.value = response.items || response.tasks || response.data || []
      hasMore.value = tasks.value.length >= limit
    }
  } catch (err) {
    errorStore.showError(isZh.value ? '加载任务失败' : 'Failed to load tasks')
    tasks.value = []
  } finally {
    isLoading.value = false
  }
}

// Load more tasks
async function loadMore() {
  if (isLoadingMore.value || !hasMore.value) return
  isLoadingMore.value = true
  offset.value += limit
  try {
    const response = await getMyTasks({ limit, offset: offset.value })
    const newTasks = Array.isArray(response) 
      ? response 
      : (response.items || response.tasks || response.data || [])
    
    if (newTasks.length < limit) {
      hasMore.value = false
    }
    tasks.value.push(...newTasks)
  } catch (err) {
    errorStore.showError(isZh.value ? '加载更多失败' : 'Failed to load more')
    offset.value -= limit
  } finally {
    isLoadingMore.value = false
  }
}

// Open task detail
function openTaskDetail(task) {
  router.push({ name: 'task-detail', params: { taskId: task.id } })
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  
  requestAnimationFrame(() => {
    pageEnter.value = true
  })
  
  loadTasks()
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
.my-tasks-page {
  min-height: 100vh;
  background: #fbfbfb;
  padding: 120px 24px 148px;
}

.page-container {
  max-width: 720px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
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

/* Filter Tabs */
.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.filter-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: 1.5px solid rgba(0, 0, 0, 0.1);
  border-radius: 999px;
  background: #fff;
  font-size: 14px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tab:hover {
  border-color: rgba(0, 0, 0, 0.2);
  color: #0b0f19;
}

.filter-tab.active {
  background: #0b0f19;
  border-color: #0b0f19;
  color: #fff;
}

.tab-count {
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.08);
  border-radius: 999px;
  font-size: 12px;
}

.filter-tab.active .tab-count {
  background: rgba(255, 255, 255, 0.2);
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  color: rgba(0, 0, 0, 0.5);
  gap: 16px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: #0b0f19;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  text-align: center;
}

.empty-icon {
  color: rgba(0, 0, 0, 0.2);
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #0b0f19;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.5);
}

/* Task List */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-card {
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
  box-sizing: border-box;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.task-card:hover {
  border-color: rgba(0, 0, 0, 0.15);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.task-card:active {
  transform: scale(0.985) translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

.task-card-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 18px 20px;
}

/* Status Indicator */
.task-status-indicator {
  display: flex;
  align-items: center;
  height: 24px; /* Match task-title line height (15px font + padding) */
  flex-shrink: 0;
}

.status-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-icon--pending {
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
}

.status-icon--submitted {
  background: rgba(59, 130, 246, 0.12);
  color: #2563eb;
}

.status-icon--scored {
  background: rgba(16, 185, 129, 0.12);
  color: #059669;
}

.task-main {
  flex: 1;
  min-width: 0;
}

.task-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.task-title {
  font-size: 15px;
  font-weight: 600;
  color: #0b0f19;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.task-score {
  padding: 4px 12px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.task-badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.task-badge--pending {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.task-badge--submitted {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.task-badge--scored {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.task-content-preview {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.55);
  line-height: 1.5;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-bottom {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.4);
  flex-wrap: wrap;
}

.task-time,
.task-submission-time {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.task-submission-time {
  color: #2563eb;
}

.task-arrow {
  color: rgba(0, 0, 0, 0.25);
  transition: all 0.2s ease;
  flex-shrink: 0;
  align-self: center;
}

.task-card:hover .task-arrow {
  color: rgba(0, 0, 0, 0.5);
  transform: translateX(4px);
}

/* Load More */
.load-more {
  display: flex;
  justify-content: center;
  padding: 24px 0;
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
}

.bottom-right {
  display: inline-flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  padding: 0 20px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  border: 1.5px solid #000000;
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

.btn.ghost {
  border-color: rgba(0, 0, 0, 0.2);
}
</style>
