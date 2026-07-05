<template>
  <section class="login-page">
    <div class="panel left-panel">
      <div class="video-container">
        <video
          class="bg-video"
          autoplay
          loop
          muted
          playsinline
          :src="bgVideo"
        ></video>
        
        <div class="video-mask"></div>

        <div class="tagline">
          <!-- Redefining AI Possibilities -->
        </div>

        <template v-if="showLeftText">
          <!-- 第一段：Founded -->
          <div class="founded-days left-baseline left-enter" :class="{ on: foundedEnterOn }">
            <span class="founded-inline founded-inline--brand reveal" :class="{ show: foundedRevealOn }">
              DAIL Tech
            </span>

            <span
              class="founded-inline founded-inline--text reveal"
              :class="{ show: foundedRevealOn }"
              style="transition-delay:.12s"
            >
              {{ t('auth.foundedText') }}
            </span>

            <span class="founded-inline founded-inline--days">
              <span class="days-number count-up reveal" :class="{ show: foundedNumOn }">
                {{ animatedDaysFounded }}
              </span>

              <span
                class="days-label reveal"
                :class="{ show: foundedRevealOn }"
                style="transition-delay:.18s"
              >{{ t('common.days') }}</span>

              <span class="hours-number count-up reveal" :class="{ show: foundedNumOn }" style="margin-left:32px">
                {{ animatedHoursFounded }}
              </span>

              <span
                class="hours-label reveal"
                :class="{ show: foundedRevealOn }"
                style="transition-delay:.22s"
              >{{ t('common.hours') }}</span>
            </span>
          </div>

          <!-- 第二段：Welcome -->
          <div class="welcome-block left-baseline left-enter" :class="{ on: welcomeEnterOn }">
            <div
              class="welcome-line reveal"
              :class="{ show: welcomeRevealOn }"
              style="transition-delay:0s"
            >
              {{ t('auth.welcomeTo') }}
              <span class="welcome-name">{{ displayName }}</span>
            </div>

            <div
              class="welcome-days reveal"
              :class="{ show: welcomeRevealOn }"
              style="transition-delay:.12s"
            >
              {{ t('auth.welcomeDaysPrefix') }}
              <span class="welcome-days-number count-up reveal" :class="{ show: welcomeNumOn }">
                {{ animatedDaysWelcome }}
              </span>
              <span class="welcome-days-label">{{ t('common.days') }}</span>
              {{ t('auth.welcomeDaysSuffix') }}
            </div>
          </div>
        </template>
      </div>
    </div>

    <div class="panel right-panel">
      <div class="form-shell">
        <h2 class="title fade-in-up" :class="{ 'animate': isMounted }">{{ t('auth.signInTitle') }}</h2>
        <p class="subtitle fade-in-up" :class="{ 'animate': isMounted }">{{ t('auth.signInSubtitle') }}</p>

         <form class="form" novalidate @submit.prevent="handleSubmit">
           <div class="form-control fade-in-up" :class="{ 'animate': isMounted, filled: !!phone }">
             <input
               v-model="phone"
               type="tel"
               autocomplete="tel"
             />
             <label>
               <span
                 v-for="(ch, idx) in phoneNumberLabelChars"
                 :key="`phone-${idx}-${ch}`"
                 :style="{ 'transition-delay': `${idx * 50}ms` }"
               >
                 {{ ch }}
               </span>
             </label>
           </div>

           <div class="form-control fade-in-up" :class="{ 'animate': isMounted, filled: !!password }">
             <input
               v-model="password"
               type="password"
               autocomplete="off"
             />
             <label>
               <span
                 v-for="(ch, idx) in passwordLabelChars"
                 :key="`pass-${idx}-${ch}`"
                 :style="{ 'transition-delay': `${idx * 50}ms` }"
               >
                 {{ ch }}
               </span>
             </label>
           </div>

          <div class="form-row fade-in-up" :class="{ 'animate': isMounted }">
            <label class="checkbox">
              <input v-model="remember" type="checkbox" />
              <span>{{ t('auth.rememberMe') }}</span>
            </label>
            <label class="checkbox checkbox--animation">
              <input v-model="enableLoginAnimation" type="checkbox" />
              <span>{{ i18n.locale === 'zh' ? '开启登录动画' : 'Enable login animation' }}</span>
            </label>
          </div>

          <button type="submit" class="primary-btn fade-in-up" :class="{ 'animate': isMounted }">{{ t('auth.signIn') }}</button>
        </form>

        <div class="footer fade-in-up" :class="{ 'animate': isMounted }">
          {{ t('auth.newToDail') }}
          <router-link to="/register" class="footer-link">{{ t('auth.registerNow') }}</router-link>
        </div>
      </div>
    </div>

    <!-- 过渡层：Sign In 后出现 -->
    <div v-if="isTransitioning" class="transition-overlay">
      <!-- 黑色从左到右覆盖 -->
      <div class="transition-cover" :class="{ run: overlayRun }"></div>

      <!-- 白色文字阶段 -->
      <div class="transition-stage">
        <!-- 第一段：Founded（白色） -->
        <template v-if="overlayPhase === 'founded'">
          <div
            class="founded-days left-baseline left-enter"
            :class="[{ on: foundedEnterOn }, { 'phase-out': foundedOutOn }]"
          >
            <span class="founded-inline founded-inline--brand reveal" :class="{ show: foundedRevealOn }">
              DAIL Tech
            </span>

            <span
              class="founded-inline founded-inline--text reveal"
              :class="{ show: foundedRevealOn }"
              style="transition-delay:.12s"
            >
              {{ t('auth.foundedText') }}
            </span>

            <span class="founded-inline founded-inline--days">
              <span class="days-number count-up reveal" :class="{ show: foundedNumOn }">
                {{ animatedDaysFounded }}
              </span>

              <span
                class="days-label reveal"
                :class="{ show: foundedRevealOn }"
                style="transition-delay:.18s"
              >{{ t('common.days') }}</span>

              <span class="hours-number count-up reveal" :class="{ show: foundedNumOn }" style="margin-left:32px">
                {{ animatedHoursFounded }}
              </span>

              <span
                class="hours-label reveal"
                :class="{ show: foundedRevealOn }"
                style="transition-delay:.22s"
              >{{ t('common.hours') }}</span>
            </span>
          </div>
        </template>

        <!-- 第二段：Welcome（只保留 days 这一行） -->
        <template v-else-if="overlayPhase === 'welcome'">
          <div
            class="welcome-block left-baseline left-enter"
            :class="[{ on: welcomeEnterOn }, { 'phase-out': welcomeOutOn }]"
          >
            <div
              class="welcome-days reveal"
              :class="{ show: welcomeRevealOn }"
              style="transition-delay:0s"
            >
              {{ t('auth.welcomeDaysPrefix') }}
              <span class="welcome-days-number count-up reveal" :class="{ show: welcomeNumOn }">
                {{ animatedDaysWelcome }}
              </span>
              <span class="welcome-days-label">{{ t('common.days') }}</span>
              {{ t('auth.welcomeDaysSuffix') }}
            </div>
          </div>
        </template>

        <!-- Final：屏幕中心出现 Welcome + Guest -->
        <template v-else-if="overlayPhase === 'final'">
          <div class="final-center final-enter" :class="{ on: finalEnterOn }">
            <div
              class="welcome-line reveal"
              :class="{ show: finalRevealOn }"
              style="transition-delay:0s"
            >
              {{ t('auth.welcomeTo') }}
            </div>
            <div
              class="welcome-name reveal"
              :class="{ show: finalRevealOn }"
              style="transition-delay:.12s"
            >
              {{ displayName }}
            </div>
          </div>
        </template>
      </div>

      <!-- 白色逐渐覆盖全屏 -->
      <div class="transition-white" :class="{ on: whiteCoverOn }"></div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useErrorStore } from '@/stores/error'
