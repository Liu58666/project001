<!-- src/pages/Third.vue -->
<template>
  <section
    class="cta-section"
    :class="{ 'cta-section--home-handoff': homeHandoff }"
  >
    <!-- 中部视频背景（只负责展示） -->
    <div class="cta-band">
      <video
        class="cta-video"
        autoplay
        muted
        loop
        playsinline
      >
        <source :src="videoSrc" type="video/webm" />
      </video>
    </div>

    <!-- 前景内容 -->
    <div class="cta-container" ref="ctaRef">
      <div class="cta-content">
        <div class="cta-preheadline fade-in-slide" :class="{ 'animate': isVisible }">{{ $t('cta.preheadline') }}</div>

        <h2 class="cta-headline fade-in-slide" :class="{ 'animate': isVisible }">
          {{ $t('cta.headlineLine1') }}
          <br />
          {{ $t('cta.headlineLine2') }}
        </h2>

        <div class="cta-buttons fade-in-slide" :class="{ 'animate': isVisible }">
          <button class="btn-try" @click="router.push('/coming-soon')">
            <span class="text-container">
              <span class="text">{{ $t('cta.talk') }}</span>
            </span>
          </button>
          <button class="btn-talk animated-button" @click="router.push('/coming-soon')">
            <svg xmlns="http://www.w3.org/2000/svg" class="arr-2" viewBox="0 0 24 24">
              <path
                d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z"
              ></path>
            </svg>
            <span class="text">{{ $t('cta.explore') }}</span>
            <span class="circle"></span>
            <svg xmlns="http://www.w3.org/2000/svg" class="arr-1" viewBox="0 0 24 24">
              <path
                d="M16.1716 10.9999L10.8076 5.63589L12.2218 4.22168L20 11.9999L12.2218 19.778L10.8076 18.3638L16.1716 12.9999H4V10.9999H16.1716Z"
              ></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import videoSrc from '@/assets/images/section4.webm'

defineProps({
  homeHandoff: {
    type: Boolean,
    default: false,
  },
})

const router = useRouter()
const ctaRef = ref(null)
const isVisible = ref(false)
let observer = null

onMounted(() => {
  const reveal = () => {
    // 防止重复触发
    if (isVisible.value) return
    isVisible.value = true

    // 触发一次后就彻底断开，避免后续回调/内存泄漏
    if (observer) {
      observer.disconnect()
      observer = null
    }
  }

  const isElementInViewport = (el) => {
    if (!el) return false
    const rect = el.getBoundingClientRect()
    const vh = window.innerHeight || document.documentElement.clientHeight || 0
    // 给一个比较“宽松但不太早”的判定区间，避免永远触发不了
    return rect.top <= vh * 0.85 && rect.bottom >= vh * 0.15
  }

  const setup = async () => {
    await nextTick()
    const el = ctaRef.value
    if (!el) return

    // 如果一开始就已经在视口内（例如刷新/锚点跳转），直接触发动画
    if (isElementInViewport(el)) {
      requestAnimationFrame(reveal)
      return
    }

    // IntersectionObserver 不可用/构造失败时，降级为直接展示（至少不至于一直 opacity:0）
    if (typeof window === 'undefined' || typeof window.IntersectionObserver === 'undefined') {
      requestAnimationFrame(reveal)
      return
    }

    try {
      observer = new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (entry.isIntersecting) {
              // 用 rAF 确保在下一帧应用 class，避免部分浏览器“加了 class 但动画不跑”的边缘情况
              requestAnimationFrame(reveal)
              break
            }
          }
        },
        {
          threshold: 0.15, // 更容易触发，避免因为阈值导致永远不触发
          rootMargin: '0px 0px -10% 0px'
        }
      )

      observer.observe(el)
    } catch (e) {
      // rootMargin 格式/兼容性等异常：直接展示
      requestAnimationFrame(reveal)
    }
  }

  setup()
})

onBeforeUnmount(() => {
  if (observer) {
    observer.disconnect()
    observer = null
  }
})
</script>

<style scoped>
/* ---------------- 浮现动画样式 (优化版) ---------------- */

