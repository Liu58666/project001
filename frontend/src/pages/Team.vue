<template>
  <section class="team-page">
    <div class="team-container">
      <!-- 页面标题 - 靠左 -->
      <header class="team-header">
        <h1 class="team-title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }">
          {{ isZh ? '团队' : 'Team' }}
        </h1>
        <p class="team-subtitle reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '140ms' }">
          {{ isZh ? '认识我们的核心团队成员，了解公司组织架构' : 'Meet our core team members and learn about our organization' }}
        </p>
      </header>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <span>{{ isZh ? '加载中...' : 'Loading...' }}</span>
      </div>

      <!-- 团队内容 -->
      <div v-else class="team-content">
        <!-- 创始人 / 联合创始人 (role 4) -->
        <section class="team-section reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '200ms' }">
          <div class="section-header">
            <h2 class="section-title">{{ isZh ? '创始人 & 联合创始人' : 'Founders' }}</h2>
            <div class="section-line"></div>
          </div>
          <div v-if="founders.length" class="members-row">
            <div v-for="member in founders" :key="member.user_id" class="member-card member-card--founder" :class="{ 'member-card--private': member.private_hidden }" @click="viewProfile(member)">
              <div class="member-avatar" :class="{ 'avatar-loading': !isAvatarLoaded(member) }">
                <img 
                  v-if="getResumeAvatar(member)" 
                  :src="getResumeAvatar(member)" 
                  :alt="member.real_name"
                  loading="lazy"
                  @load="onAvatarLoad(getResumeAvatar(member))"
                />
                <div v-else class="avatar-letter">{{ getInitial(member.real_name) }}</div>
                <div class="avatar-skeleton"></div>
              </div>
              <div class="member-info">
                <h3 class="member-name">{{ member.real_name || (isZh ? '未设置' : 'Not set') }}</h3>
                <p class="member-title">{{ member.job_title || (isZh ? '创始人' : 'Founder') }}</p>
                <p v-if="member.department" class="member-dept">{{ member.department }}</p>
              </div>
              <div v-if="member.private_hidden" class="member-private-icon" :title="isZh ? '简历未公开' : 'Private'">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" stroke-width="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
            </div>
          </div>
          <div v-else class="empty-hint">{{ isZh ? '暂无成员' : 'No members yet' }}</div>
        </section>

        <!-- 部门主管 (role 3) -->
        <section class="team-section reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '300ms' }">
          <div class="section-header">
            <h2 class="section-title">{{ isZh ? '部门主管' : 'Department Heads' }}</h2>
            <div class="section-line"></div>
          </div>
          <div v-if="managers.length" class="members-row">
            <!-- <div v-for="member in managers" :key="member.user_id" class="member-card member-card--manager" :class="{ 'member-card--private': member.private_hidden }" @click="viewProfile(member)">
              <div class="member-avatar" :class="{ 'avatar-loading': !isAvatarLoaded(member) }">
                <img 
                  v-if="getResumeAvatar(member)" 
                  :src="getResumeAvatar(member)" 
                  :alt="member.real_name"
                  loading="lazy"
                  @load="onAvatarLoad(getResumeAvatar(member))"
                />
                <div v-else class="avatar-letter">{{ getInitial(member.real_name) }}</div>
                <div class="avatar-skeleton"></div>
              </div>
              <div class="member-info">
                <h3 class="member-name">{{ member.real_name || (isZh ? '未设置' : 'Not set') }}</h3>
                <p class="member-title">{{ member.job_title || (isZh ? '主管' : 'Manager') }}</p>
                <p v-if="member.department" class="member-dept">{{ member.department }}</p>
              </div>
              <div v-if="member.private_hidden" class="member-private-icon" :title="isZh ? '简历未公开' : 'Private'">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" stroke-width="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
            </div> -->
          </div>
          <div v-else class="empty-hint">{{ isZh ? '暂无成员' : 'No members yet' }}</div>
        </section>

        <!-- 部门经理 & 职员 (role 2, 1) -->
        <section class="team-section reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '400ms' }">
          <div class="section-header">
            <h2 class="section-title">{{ isZh ? '团队成员' : 'Team Members' }}</h2>
            <div class="section-line"></div>
          </div>
          <div v-if="staff.length" class="members-row">
            <div v-for="member in staff" :key="member.user_id" class="member-card member-card--staff member-card--compact" :class="{ 'member-card--private': member.private_hidden }" @click="viewProfile(member)">
              <div class="member-avatar member-avatar--small" :class="{ 'avatar-loading': !isAvatarLoaded(member) }">
                <img 
                  v-if="getResumeAvatar(member)" 
                  :src="getResumeAvatar(member)" 
                  :alt="member.real_name"
                  loading="lazy"
                  @load="onAvatarLoad(getResumeAvatar(member))"
                />
                <div v-else class="avatar-letter">{{ getInitial(member.real_name) }}</div>
                <div class="avatar-skeleton"></div>
              </div>
              <div class="member-info">
                <h3 class="member-name">{{ member.real_name || (isZh ? '未设置' : 'Not set') }}</h3>
                <p class="member-title">{{ member.job_title || (isZh ? '成员' : 'Member') }}</p>
                <p v-if="member.department" class="member-dept">{{ member.department }}</p>
              </div>
              <div v-if="member.private_hidden" class="member-private-icon" :title="isZh ? '简历未公开' : 'Private'">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" stroke-width="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
            </div>
          </div>
          <div v-else class="empty-hint">{{ isZh ? '暂无成员' : 'No members yet' }}</div>
        </section>
      </div>
    </div>

    <!-- 未公开简历的简要信息弹窗 -->
    <div v-if="selectedMember" class="modal-layer" @click.self="selectedMember = null">
      <div class="modal profile-modal">
        <button class="modal-close" @click="selectedMember = null">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6 6 18M6 6l12 12"/>
          </svg>
        </button>
        <div class="profile-header">
          <div class="profile-avatar">
            <img v-if="getResumeAvatar(selectedMember)" :src="getResumeAvatar(selectedMember)" :alt="selectedMember.real_name" />
            <div v-else class="avatar-letter avatar-letter--large">{{ getInitial(selectedMember.real_name) }}</div>
          </div>
          <h2 class="profile-name">{{ selectedMember.real_name || (isZh ? '未设置' : 'Not set') }}</h2>
          <p class="profile-title">{{ selectedMember.job_title }}</p>
          <p v-if="selectedMember.department" class="profile-dept">{{ selectedMember.department }}</p>
        </div>
        <div class="profile-body">
          <div v-if="selectedMember.email" class="profile-field">
            <span class="field-label">{{ isZh ? '邮箱' : 'Email' }}</span>
            <span class="field-value">{{ selectedMember.email }}</span>
          </div>
        </div>
        <div class="profile-private">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" stroke-width="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <p>{{ isZh ? '该成员的详细简历未公开' : "This member's detailed resume is private" }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'
import { useErrorStore } from '@/stores/error'
import { listAllResumes } from '@/services/resumeService'
import { preloadImagesInBackground } from '@/utils/imagePreloader'

const router = useRouter()
const i18n = useI18nStore()
const errorStore = useErrorStore()

const isZh = computed(() => i18n.locale === 'zh')
const pageEnter = ref(false)
const isLoading = ref(true)
const members = ref([])
const selectedMember = ref(null)
const loadedAvatars = ref(new Set()) // 跟踪已加载的头像

// 按角色分组
const founders = computed(() => members.value.filter(m => m.role === 4))
const managers = computed(() => members.value.filter(m => m.role === 3))
const staff = computed(() => members.value.filter(m => m.role === 2))

function getInitial(name) {
  const s = String(name || '').trim() || 'U'
  return s[0].toUpperCase()
}

// 获取简历头像（优先使用 avatar_url）
function getResumeAvatar(member) {
  return member.avatar_url || member.avatarUrl || member.avatar || ''
}

// 标记头像已加载
function onAvatarLoad(url) {
  if (url) loadedAvatars.value.add(url)
}

// 检查头像是否已加载
function isAvatarLoaded(member) {
  const url = getResumeAvatar(member)
  return !url || loadedAvatars.value.has(url)
}

// 点击卡片：如果简历公开则跳转，否则弹出简要信息卡片
function viewProfile(member) {
  if (!member.user_id) return
  
  // 如果 private_hidden=true，说明简历未公开，显示弹窗
  if (member.private_hidden) {
    selectedMember.value = member
    return
  }
  
  router.push(`/user/resume/${member.user_id}`)
}

async function loadTeam() {
  isLoading.value = true
  try {
    const data = await listAllResumes({ limit: 200, offset: 0 })
    const list = Array.isArray(data) ? data : []
    // 只显示 role > 0 的成员，并按 role 从高到低排序
    const filtered = list.filter(m => (m.role || 0) > 0)
    filtered.sort((a, b) => (b.role || 0) - (a.role || 0))
    members.value = filtered
    
    // 数据加载完成后，立即在后台预加载所有头像
    const avatarUrls = filtered
      .map(m => m.avatar_url || m.avatarUrl || m.avatar)
      .filter(Boolean)
    preloadImagesInBackground(avatarUrls)
  } catch (e) {
    errorStore.showError(isZh.value ? `加载失败：${e?.message || e}` : `Load failed: ${e?.message || e}`)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  setTimeout(() => { pageEnter.value = true }, 100)
  loadTeam()
})
</script>

<style scoped>
.team-page {
  background: #fbfbfb;
  padding: 120px 24px 72px;
  min-height: 100vh;
}

.team-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* 标题 - 靠左对齐 */
.team-header {
  margin-bottom: 48px;
}

.team-title {
  font-size: 72px;
  line-height: 1.02;
  letter-spacing: -0.04em;
  font-weight: 500;
  color: #0b0f19;
  margin: 0 0 10px;
}

.team-subtitle {
  margin: 0;
  max-width: 760px;
  font-size: 15px;
  line-height: 1.7;
  color: rgba(17, 24, 39, 0.62);
}

/* 动画 */
.reveal {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--d, 0ms);
}

