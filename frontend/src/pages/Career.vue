<template>
  <section class="career-page">
    <div class="career-container">
      <!-- 页面标题 -->
      <header class="career-header">
        <h1 class="career-title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }">
          {{ isZh ? '加入我们' : 'Join Us' }}
        </h1>
        <p class="career-subtitle reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '140ms' }">
          {{ isZh ? '选择适合你的方式，开启与 DAIL 的旅程' : 'Choose your path and start your journey with DAIL' }}
        </p>
      </header>

      <!-- 底部提示 -->
      <div class="career-footer reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '200ms' }">
        <p>
          {{ isZh ? '不确定哪个适合你？' : 'Not sure which is right for you?' }}
          <a href="mailto:hr@dail.com" class="contact-link">{{ isZh ? '联系我们聊聊' : "Let's talk" }}</a>
        </p>
      </div>

      <!-- 选项卡片 -->
      <div class="career-options">
        <!-- 实习生选项 -->
        <div 
          class="career-card reveal" 
          :class="{ 'is-in': pageEnter, 'entered': cardsEntered }" 
          :style="{ '--d': '320ms' }"
          @click="handleIntern"
        >
          <div class="card-icon card-icon--intern">
            <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
              <path d="M6 12v5c3 3 9 3 12 0v-5"/>
            </svg>
          </div>
          <div class="card-content">
            <h2 class="card-title">{{ isZh ? '我想当实习生' : 'I Want to Intern' }}</h2>
            <p class="card-desc">
              {{ isZh 
                ? '适合在校学生或应届毕业生，在实践中学习成长，积累宝贵经验。' 
                : 'Perfect for students or fresh graduates. Learn and grow through hands-on experience.' 
              }}
            </p>
            <ul class="card-features">
              <li>{{ isZh ? '灵活的工作时间' : 'Flexible working hours' }}</li>
              <li>{{ isZh ? '导师一对一指导' : 'One-on-one mentorship' }}</li>
              <li>{{ isZh ? '参与真实项目' : 'Real project involvement' }}</li>
            </ul>
          </div>
          <div class="card-arrow">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14"/>
              <path d="m12 5 7 7-7 7"/>
            </svg>
          </div>
        </div>

        <!-- 正式入职选项 -->
        <div 
          class="career-card reveal" 
          :class="{ 'is-in': pageEnter, 'entered': cardsEntered }" 
          :style="{ '--d': '450ms' }"
          @click="handleFullTime"
        >
          <div class="card-icon card-icon--fulltime">
            <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>
              <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>
              <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/>
              <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>
            </svg>
          </div>
          <div class="card-content">
            <h2 class="card-title">{{ isZh ? '我想入职 DAIL' : 'I Want to Join DAIL' }}</h2>
            <p class="card-desc">
              {{ isZh 
                ? '成为正式团队成员，与优秀的伙伴一起创造价值，共同成长。' 
                : 'Become a full team member. Create value and grow together with excellent partners.' 
              }}
            </p>
            <ul class="card-features">
              <li>{{ isZh ? '有竞争力的薪酬' : 'Competitive compensation' }}</li>
              <li>{{ isZh ? '完善的福利体系' : 'Comprehensive benefits' }}</li>
              <li>{{ isZh ? '主导百万级项目' : 'Lead million-level projects' }}</li>
            </ul>
          </div>
          <div class="card-arrow">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14"/>
              <path d="m12 5 7 7-7 7"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- 警示弹窗 -->
      <WarningModal
        v-model="showWarningModal"
        type="warning"
        :title="isZh ? '无法申请' : 'Cannot Apply'"
        :message="warningMessage"
      />
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'
import { useUserStore } from '@/stores/user'
import WarningModal from '@/components/WarningModal.vue'

const router = useRouter()
const i18n = useI18nStore()
const userStore = useUserStore()

const isZh = computed(() => i18n.locale === 'zh')
const pageEnter = ref(false)
const cardsEntered = ref(false)
const userRole = ref(-1)
const showWarningModal = ref(false)
const warningMessage = ref('')

// 检查用户权限
function getUserRole() {
  try {
    const token = userStore.accessToken
    if (!token) return -1
    const [, payload] = String(token).split('.')
    if (!payload) return -1
    const json = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    return typeof json?.role === 'number' ? json.role : -1
  } catch {
    return -1
  }
}

const canApply = computed(() => userRole.value === 0)
const isLoggedIn = computed(() => userStore.isLoggedIn)

function handleIntern() {
  if (!isLoggedIn.value) {
    warningMessage.value = isZh.value ? '请先登录后再申请' : 'Please login first to apply'
    showWarningModal.value = true
    return
  }
  if (!canApply.value) {
    warningMessage.value = isZh.value ? '您已是团队成员，无需再次申请' : 'You are already a team member'
    showWarningModal.value = true
    return
  }
  router.push('/career/intern-apply')
}

function handleFullTime() {
  if (!isLoggedIn.value) {
    warningMessage.value = isZh.value ? '请先登录后再申请' : 'Please login first to apply'
    showWarningModal.value = true
    return
  }
  if (userRole.value !== 0) {
    warningMessage.value = isZh.value ? '您已是团队成员，无需再次申请' : 'You are already a team member'
    showWarningModal.value = true
    return
  }
  router.push('/career/join')
}