import { useWarningStore } from '@/stores/warning'
import { useI18nStore } from '@/stores/i18n'
import bgVideo from '@/assets/images/section4.webm'

// Use Vite proxy: /api -> backend (see vite.config.js)
const API_BASE = ''

function parseApiDate(s) {
  if (!s) return null
  // created_at 这种不带时区的字符串，统一当 UTC 处理，避免浏览器本地时区导致天数偏差
  const hasTz = /Z$|[+-]\d{2}:\d{2}$/.test(s)
  return new Date(hasTz ? s : `${s}Z`)
}

async function postJson(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  let data = null
  try { data = await res.json() } catch (e) {}

  if (!res.ok) {
    const msg =
      data?.detail ||
      data?.message ||
      (typeof data === 'string' ? data : null) ||
      `Request failed (${res.status})`
    throw new Error(msg)
  }

  return data
}

const router = useRouter()
const userStore = useUserStore()
const errorStore = useErrorStore()
const warningStore = useWarningStore()
const i18n = useI18nStore()
const t = (key, vars) => i18n.t(key, vars)

const splitLabel = (s) => Array.from(String(s || ''))
const toNbsp = (ch) => (ch === ' ' ? '\u00A0' : ch)

const phoneNumberLabelChars = computed(() =>
  splitLabel(t('auth.labelPhoneNumber')).map(toNbsp)
)
const passwordLabelChars = computed(() =>
  splitLabel(t('auth.labelPassword')).map(toNbsp)
)