.reveal.is-in {
  opacity: 1;
  transform: translateY(0);
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 80px 0;
  color: #64748b;
}

.loading-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #e2e8f0;
  border-top-color: #0f172a;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 团队内容 */
.team-content {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

/* 分区 */
.team-section {
  padding: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 28px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #0b0f19;
  margin: 0;
  white-space: nowrap;
  letter-spacing: 0.02em;
}

.section-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, #d1d5db 0%, transparent 100%);
}

/* 成员行 - 横向排列，每个卡片占 1/3 */
.members-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

/* 成员卡片 - 占 1/3 宽度 */
.member-card {
  width: calc(33.333% - 14px);
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  border: 2px solid #e5e7eb;
  cursor: pointer;
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), 
              box-shadow 0.2s ease,
              border-color 0.2s ease,
              background 0.2s ease;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

.member-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.1);
}

.member-card:active {
  transform: translateY(0) scale(0.98);
  transition: transform 0.1s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
}

/* 创始人 - 深红色边框 */
.member-card--founder {
  border-color: #991b1b;
  background: linear-gradient(135deg, #fef2f2 0%, #fff 100%);
}

.member-card--founder:hover {
  border-color: #7f1d1d;
  box-shadow: 0 12px 28px rgba(153, 27, 27, 0.15);
}

.member-card--founder:active {
  box-shadow: 0 2px 8px rgba(153, 27, 27, 0.1);
}

/* 主管 - 金色边框 */
.member-card--manager {
  border-color: #b45309;
  background: linear-gradient(135deg, #fffbeb 0%, #fff 100%);
}

.member-card--manager:hover {
  border-color: #92400e;
  box-shadow: 0 12px 28px rgba(180, 83, 9, 0.15);
}

.member-card--manager:active {
  box-shadow: 0 2px 8px rgba(180, 83, 9, 0.1);
}

/* 职员 - 蓝色边框 */
.member-card--staff {
  border-color: #1d4ed8;
  background: linear-gradient(135deg, #eff6ff 0%, #fff 100%);
}

.member-card--staff:hover {
  border-color: #1e40af;
  box-shadow: 0 12px 28px rgba(29, 78, 216, 0.15);
}

.member-card--staff:active {
  box-shadow: 0 2px 8px rgba(29, 78, 216, 0.1);
}

.member-card--compact {
  padding: 16px;
}

/* 头像 */
.member-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background: #f3f4f6;
  display: grid;
  place-items: center;
  position: relative;
}

.member-avatar--small {
  width: 48px;
  height: 48px;
}

.member-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 1;
  transition: opacity 0.3s ease;
}

.member-avatar.avatar-loading img {
  opacity: 0;
}

/* 头像骨架屏 */
.avatar-skeleton {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.member-avatar.avatar-loading .avatar-skeleton {
  opacity: 1;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.avatar-letter {
  font-size: 24px;
  font-weight: 700;
  color: #9ca3af;
}

.member-avatar--small .avatar-letter {
  font-size: 18px;
}

.avatar-letter--large {
  font-size: 40px;
}

/* 成员信息 */
.member-info {
  flex: 1;
  min-width: 0;
}

.member-name {
  font-size: 15px;
  font-weight: 600;
  color: #0b0f19;
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.member-title {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.member-dept {
  font-size: 12px;
  color: #9ca3af;
  margin: 4px 0 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 空提示 */
.empty-hint {
  color: #9ca3af;
  font-size: 14px;
  padding: 12px 0;
}

/* 私密卡片样式 */
.member-card--private {
  opacity: 0.85;
}

.member-private-icon {
  flex-shrink: 0;
  color: #9ca3af;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 弹窗 */
.modal-layer {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: grid;
  place-items: center;
  padding: 24px;
}

.modal {
  position: relative;
  background: #fff;
  border-radius: 20px;
  max-width: 420px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.18);
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  border: none;
  background: #f3f4f6;
  border-radius: 50%;
  cursor: pointer;
  display: grid;
  place-items: center;
  color: #6b7280;
  transition: all 0.15s ease;
}

.modal-close:hover {
  background: #e5e7eb;
  color: #0b0f19;
}

.profile-modal {
  padding: 40px 28px 28px;
}

.profile-header {
  text-align: center;
  margin-bottom: 20px;
}

.profile-avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto 16px;
  background: #f3f4f6;
  display: grid;
  place-items: center;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-name {
  font-size: 20px;
  font-weight: 600;
  color: #0b0f19;
  margin: 0 0 6px;
}

.profile-title {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.profile-dept {
  font-size: 13px;
  color: #9ca3af;
  margin: 4px 0 0;
}

.profile-body {
  border-top: 1px solid #e5e7eb;
  padding-top: 16px;
}

.profile-field {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
}

.field-label {
  font-size: 13px;
  color: #6b7280;
}

.field-value {
  font-size: 13px;
  color: #0b0f19;
  font-weight: 500;
}

.profile-private {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
  padding: 20px;
  margin-top: 8px;
  background: #f9fafb;
  border-radius: 12px;
  color: #9ca3af;
}

.profile-private p {
  margin: 0;
  font-size: 13px;
}
</style>