onMounted(() => {
  setTimeout(() => { pageEnter.value = true }, 100)
  // 入场动画完成后移除延时
  setTimeout(() => { cardsEntered.value = true }, 1400)
  // 获取用户角色
  userRole.value = getUserRole()
})
</script>

<style scoped>
.career-page {
  background: #fbfbfb;
  padding: 120px 24px 72px;
  min-height: 100vh;
}

.career-container {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
}

/* 标题 */
.career-header {
  text-align: center;
  margin-bottom: 64px;
}

.career-title {
  font-size: 72px;
  line-height: 1.02;
  letter-spacing: -0.04em;
  font-weight: 500;
  color: #0b0f19;
  margin: 0 0 16px;
}

.career-subtitle {
  margin: 0 auto;
  max-width: 560px;
  font-size: 17px;
  line-height: 1.7;
  color: rgba(17, 24, 39, 0.62);
}

/* 动画 */
.reveal {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--d, 0ms);
}

.reveal.is-in {
  opacity: 1;
  transform: translateY(0);
}

/* 卡片入场动画 */
.career-card.reveal {
  opacity: 0;
  transform: translateY(40px) scale(0.96);
  transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), 
              transform 0.8s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.3s ease,
              border-color 0.3s ease;
  transition-delay: var(--d, 0ms);
  pointer-events: none;
}

.career-card.reveal.is-in {
  opacity: 1;
  transform: translateY(0) scale(1);
}

/* 入场完成后移除延时，让 hover 立即响应 */
.career-card.reveal.entered {
  transition-delay: 0ms !important;
  pointer-events: auto;
  transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), 
              transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1),
              box-shadow 0.2s ease,
              border-color 0.2s ease;
}

.career-card.reveal.entered:hover {
  transform: translateY(-6px) scale(1.01);
}

/* 选项卡片容器 */
.career-options {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 卡片 */
.career-card {
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 36px 40px;
  background: #fff;
  border-radius: 20px;
  border: 2px solid #e5e7eb;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
}

.career-card:hover {
  box-shadow: 0 24px 56px rgba(15, 23, 42, 0.14);
  border-color: #0b0f19;
}

.career-card:active {
  transform: translateY(4px) scale(0.96) !important;
  transition: transform 0.08s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.08s ease,
              border-color 0.08s ease !important;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
  border-color: #9ca3af;
}

.career-card:hover .card-arrow {
  transform: translateX(6px);
  color: #0b0f19;
}

.career-card:hover .card-icon--intern {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-color: transparent;
  color: #fff;
}

.career-card:hover .card-icon--fulltime {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 8px 24px rgba(245, 158, 11, 0.35);
}

/* 图标 */
.card-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.card-icon--intern {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border: 2px solid #a7f3d0;
  color: #059669;
}

.card-icon--fulltime {
  background: linear-gradient(135deg, #fef9e7 0%, #fef3c7 100%);
  border: 2px solid #fcd34d;
  color: #d97706;
}

/* 内容 */
.card-content {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 24px;
  font-weight: 600;
  color: #0b0f19;
  margin: 0 0 10px;
  letter-spacing: -0.01em;
}

.card-desc {
  font-size: 15px;
  color: #6b7280;
  margin: 0 0 16px;
  line-height: 1.6;
}

.card-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 20px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.card-features li {
  font-size: 13px;
  color: #9ca3af;
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-features li::before {
  content: '';
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #d1d5db;
}

/* 箭头 */
.card-arrow {
  flex-shrink: 0;
  color: #d1d5db;
  transition: all 0.3s ease;
}

/* 底部 */
.career-footer {
  order: 1;
  margin-top: 56px;
  text-align: center;
}

.career-footer p {
  font-size: 15px;
  color: #6b7280;
  margin: 0;
}

.contact-link {
  color: #0b0f19;
  text-decoration: none;
  font-weight: 600;
  position: relative;
  margin-left: 4px;
  transition: color 0.2s ease;
}

.contact-link::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -2px;
  width: 100%;
  height: 2px;
  background: #0b0f19;
  transform: scaleX(1);
  transform-origin: left;
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), background 0.2s ease;
}

.contact-link:hover {
  color: #7c3aed;
}

.contact-link:hover::after {
  background: #7c3aed;
  transform: scaleX(1.05);
  animation: underline-bounce 0.4s ease;
}

@keyframes underline-bounce {
  0% { transform: scaleX(1); }
  50% { transform: scaleX(0.3); }
  100% { transform: scaleX(1.05); }
}

@media (max-width: 900px) {
  .career-page { padding: 104px 20px 64px; }
  .career-header { margin-bottom: 40px; }
  .career-title { font-size: clamp(44px, 12vw, 60px); }
  .career-subtitle { font-size: 16px; }
  .career-card { align-items: flex-start; gap: 18px; padding: 24px 20px; border-radius: 16px; }
  .card-icon { width: 60px; height: 60px; border-radius: 16px; }
  .card-title { font-size: 21px; }
  .card-arrow { align-self: center; }
  .career-footer { margin-top: 40px; }
}

@media (max-width: 520px) {
  .career-card { flex-direction: column; }
  .card-arrow { display: none; }
  .card-features { gap: 8px 14px; }
}
</style>