const phone = ref('')
const password = ref('')
const remember = ref(true)
const enableLoginAnimation = ref(localStorage.getItem('enableLoginAnimation') === null || localStorage.getItem('enableLoginAnimation') === 'true')
const isMounted = ref(false)
const showLeftText = ref(false)

// 第一段
const foundedEnterOn = ref(false)
const foundedRevealOn = ref(false)
const foundedNumOn = ref(false)
const animatedDaysFounded = ref(0)
const animatedHoursFounded = ref(0)

// 第二段
const welcomeEnterOn = ref(false)
const welcomeRevealOn = ref(false)
const welcomeNumOn = ref(false)
const animatedDaysWelcome = ref(0)

// 用来清理定时器，避免重复点击叠加
let introTimers = []
const clearIntroTimers = () => {
  introTimers.forEach((t) => clearTimeout(t))
  introTimers = []
}

// 过渡控制变量
const isTransitioning = ref(false)
const overlayRun = ref(false)
const overlayPhase = ref('none') // 'none' | 'founded' | 'welcome' | 'final'
const foundedOutOn = ref(false)
const welcomeOutOn = ref(false)
const finalEnterOn = ref(false)
const finalRevealOn = ref(false)
const whiteCoverOn = ref(false)

// 计算创办天数：创始日 2024年1月28日
const foundedTimestamp = new Date('2024-01-28T00:00:00').getTime()
const DAY_MS = 1000 * 60 * 60 * 24

const foundedDays = computed(() => {
  const diffTime = Date.now() - foundedTimestamp
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
})

// 距离上次整天后的小时数（0-23）
const foundedHours = computed(() => {
  const diffTime = Date.now() - foundedTimestamp
  const diffHours = Math.floor(diffTime / (1000 * 60 * 60)) % 24
  return diffHours
})

// “days in DAIL” = 注册时间(created_at) 到现在(Date.now()) 的整天数
const welcomeDays = computed(() => {
  const created = parseApiDate(currentCreatedAt.value)
  if (!created) return 0
  const diff = Date.now() - created.getTime()
  return Math.max(0, Math.floor(diff / DAY_MS))
})

// 登录人姓名：从 store 获取（本地化兜底）
const displayName = computed(() => userStore.displayName || userStore.username || t('common.guest'))

// 从 store 获取 created_at（用于计算 days in DAIL）
const currentCreatedAt = computed(() => userStore.createdAt)

function animateNumber(targetRef, to, duration = 1200) {
  const from = 0
  const start = performance.now()
  function tick(now) {
    const t = Math.min(1, (now - start) / duration)
    const eased = 1 - Math.pow(1 - t, 3) // easeOutCubic
    targetRef.value = Math.floor(from + (to - from) * eased)
    if (t < 1) requestAnimationFrame(tick)
    else targetRef.value = to
  }
  targetRef.value = 0
  requestAnimationFrame(tick)
}

