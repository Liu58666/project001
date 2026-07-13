<template>
  <section class="register-page">
    <div class="panel left-panel">
      <div class="form-shell">
        <h2 class="title slide-in-right" :class="{ 'animate': isMounted }">{{ t('auth.createAccount') }}</h2>
        <p class="subtitle slide-in-right" :class="{ 'animate': isMounted }">{{ t('auth.registerSubtitle') }}</p>

        <form class="form" @submit.prevent="handleRegister">
          
          <div class="form-control scale-fade" :class="{ 'animate': isMounted, filled: !!username }">
            <input
              v-model="username"
              type="text"
              required
              autocomplete="off"
            />
            <label>
              <span
                v-for="(ch, idx) in usernameLabelChars"
                :key="`username-${idx}-${ch}`"
                :style="{ 'transition-delay': `${idx * 50}ms` }"
              >
                {{ ch }}
              </span>
            </label>
          </div>

          <div class="phone-group scale-fade" :class="{ 'animate': isMounted }">
            <div class="form-control" :class="{ filled: !!phone }">
              <input
                v-model="phone"
                type="tel"
                required
                autocomplete="off"
              />
              <label>
                <span
                  v-for="(ch, idx) in phoneLabelChars"
                  :key="`phone-${idx}-${ch}`"
                  :style="{ 'transition-delay': `${idx * 50}ms` }"
                >
                  {{ ch }}
                </span>
              </label>
            </div>
            <button 
              type="button" 
              class="send-code-btn"
              :class="{
                counting: isCounting,
                animating: sendAnimating,
                sending: showSendingUI
              }"
              :disabled="isCounting || sendLoading || sendAnimating"
              @click="sendCode"
            >
              {{ isCounting ? `${count}s` : (showSendingUI ? t('auth.sending') : t('auth.sendCode')) }}
            </button>
          </div>

          <div class="form-control scale-fade" :class="{ 'animate': isMounted, filled: !!code }">
            <input
              v-model="code"
              type="text"
              required
              autocomplete="off"
            />
            <label>
              <span
                v-for="(ch, idx) in codeLabelChars"
                :key="`code-${idx}-${ch}`"
                :style="{ 'transition-delay': `${idx * 50}ms` }"
              >
                {{ ch }}
              </span>
            </label>
          </div>

          <div class="form-control scale-fade" :class="{ 'animate': isMounted, filled: !!password }">
            <input
              v-model="password"
              type="password"
              required
              autocomplete="off"
            />
            <label>
              <span
                v-for="(ch, idx) in passwordLabelChars"
                :key="`password-${idx}-${ch}`"
                :style="{ 'transition-delay': `${idx * 50}ms` }"
              >
                {{ ch }}
              </span>
            </label>
          </div>

          <div class="form-control scale-fade" :class="{ 'animate': isMounted, filled: !!confirmPassword }">
            <input
              v-model="confirmPassword"
              type="password"
              required
              autocomplete="off"
            />
            <label>
              <span
                v-for="(ch, idx) in confirmLabelChars"
                :key="`confirm-${idx}-${ch}`"
                :style="{ 'transition-delay': `${idx * 50}ms` }"
              >
                {{ ch }}
              </span>
            </label>
          </div>

          <button type="submit" class="primary-btn blur-fade" :class="{ 'animate': isMounted }" :disabled="registerLoading">
            {{ registerLoading ? t('auth.signingUp') : t('auth.signUp') }}
          </button>
        </form>

        <div class="footer slide-in-left" :class="{ 'animate': isMounted }">
          {{ t('auth.alreadyHaveAccount') }}
          <router-link to="/login" class="footer-link">{{ t('auth.loginHere') }}</router-link>
        </div>
      </div>
    </div>

    <div class="panel right-panel">
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
          </div>

      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import bgVideo from '@/assets/images/section4.webm'
import { useI18nStore } from '@/stores/i18n'
import { useErrorStore } from '@/stores/error'
import { useWarningStore } from '@/stores/warning'

const router = useRouter()
const i18n = useI18nStore()
const t = (key, vars) => i18n.t(key, vars)
const errorStore = useErrorStore()
const warningStore = useWarningStore()

const splitLabel = (s) => Array.from(String(s || ''))
const toNbsp = (ch) => (ch === ' ' ? '\u00A0' : ch)

const usernameLabelChars = computed(() => splitLabel(t('auth.labelUsername')).map(toNbsp))
const phoneLabelChars = computed(() => splitLabel(t('auth.labelPhone')).map(toNbsp))
const codeLabelChars = computed(() => splitLabel(t('auth.labelCode')).map(toNbsp))
const passwordLabelChars = computed(() => splitLabel(t('auth.labelPassword')).map(toNbsp))
const confirmLabelChars = computed(() => splitLabel(t('auth.labelConfirm')).map(toNbsp))