/* 1. 定义动画关键帧 */
@keyframes fadeInSlideKeyframes {
  from {
    opacity: 0;
    transform: translateX(-40px); /* 减小位移距离，看起来更精致 */
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeInSlideRightKeyframes {
  from {
    opacity: 0;
    transform: translateX(40px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 更明显的入场（给大标题/按钮用） */
@keyframes fadeInSlideStrongKeyframes {
  from {
    opacity: 0;
    transform: translateX(-80px);
    filter: blur(10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
    filter: blur(0);
  }
}

@keyframes fadeInSlideRightStrongKeyframes {
  from {
    opacity: 0;
    transform: translateX(80px);
    filter: blur(10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
    filter: blur(0);
  }
}

/* 2. 基础状态 */
.fade-in-slide {
  opacity: 0;
  will-change: opacity, transform;
}

/* 3. 激活状态：通用动画设置 */
/* 把 duration 改为 1s，看起来更干脆 */
.fade-in-slide.animate {
  animation: fadeInSlideKeyframes 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* 4. 不同组件的配置 (覆盖上方通用设置) */

/* 小标题：立即出现 */
.cta-preheadline.fade-in-slide.animate {
  animation-delay: 0s;
  animation-duration: 1.1s;
}

/* 大标题：更久、更明显，从右侧滑入 */
.cta-headline.fade-in-slide.animate {
  animation-delay: 0.55s;
  animation-duration: 1.9s;
  animation-name: fadeInSlideRightStrongKeyframes;
}

/* 按钮组：更久、更明显，从左侧滑入 */
.cta-buttons.fade-in-slide.animate {
  animation-delay: 1.15s;
  animation-duration: 2.1s;
  animation-name: fadeInSlideStrongKeyframes;
}

/* 整个 section，白底，内容竖直居中 */
.cta-section {
  position: relative;
  width: 100%;
  padding: 80px 0 0 0;
  overflow: hidden;
  background: #ffffff;
}

/* 中间那条视频“色带”：铺满窗口宽度，居中放置 */
.cta-band {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 100vw;          /* 横向铺满视口 */
  height: 460px;         /* 色带高度，可根据实际效果微调 */
  transform: translate(-50%, -50%);
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

/* 只在上方 30% 加一个淡化叠加层 */
.cta-band::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  background: linear-gradient(
    to bottom,
    #ffffff 0%,
    #ffffff 22%,
    rgba(255, 255, 255, 0.96) 32%,
    rgba(255, 255, 255, 0.88) 42%,
    rgba(255, 255, 255, 0.70) 52%,
    rgba(255, 255, 255, 0.0) 70%
  );
}

/* 视频：纯裁剪，不再做额外处理 */
.cta-video {
  width: 100%;
  height: 100%;
  object-fit: cover;      /* 按条带裁剪 */
  object-position: 50% 0%; /* 以顶部为主：50% 水平居中，0% 顶部 */
}

/* 内容容器：在视频之上居中显示 */
.cta-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  position: relative;
  z-index: 2;             /* 高于视频和叠加层 */
  min-height: 420px;
  display: flex;
  align-items: center;
}

.cta-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  width: 100%;
  margin-bottom: 100px;
}

.cta-preheadline {
  font-size: 18px;
  font-weight: 900;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #9ca3af;
  font-family: 'Courier New', monospace;
}

.cta-headline {
  font-size: 46px;
  font-weight: 500;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: #111827;
  max-width: 900px;
  margin-top: 30px;
}

.cta-buttons {
  display: flex;
  gap: 50px;
  align-items: center;
  margin-top: 14px;
  /* transform: translateY(30px); */ /* 删除这一行，避免和动画冲突 */
}

/* 动画按钮基础样式 */
.animated-button {
  position: relative;
  display: flex;
  align-items: center;
  gap: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
}

.animated-button svg {
  position: absolute;
  width: 24px;
  z-index: 9;
  transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
}

.animated-button .arr-1 {
  right: 16px;
}

.animated-button .arr-2 {
  left: -25%;
}

.animated-button .circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  border-radius: 50%;
  opacity: 0;
  transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
}

.animated-button .text {
  position: relative;
  z-index: 1;
  transform: translateX(-12px);
  transition: all 0.8s cubic-bezier(0.23, 1, 0.32, 1);
}

.animated-button:hover {
  box-shadow: 0 0 0 12px transparent;
  border-radius: 12px;
}

.animated-button:hover .arr-1 {
  right: -25%;
}

.animated-button:hover .arr-2 {
  left: 16px;
}

.animated-button:hover .text {
  transform: translateX(12px);
}

.animated-button:active {
  scale: 0.95;
  box-shadow: 0 0 0 4px rgba(0, 0, 0, 0.1);
}

.animated-button:hover .circle {
  width: 220px;
  height: 220px;
  opacity: 1;
}

/* 第一个按钮 - 黑色背景，使用新特效 */
.btn-try,
.btn-try *,
.btn-try :after,
.btn-try :before,
.btn-try:after,
.btn-try:before {
  border: 0 solid;
  box-sizing: border-box;
}

.btn-try {
  -webkit-tap-highlight-color: transparent;
  -webkit-appearance: button;
  appearance: button;
  background-color: #000;
  background-image: none;
  color: #fff;
  cursor: pointer;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif,
    Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color Emoji;
  font-size: 15px;
  font-weight: 500;
  line-height: 1.5;
  margin: 0;
  padding: 14px 28px;
  text-transform: none;
  border-radius: 999px;
  border: none;
  z-index: 0;
  position: relative;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-try:disabled {
  cursor: default;
}

.btn-try:-moz-focusring {
  outline: auto;
}

.btn-try svg {
  display: block;
}

.btn-try [hidden] {
  display: none;
}

.btn-try,
.btn-try .text-container {
  overflow: hidden;
  position: relative;
}

.btn-try .text-container {
  display: block;
  mix-blend-mode: difference;
  color: #fff;
}

.btn-try .text {
  display: block;
  position: relative;
  color: #fff;
}

.btn-try:hover .text {
  -webkit-animation: move-up-alternate 0.3s forwards;
  animation: move-up-alternate 0.3s forwards;
}

@-webkit-keyframes move-up-alternate {
  0% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(80%);
  }

  51% {
    transform: translateY(-80%);
  }

  to {
    transform: translateY(0);
  }
}

@keyframes move-up-alternate {
  0% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(80%);
  }

  51% {
    transform: translateY(-80%);
  }

  to {
    transform: translateY(0);
  }
}

.btn-try:after,
.btn-try:before {
  --skew: 0.2;
  background: #fff;
  content: "";
  display: block;
  height: 102%;
  left: calc(-50% - 50% * var(--skew));
  pointer-events: none;
  position: absolute;
  top: -104%;
  transform: skew(calc(150deg * var(--skew))) translateY(var(--progress, 0));
  transition: transform 0.2s ease;
  width: 100%;
}

.btn-try:after {
  --progress: 0%;
  left: calc(50% + 50% * var(--skew));
  top: 102%;
  z-index: -1;
}

.btn-try:hover:before {
  --progress: 100%;
}

.btn-try:hover:after {
  --progress: -102%;
}

/* 第二个按钮 - 白色背景 */
.btn-talk {
  padding: 14px 28px;
  background: #ffffff;
  color: #111827;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  font-size: 15px;
  font-weight: 500;
  box-shadow: 0 0 0 2px transparent;
}

.btn-talk svg {
  fill: #111827;
}

.btn-talk .circle {
  background-color: rgba(0, 0, 0, 0.05);
}

.btn-talk:hover .circle {
  background-color: rgba(255, 255, 255, 0.1);
}

.btn-talk:hover {
  background: #000000;
  border-color: #000000;
  color: #ffffff;
}

.btn-talk:hover svg {
  fill: #ffffff;
}

.btn-talk:active {
  box-shadow: 0 0 0 4px rgba(0, 0, 0, 0.05);
}

@media (min-width: 901px) {
  .cta-section--home-handoff .cta-band {
    top: 40%;
    height: 500px;
  }

  .cta-section--home-handoff .cta-band::after {
    background: linear-gradient(
      to bottom,
      #ffffff 0%,
      #ffffff 18%,
      rgba(255, 255, 255, 0.96) 27%,
      rgba(255, 255, 255, 0.82) 35%,
      rgba(255, 255, 255, 0.5) 43%,
      rgba(255, 255, 255, 0.18) 50%,
      rgba(255, 255, 255, 0) 55%
    );
  }
}

@media (max-width: 900px) {
  .cta-section {
    padding-top: 20px;
  }

  .cta-section--home-handoff {
    z-index: 4;
    margin-top: -2px;
    box-shadow: 0 -2px 0 #ffffff;
  }

  .cta-band {
    height: 100%;
  }

  .cta-container {
    min-height: 420px;
    padding: 32px 20px 36px;
  }

  .cta-content {
    gap: 16px;
    margin-bottom: 0;
  }

  .cta-preheadline {
    font-size: 14px;
    line-height: 1.5;
  }

  .cta-headline {
    margin-top: 12px;
    font-size: clamp(32px, 9vw, 44px);
    line-height: 1.12;
  }

  .cta-buttons {
    width: 100%;
    max-width: 420px;
    flex-direction: column;
    gap: 12px;
    margin-top: 12px;
  }

  .btn-try,
  .btn-talk {
    width: 100%;
    min-height: 50px;
    justify-content: center;
  }

  /* 手机屏幕停留时间更短，避免先看到长时间的空白色带。 */
  .cta-preheadline.fade-in-slide.animate {
    animation-delay: 0s;
    animation-duration: 0.45s;
  }

  .cta-headline.fade-in-slide.animate {
    animation-delay: 0.08s;
    animation-duration: 0.68s;
    animation-name: fadeInSlideRightKeyframes;
  }

  .cta-buttons.fade-in-slide.animate {
    animation-delay: 0.24s;
    animation-duration: 0.68s;
    animation-name: fadeInSlideKeyframes;
  }
}

@media (prefers-reduced-motion: reduce) {
  .fade-in-slide,
  .fade-in-slide.animate {
    opacity: 1;
    animation: none;
    transform: none;
    filter: none;
  }
}

</style>