async function runLeftIntro() {
  clearIntroTimers()

  // 重播：全部归零/关闭
  showLeftText.value = false

  foundedEnterOn.value = false
  foundedRevealOn.value = false
  foundedNumOn.value = false
  animatedDaysFounded.value = 0
  animatedHoursFounded.value = 0

  welcomeEnterOn.value = false
  welcomeRevealOn.value = false
  welcomeNumOn.value = false
  animatedDaysWelcome.value = 0

  await nextTick()
  showLeftText.value = true
  await nextTick()

  requestAnimationFrame(() => {
    // ===== 第一段：Founded =====
    foundedEnterOn.value = true

    introTimers.push(setTimeout(() => {
      foundedRevealOn.value = true          // 文字按 delay 依次出现
    }, 600))

    introTimers.push(setTimeout(() => {
      foundedNumOn.value = true            // 数字最后出现
      animateNumber(animatedDaysFounded, foundedDays.value, 2000)
      animateNumber(animatedHoursFounded, foundedHours.value, 1800)
    }, 600 + 1500)) // 文字基本完成后再出数字

    // ===== 第二段：Welcome（等第一段数字跑完再开始）=====
    const tWelcomeStart = 400 + 1500 + 2000 + 600 // 额外增加间隔增强仪式感

    introTimers.push(setTimeout(() => {
      welcomeEnterOn.value = true
    }, tWelcomeStart))

    introTimers.push(setTimeout(() => {
      welcomeRevealOn.value = true         // Welcome 文字依次出现
    }, tWelcomeStart + 300))

    introTimers.push(setTimeout(() => {
      welcomeNumOn.value = true            // Welcome 数字最后出现
      animateNumber(animatedDaysWelcome, welcomeDays.value, 1800)
    }, tWelcomeStart + 300 + 1300))
  })
}