// Use Vite proxy: /api -> backend (see vite.config.js)
const API_BASE = ''

const username = ref('')
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const code = ref('')
const isMounted = ref(false)

// loading
const sendLoading = ref(false)
const registerLoading = ref(false)
const sendAnimating = ref(false)      // 点击后动画阶段
const showSendingUI = ref(false)      // 动画后显示 Sending...（白底）

// 倒计时逻辑
const isCounting = ref(false)
const count = ref(60)
let timer = null

const stopCountdown = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

const startCountdown = (seconds) => {
  stopCountdown()
  isCounting.value = true
  count.value = seconds

  timer = setInterval(() => {
    count.value -= 1
    if (count.value <= 0) {
      stopCountdown()
      isCounting.value = false
      count.value = seconds
    }
  }, 1000)
}

async function postJson(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  let data = null
  try {
    data = await res.json()
  } catch (e) {
    // ignore
  }

  if (!res.ok) {
    throw new Error(extractApiErrorMessage(data, res.status))
  }

  return data
}

function extractApiErrorMessage(data, status) {
  // FastAPI / Pydantic style:
  // { detail: [ { loc: [...], msg: '...', type: '...' }, ... ] }
  if (Array.isArray(data?.detail)) {
    const msgs = data.detail
      .map((it) => it?.msg)
      .filter((s) => typeof s === 'string' && s.trim().length > 0)
      .map((s) => s.trim())
    if (msgs.length) {
      // 去重，保持顺序
      const uniq = []
      for (const m of msgs) if (!uniq.includes(m)) uniq.push(m)
      return uniq.join(' ; ')
    }
  }

  if (typeof data?.detail === 'string' && data.detail.trim()) return data.detail.trim()
  if (typeof data?.message === 'string' && data.message.trim()) return data.message.trim()
  if (typeof data === 'string' && data.trim()) return data.trim()
  return `Request failed (${status})`
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

const sendCode = async () => {
  const p = phone.value.trim()
  if (!p) {
    warningStore.showWarning(t('auth.errEnterPhoneFirst'))
    return
  }

  if (isCounting.value || sendLoading.value || sendAnimating.value) return

  // 进入 1s 动画阶段：先不显示 Sending...
  sendAnimating.value = true
  showSendingUI.value = false

  // 请求可以立刻发（不耽误），但 UI 1s 后才显示 Sending
  sendLoading.value = true
  const req = postJson('/api/auth/send-code', { phone: p })

  try {
    // 等动画走完 2s
    await sleep(2000)
    sendAnimating.value = false
    showSendingUI.value = true

    // 等接口返回，再开始倒计时
    const resp = await req
    const seconds = Number(resp?.resend_interval_seconds) || 60

    // 进入倒计时前，把 Sending UI 关掉（倒计时优先生效）
    showSendingUI.value = false
    startCountdown(seconds)
  } catch (err) {
    errorStore.showError(err?.message || t('auth.errSendCodeFailed'))
    showSendingUI.value = false
  } finally {
    sendAnimating.value = false
    sendLoading.value = false
  }
}

// 创办时间逻辑（你这页暂时没用到也保留）
const foundedTimestamp = new Date('2024-01-28T00:00:00').getTime()
const foundedDays = computed(() => {
  const diffTime = Date.now() - foundedTimestamp
  return Math.floor(diffTime / (1000 * 60 * 60 * 24))
})
const foundedHours = computed(() => {
  const diffTime = Date.now() - foundedTimestamp
  return Math.floor(diffTime / (1000 * 60 * 60)) % 24
})

const handleRegister = async () => {
  if (registerLoading.value) return

  if (password.value !== confirmPassword.value) {
    warningStore.showWarning(t('auth.errPasswordMismatch'))
    return
  }

  const payload = {
    username: username.value.trim(),
    phone: phone.value.trim(),
    password: password.value,
    confirm_password: confirmPassword.value,
    code: code.value.trim(),
  }

  registerLoading.value = true
  try {
    const resp = await postJson('/api/auth/register', payload)
    console.log('Register success:', resp)
    // 注册成功：跳回登录页（你也可以改成直接进入首页）
    router.push('/login')
  } catch (err) {
    errorStore.showError(err?.message || t('auth.errRegisterFailed'))
  } finally {
    registerLoading.value = false
  }
}

onMounted(() => {
  setTimeout(() => {
    isMounted.value = true
  }, 100)
})

onBeforeUnmount(() => {
  stopCountdown()
})
</script>

<style scoped>
/* ================= 布局翻转核心逻辑 ================= */
.register-page {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
  background: #ffffff; 
}

.panel {
  position: relative;
}

/* --- 左侧面板 (现在放表单) --- */
.left-panel {
  /* 关键：背景透明，允许下方（从右侧延伸过来）的视频显示 */
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(32px, 6vw, 72px);
  position: relative;
  z-index: 1; /* 保证表单浮在视频之上 */
}

/* --- 右侧面板 (现在放视频) --- */
.right-panel {
  display: block;
  position: relative;
  /* 允许视频向左溢出 */
  overflow: visible; 
  z-index: 0;
}

.video-container {
  position: absolute;
  top: 0;
  /* 关键：从右向左延伸 */
  /* Login页面是 left: 0, width: 160% (向右延) */
  /* 这里我们要向左延，所以设置 left 为负值 */
  left: -60%; 
  width: 160%;      
  height: 100%;      
  overflow: hidden; 
}

.bg-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: saturate(1.05); 
}