async function runSignInTransition() {
  clearIntroTimers()

  // 不在左侧面板播（避免重复），这次在 overlay 播
  showLeftText.value = false

  // 归零（复用你原来的动画状态）
  foundedEnterOn.value = false
  foundedRevealOn.value = false
  foundedNumOn.value = false
  animatedDaysFounded.value = 0
  animatedHoursFounded.value = 0
  foundedOutOn.value = false

  welcomeEnterOn.value = false
  welcomeRevealOn.value = false
  welcomeNumOn.value = false
  animatedDaysWelcome.value = 0
  welcomeOutOn.value = false
  finalEnterOn.value = false
  finalRevealOn.value = false
  whiteCoverOn.value = false

  // 打开 overlay
  isTransitioning.value = true
  overlayRun.value = false
  overlayPhase.value = 'none'
  await nextTick()

  // 黑幕横扫
  requestAnimationFrame(() => {
    overlayRun.value = true
  })

  const COVER_MS = 900
  const FOUND_REVEAL_DELAY = 320
  const FOUND_NUM_DELAY = 1400
  const FOUND_NUM_RUN = 2000
  const FOUND_HOLD = 350
  const FOUND_FADE_OUT = 650

  const WELCOME_REVEAL_DELAY = 260
  const WELCOME_NUM_DELAY = 1100
  const WELCOME_NUM_RUN = 1800
  const WELCOME_HOLD = 300

  // 黑幕盖满后，播 Founded
  introTimers.push(setTimeout(() => {
    overlayPhase.value = 'founded'
    foundedOutOn.value = false

    foundedEnterOn.value = true

    introTimers.push(setTimeout(() => {
      foundedRevealOn.value = true
    }, FOUND_REVEAL_DELAY))

    introTimers.push(setTimeout(() => {
      foundedNumOn.value = true
      animateNumber(animatedDaysFounded, foundedDays.value, FOUND_NUM_RUN)
      animateNumber(animatedHoursFounded, foundedHours.value, 1800)
    }, FOUND_NUM_DELAY))

    // Founded 完成后淡出
    const tFoundedEnd = FOUND_NUM_DELAY + FOUND_NUM_RUN + FOUND_HOLD
    introTimers.push(setTimeout(() => {
      foundedOutOn.value = true
    }, tFoundedEnd))

    // 淡出结束后，播 Welcome（只保留 days 行） -> 淡出 -> Final(居中) -> 白色覆盖 -> 跳转
    introTimers.push(setTimeout(() => {
      overlayPhase.value = 'welcome'
      welcomeOutOn.value = false

      // 重置 founded（可选）
      foundedEnterOn.value = false
      foundedRevealOn.value = false
      foundedNumOn.value = false

      // Welcome days 行
      welcomeEnterOn.value = true
      introTimers.push(setTimeout(() => {
        welcomeRevealOn.value = true
      }, WELCOME_REVEAL_DELAY))

      introTimers.push(setTimeout(() => {
        welcomeNumOn.value = true
        animateNumber(animatedDaysWelcome, welcomeDays.value, WELCOME_NUM_RUN)
      }, WELCOME_NUM_DELAY))

      // Welcome days 行结束后淡出
      const WELCOME_FADE_OUT = 650
      const tWelcomeEnd = WELCOME_NUM_DELAY + WELCOME_NUM_RUN + WELCOME_HOLD

      introTimers.push(setTimeout(() => {
        welcomeOutOn.value = true
      }, tWelcomeEnd))

      // 淡出后进入 Final（居中 Welcome + Guest）
      introTimers.push(setTimeout(() => {
        overlayPhase.value = 'final'
        finalEnterOn.value = true

        // 让 final 使用自己的 reveal（稍微放慢）
        introTimers.push(setTimeout(() => {
          finalRevealOn.value = true
        }, 450))

        // Final 显示更久，再白色覆盖
        const WHITE_FADE_MS = 1500
        const FINAL_HOLD_BEFORE_WHITE = 1500

        introTimers.push(setTimeout(() => {
          whiteCoverOn.value = true
        }, 450 + FINAL_HOLD_BEFORE_WHITE))

        // 白色盖满后跳转
        introTimers.push(setTimeout(() => {
          router.push('/home')
        }, 450 + FINAL_HOLD_BEFORE_WHITE + WHITE_FADE_MS))
      }, tWelcomeEnd + WELCOME_FADE_OUT))
    }, tFoundedEnd + FOUND_FADE_OUT))
  }, COVER_MS))
}

const handleSubmit = async () => {
  // 验证输入
  if (!phone.value.trim()) {
    warningStore.showWarning(t('auth.errPhoneRequired'))
    return
  }
  
  if (!password.value) {
    warningStore.showWarning(t('auth.errPasswordRequired'))
    return
  }

  try {
    const payload = {
      phone: phone.value.trim(),
      password: password.value,
    }

    const resp = await postJson('/api/auth/login', payload)

    // 使用 store 保存 token 和用户信息
    userStore.login(
      {
        access_token: resp?.access_token,
        refresh_token: resp?.refresh_token,
        token_type: resp?.token_type,
        access_expires_in: resp?.access_expires_in,
        refresh_expires_in: resp?.refresh_expires_in
      },
      {
        username: resp?.username || '',
        created_at: resp?.created_at || '',
        // optional: backend may return display_name (preferred for UI)
        display_name: resp?.display_name ?? resp?.displayName ?? '',
        email: resp?.email ?? '',
        birthday: resp?.birthday ?? '',
        photo: resp?.photo ?? ''
      },
      remember.value
    )

    // 登录成功后根据设置决定是否播放动画
    if (enableLoginAnimation.value) {
      runSignInTransition()
    } else {
      router.push('/home')
    }
  } catch (err) {
    // 显示错误提示
    const errorMessage = err?.message || t('auth.errLoginFailed')
    if (errorMessage.includes('token') || errorMessage.includes('Incorrect')) {
      errorStore.showError(t('auth.errIncorrectCredential'))
    } else {
      errorStore.showError(errorMessage)
    }
  }
}

// 保存登录动画设置到 localStorage
watch(enableLoginAnimation, (val) => {
  localStorage.setItem('enableLoginAnimation', val ? 'true' : 'false')
})