/* 遮罩层：方向改为向右渐变 (融合左侧白底) */
.video-mask {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  background: linear-gradient(to right, #ffffff 0%, rgba(255,255,255,0) 30%);
}

/* --- 覆盖视频上的文字位置 --- */
/* 因为视频现在在右侧，文字布局可能需要微调，或者保持绝对定位相对原点 */
.tagline {
  position: absolute;
  top: 64px;
  /* 在右侧面板中，可能希望文字靠右一些，或者保持原样 */
  right: 48px; 
  left: auto;
  font-size: 40px;
  line-height: 1.1;
  letter-spacing: -0.02em;
  font-weight: 800;
  z-index: 2;
  color: #111827; 
  text-align: right;
}

.founded-days {
  position: absolute;
  top: 28%;
  /* 调整中心点位置，适应右侧布局 */
  left: 60%; 
  transform: translate(-50%, -50%);
  z-index: 2;
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 10px;
  line-height: 1.2;
  color: #020617;
}

/* 复用 Login 的文字样式 */
.founded-inline { font-weight: 700; }
.founded-inline--brand { font-size: 72px; font-weight: 800; }
.founded-inline--text { font-size: 28px; font-weight: 500; margin-left: 12px; }
.founded-inline--days { font-size: 44px; font-weight: 800; display: block; width: 100%; margin-top: 32px; }
.days-number { font-size: 124px; font-weight: 800; }
.days-label { margin-left: 6px; font-size: 24px; font-weight: 600; }
.hours-number { margin-left: 32px; font-size: 67px; font-weight: 700; }
.hours-label { margin-left: 12px; font-size: 20px; font-weight: 600; }

/* ================= 动画样式（与 Login.vue 区分） ================= */
/* 从右侧滑入 */
.slide-in-right {
  opacity: 0;
  transform: translateX(50px);
  will-change: opacity, transform;
  transition: opacity 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.slide-in-right.animate {
  opacity: 1;
  transform: translateX(0);
}

.title.slide-in-right {
  transition-delay: 0s;
}

.subtitle.slide-in-right {
  transition-delay: 0.2s;
}

.title.slide-in-right.animate {
  transform: translateX(0) translateY(-10px);
}

.subtitle.slide-in-right.animate {
  transform: translateX(0) translateY(-10px);
}

/* 缩放+淡入 */
.scale-fade {
  opacity: 0;
  transform: scale(0.9);
  will-change: opacity, transform;
  transition: opacity 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.scale-fade.animate {
  opacity: 1;
  transform: scale(1);
}

.form-control.scale-fade:nth-of-type(1) {
  transition-delay: 0.4s;
}

.phone-group.scale-fade {
  transition-delay: 0.5s;
}

.form-control.scale-fade:nth-of-type(3) {
  transition-delay: 0.6s;
}

.form-control.scale-fade:nth-of-type(4) {
  transition-delay: 0.7s;
}

.form-control.scale-fade:nth-of-type(5) {
  transition-delay: 0.8s;
}

/* 模糊到清晰 */
.blur-fade {
  opacity: 0.3;
  filter: blur(8px);
  transform: translateY(0);
  will-change: opacity, filter;
  transition: opacity 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              filter 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.blur-fade.animate {
  opacity: 1;
  filter: blur(0);
}

.primary-btn.blur-fade {
  transition-delay: 0.9s;
}

/* 从左侧滑入 */
.slide-in-left {
  opacity: 0;
  transform: translateX(-30px);
  will-change: opacity, transform;
  transition: opacity 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              transform 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.slide-in-left.animate {
  opacity: 1;
  transform: translateX(0);
}

.footer.slide-in-left {
  transition-delay: 1.1s;
}

/* ================= 表单样式 ================= */
.form-shell {
  width: min(420px, 100%);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.title {
  font-size: 28px;
  line-height: 1.2;
  color: #0f172a;
  transform: translateY(-10px);
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
  transform: translateY(-10px);
}

.form {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 复用 input 动画逻辑 */
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
.form-control input:valid {
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
.form-control input:valid + label span {
  color: #1a73e8;
  transform: translateY(-24px);
}
.form-control.filled input { border-bottom-color: #1a73e8; }
.form-control.filled label span { color: #1a73e8; transform: translateY(-24px); }

/* --- 手机号 + 验证码按钮 特殊布局 --- */
.phone-group {
  display: flex;
  align-items: baseline; /* 底部对齐 */
  gap: 12px;
}

.phone-group .form-control {
  flex: 1; /* 输入框占据剩余空间 */
}

.send-code-btn {
  /* 复用 Main.vue 中 Try DAIL 按钮样式 */
  white-space: nowrap;
  border-radius: 0.625em;
  padding: 12px 28px;
  min-width: 140px;
  text-align: center;
  font-size: 15px;
  font-weight: 500;
  border: 1px solid transparent;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  /* transition 保留点击时的平滑过渡 */
  transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease,
    transform 0.18s ease, border-color 0.18s ease;
  background: black;
  color: white;
  border: none;
  position: relative;
  z-index: 1;
  overflow: hidden;
  box-shadow: none;
  height: auto;
  margin-bottom: 0;
}

/* 背景遮罩层基础样式 */
.send-code-btn::after {
  content: "";
  background: white;
  position: absolute;
  z-index: -1;
  left: -20%;
  right: -20%;
  top: 0;
  bottom: 0;
  transform: skewX(-45deg) scale(0, 1);
  transition: transform 0.5s;
}

/* hover 触发（你之前要的 hover） */
.send-code-btn:hover:not(:disabled) {
  color: black;
}
.send-code-btn:hover:not(:disabled)::after {
  transform: skewX(-45deg) scale(1, 1);
}

/* 点击后 2s 动画阶段：白底滑入（用 2s） */
.send-code-btn.animating {
  color: black;
}
.send-code-btn.animating::after {
  transition-duration: 2s;
  transform: skewX(-45deg) scale(1, 1);
}

/* 1s 后 Sending... 阶段：保持白底 */
.send-code-btn.sending {
  color: black;
}
.send-code-btn.sending::after {
  transform: skewX(-45deg) scale(1, 1);
}

/* 倒计时阶段：保持白底 */
.send-code-btn.counting {
  color: black;
}
.send-code-btn.counting::after {
  transform: skewX(-45deg) scale(1, 1);
}

/* 禁用默认（如果以后有其它禁用原因） */
.send-code-btn:disabled {
  color: #9ca3af;
  cursor: not-allowed;
  background: #4b5563;
  opacity: 0.6;
}
.send-code-btn:disabled::after {
  display: none;
}

/* 但 animating / sending / counting 期间禁用也要“白底”显示 */
.send-code-btn.animating:disabled,
.send-code-btn.sending:disabled,
.send-code-btn.counting:disabled {
  color: black;
  background: black;
  opacity: 1;
}
.send-code-btn.animating:disabled::after,
.send-code-btn.sending:disabled::after,
.send-code-btn.counting:disabled::after {
  display: block;
  transform: skewX(-45deg) scale(1, 1);
}

/* 主按钮 */
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

.footer {
  font-size: 13px;
  color: #6b7280;
  margin-top: 6px;
  text-align: left; 
}

.footer-link {
  color: #0f172a;
  font-weight: 600;
  text-decoration: none;
  margin-left: 4px;
}

.footer-link:hover {
  color: #9333ea;
  text-decoration: underline;
  text-decoration-thickness: 2px;
  text-underline-offset: 4px;
}

@media (max-width: 900px) {
  .register-page { display: block; min-height: 100svh; background: linear-gradient(160deg, #ffffff 45%, #fdf2f8 100%); }
  .right-panel { display: none; }
  .left-panel { min-height: 100svh; padding: 104px 20px 56px; }
  .form-shell { width: min(440px, 100%); padding: 28px 20px; border-radius: 22px; background: rgba(255, 255, 255, 0.9); box-shadow: 0 18px 50px rgba(15, 23, 42, 0.1); }
  .title { font-size: 26px; }
  .phone-group { align-items: stretch; flex-direction: column; gap: 0; }
  .send-code-btn { width: 100%; min-width: 0; min-height: 46px; margin-bottom: 12px; }
  .primary-btn { min-height: 48px; }
}

</style>