onMounted(() => {
  // 延迟触发动画，确保 DOM 渲染完成
  setTimeout(() => {
    isMounted.value = true
  }, 100)
})
</script>

<style scoped>
/* ================= 布局核心逻辑 ================= */
.login-page {
  display: grid;
  /* 1. 保持 50/50 布局，确保右侧表单位置固定在右半屏中央 */
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
  background: #ffffff; 
}

.panel {
  position: relative;
  /* 注意：这里不能加 overflow: hidden，否则左侧视频无法溢出到右侧 */
}

/* --- 左侧面板 --- */
.left-panel {
  background: #ffffff;
  display: block;
  position: relative;
  /* 2. 关键：允许内容溢出，这样视频才能跨越中线 */
  overflow: visible;
  z-index: 0; 
}

.video-container {
  position: absolute;
  top: 0;
  left: 0;
  /* 3. 关键：宽度 160%。相对于左侧容器(50%)的160% = 全屏的 80% */
  /* 视频将延伸到右侧面板的下方，形成背景 */
  width: 160%;      
  height: 100%;      
  overflow: hidden; 
  border-radius: 0;
}

.bg-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(1.05); 
}

/* 遮罩层：处理视频边缘与白底的融合 */
.video-mask {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  
  background: 
    /* 上：白色渐变 */
    /* linear-gradient(to bottom, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0) 25%), */
    /* 下：白色渐变 */
    /* linear-gradient(to top, #ffffff 0%, rgba(255,255,255,0.6) 15%, rgba(255,255,255,0) 40%), */
    /* 右：关键过渡，因为视频很宽，需要较宽的渐变来柔和边缘 */
    linear-gradient(to left, #ffffff 0%, rgba(255,255,255,0) 30%);
}

.tagline {
  position: absolute;
  top: 64px;
  left: 48px;
  bottom: auto;
  font-size: 40px;
  line-height: 1.1;
  letter-spacing: -0.02em;
  font-weight: 800;
  z-index: 2;
  color: #111827; 
}

.founded-days {
  position: absolute;
  top: 14%;
  left: 96px;
  transform: none;
  z-index: 2;

  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 10px;

  line-height: 1.2;
  letter-spacing: 0.04em;
  color: #020617;

  background: none;
  padding: 0;
  border-radius: 0;
  box-shadow: none;
  backdrop-filter: none;
}

.founded-inline {
  font-weight: 700;
}

.founded-inline--brand {
  font-size: 72px;
  font-weight: 800;
}

.founded-inline--text {
  font-size: 28px;
  font-weight: 500;
  margin-left: 12px;
}

.founded-inline--days {
  font-size: 44px;
  font-weight: 800;
  display: block;
  width: 100%;
  margin-top: 32px;
  flex-wrap: wrap;
}

.days-number {
  font-size: 124px;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.days-label {
  margin-left: 6px;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 0.08em;
}

.welcome-block {
  position: absolute;
  top: 58%;
  left: 96px;
  transform: none;
  display: flex;
  flex-direction: column;
  gap: 16px;
  color: #0f172a;
  z-index: 2;
}

.welcome-line {
  font-size: 26px;
  font-weight: 500;
  letter-spacing: 0.04em;
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.welcome-name {
  font-size: 124px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.welcome-days {
  font-size: 26px;
  font-weight: 500;
  letter-spacing: 0.04em;
  margin-top: 16px;
}

.welcome-days-number {
  font-size: 94px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.welcome-days-label {
  margin-left: 6px;
  font-size: 32px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.left-enter {
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 2.4s cubic-bezier(0.16, 1, 0.3, 1),
              transform 2.4s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: opacity, transform;
}

.left-enter.on {
  opacity: 1;
  transform: translateY(0);
}

/* 打字机效果 */
/* 打字机效果（暂未使用） */
.typing-line {
  overflow: hidden;
  white-space: nowrap;
  width: 0;
  opacity: 0;
}

.typing-line.typing-run {
  animation: typing 1.2s steps(var(--chars)) forwards,
             fadeIn 0.2s ease forwards;
}

.typing-line--slow.typing-run {
  animation-duration: 1.5s;
}

@keyframes typing {
  from { width: 0; opacity: 1; }
  to { width: 100%; opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 非数字部分渐显（增强仪式感） */
.reveal {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 1.9s cubic-bezier(0.16, 1, 0.3, 1),
              transform 1.9s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: opacity, transform;
}

.reveal.show {
  opacity: 1;
  transform: translateY(0px);
}

/* 数字加强占位，便于动画 */
.count-up {
  will-change: contents;
}

.days-number.reveal,
.hours-number.reveal,
.welcome-days-number.reveal {
  display: inline-block;
}

/* 统一左侧内容基线 */
.left-baseline {
  left: 96px;
  transform: none;
}
.hours-number {
  margin-left: 32px;
  font-size: 67px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.hours-label {
  margin-left: 12px;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.08em;
}

.founded-line--c {
  font-size: 44px;
  font-weight: 800;
}


/* --- 右侧面板 --- */
.right-panel {
  /* 4. 关键：背景透明，否则白底会挡住延伸过来的视频 */
  background: transparent; 
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(32px, 6vw, 72px);
  position: relative;
  z-index: 1; /* 保证表单浮在视频之上 */
}

.form-shell {
  width: min(420px, 100%);
  display: flex;
  flex-direction: column;
  gap: 16px;
  
  /* 可选：如果视频背景太花，可以开启下面的毛玻璃效果让表单更清晰 */
  /* background: rgba(255,255,255,0.7); */
  /* backdrop-filter: blur(12px); */
  /* padding: 40px; */
  /* border-radius: 24px; */
  /* border: 1px solid rgba(255,255,255,0.5); */
}

/* ================= 动画样式 ================= */
.fade-in-up {
  opacity: 0;
  transform: translateY(30px);
  will-change: opacity, transform;
  transition: opacity 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.fade-in-up.animate {
  opacity: 1;
  transform: translateY(0);
}

/* 按逻辑顺序设置延迟时间：从上到下，从左到右 */
.title.fade-in-up {
  transition-delay: 0s;
}

.subtitle.fade-in-up {
  transition-delay: 0.2s;
}

.form-control.fade-in-up:nth-of-type(1) {
  transition-delay: 0.4s;
}

.form-control.fade-in-up:nth-of-type(2) {
  transition-delay: 0.6s;
}

.form-row.fade-in-up {
  transition-delay: 0.8s;
}

.primary-btn.fade-in-up {
  transition-delay: 1.0s;
  filter: blur(8px);
  transform: translateY(0);
  opacity: 0.3;
  transition: opacity 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              filter 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.primary-btn.fade-in-up.animate {
  filter: blur(0);
  opacity: 1;
}

.footer.fade-in-up {
  transition-delay: 1.2s;
}

/* ================= 表单样式 ================= */
.brand {
  font-weight: 800;
  letter-spacing: 0.08em;
  font-size: 13px;
  text-transform: uppercase;
  color: #111827;
}

.title {
  font-size: 28px;
  line-height: 1.2;
  color: #0f172a;
  transform: translateY(-10px);
}

.title.fade-in-up.animate {
  transform: translateY(-10px);
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
  transform: translateY(-10px);
}

.subtitle.fade-in-up.animate {
  transform: translateY(-10px);
}

.form {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 20px; /* 增加一点间距适应浮动标签 */
}

  /* --- 分段动画标签输入框 --- */
  .form-control {
    position: relative;
    margin: 4px 0 16px;
    width: 100%;
  }

  .form-control input {
    background-color: transparent;
    border: 0;
    border-bottom: 2px #000 solid;
    display: block;
    width: 100%;
    padding: 12px 0;
    font-size: 16px;
    color: #000;
  }

  .form-control input:focus,
  .form-control input:focus {
    outline: 0;
    border-bottom-color: #1a73e8;
  }

  .form-control label {
    position: absolute;
    top: 12px;
    left: 0;
    pointer-events: none;
  }

  .form-control label span {
    display: inline-block;
    font-size: 16px;
    min-width: 5px;
    color: #000;
    transition: 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  }

  .form-control input:focus + label span,
  .form-control input:focus + label span {
    color: #1a73e8;
    transform: translateY(-24px);
  }

  /* 内容非空时保持选中态 */
  .form-control.filled input {
    border-bottom-color: #1a73e8;
  }

  .form-control.filled label span {
    color: #1a73e8;
    transform: translateY(-24px);
  }

/* --- 其他表单元素 --- */
.form-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.checkbox--animation span {
  color: #000000;
  font-size: 14px;
}

.checkbox {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #000000;
  cursor: pointer;
}

.checkbox input {
  accent-color: #000;
  width: 16px;
  height: 16px;
}

.link-btn {
  border: none;
  background: none;
  color: #111827;
  font-size: 13px;
  cursor: pointer;
  padding: 6px 8px;
}

.link-btn:hover {
  text-decoration: underline;
}

.primary-btn {
  margin-top: 4px;
  width: 100%;
  padding: 14px 16px;
  border: none;
  border-radius: 999px;
  background: #000;
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.2s ease;
}

.primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 35px rgba(0, 0, 0, 0.15);
  background: #0a0a0a;
}

.primary-btn:active {
  transform: translateY(0);
}

.footer {
  font-size: 13px;
  color: #6b7280;
  margin-top: 6px;
}

.footer-link {
  color: #0f172a;
  font-weight: 600;
  text-decoration: none;
  margin-left: 12px;
}

.footer-link:hover {
  color: #9333ea;
  text-decoration: underline;
  text-decoration-color: #9333ea;
  text-decoration-thickness: 2px;
  text-underline-offset: 4px;
  transform: translateX(2px);
}

/* ===== Sign In 过渡层（全屏） ===== */
.transition-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  pointer-events: all; /* 防止重复点击 */
}

/* 黑幕从左到右覆盖 */
.transition-cover {
  position: absolute;
  inset: 0;
  background: #000;
  transform: translateX(-100%);
  z-index: 1;
}

.transition-cover.run {
  animation: sweep-cover 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes sweep-cover {
  to { transform: translateX(0); }
}

/* 承载白字内容（在黑幕上层） */
.transition-stage {
  position: absolute;
  inset: 0;
  z-index: 2;
}

/* 只在 overlay 内，把两段文字变白 */
.transition-overlay .founded-days,
.transition-overlay .welcome-block {
  color: #fff;
}

/* Founded 淡出（第一段结束后） */
.transition-overlay .phase-out {
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 0.65s ease, transform 0.65s ease;
}

/* Welcome days 行淡出（第二幕末尾） */
.transition-overlay .welcome-block.phase-out {
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 0.65s ease, transform 0.65s ease;
}

/* Final 居中容器（真正居中） */
.final-center {
  position: absolute;
  top: 40%;
  left: 50%;
  width: min(980px, 90vw);
  text-align: center;
  color: #fff;

  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;

  /* 关键：居中 */
  transform: translate(-50%, -50%);
}

/* Final 专用入场动画（不会覆盖居中 transform） */
.final-enter {
  opacity: 0;
  transform: translate(-50%, -50%) translateY(28px);
  transition: opacity 1.6s cubic-bezier(0.16, 1, 0.3, 1),
              transform 1.6s cubic-bezier(0.16, 1, 0.3, 1);
  will-change: opacity, transform;
}

.final-enter.on {
  opacity: 1;
  transform: translate(-50%, -50%) translateY(0);
}

/* welcome-line 原本是 flex，强制居中 */
.transition-overlay .final-center .welcome-line {
  width: 100%;
  justify-content: center;
  align-items: center;
}

/* Guest 居中且继承白色 */
.transition-overlay .final-center .welcome-name {
  color: inherit;
  display: block;
  width: 100%;
  text-align: center;
}

/* 白色从左到右覆盖全屏（在最上层） */
.transition-white {
  position: absolute;
  inset: 0;
  z-index: 4;
  background: #fff;
  pointer-events: none;

  transform: translateX(-100%);
}

.transition-white.on {
  animation: sweep-white 1.1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes sweep-white {
  to { transform: translateX(0); }
}
</style>