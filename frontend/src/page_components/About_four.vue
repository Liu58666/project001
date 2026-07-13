<template>
  <section class="about-four">
    <!-- 背景视频（不影响布局） -->
    <div class="bg-video" aria-hidden="true">
      <video class="bg-video__media" autoplay muted loop playsinline>
        <source :src="bgVideoSrc" type="video/webm" />
      </video>
    </div>
    <div class="about-four-content">
      <!-- 左侧文字 -->
      <div class="about-four-text reveal-left" :class="{ animate: isVisible }">
        <h2 class="about-four-title">{{ t('about.section4Title') }}</h2>
        <p class="about-four-desc">{{ t('about.section4Desc') }}</p>
      </div>
      <!-- 右侧轮播图片 -->
      <div class="about-four-carousel reveal-right" :class="{ animate: isVisible }">
        <transition name="carousel-fade">
          <img 
            :key="currentIndex" 
            :src="aboutImages[currentIndex]" 
            :alt="`DAIL Tech Partnership ${currentIndex + 1}`" 
          />
        </transition>
        <!-- 右侧切换按钮 -->
        <button class="carousel-btn" @click="next" aria-label="Next">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18l6-6-6-6" />
          </svg>
        </button>
        <!-- 指示器 -->
        <div class="carousel-dots">
          <button 
            v-for="(_, idx) in aboutImages" 
            :key="idx"
            class="dot"
            :class="{ active: currentIndex === idx }"
            @click="goTo(idx)"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import bgVideoSrc from '@/assets/images/section4.webm'

const baseUrl = 'https://pages-1327732770.cos.ap-guangzhou.myqcloud.com/about'
const imgVersion = 'v2' // 更新图片后修改此版本号
const aboutImages = [`${baseUrl}/5.jpg?${imgVersion}`, `${baseUrl}/6.jpg?${imgVersion}`]

const i18n = useI18nStore()
const t = (key, vars) => i18n.t(key, vars)

const isVisible = ref(false)
const currentIndex = ref(0)
let timer = null

const goTo = (idx) => {
  currentIndex.value = idx
  resetTimer()
}

const next = () => {
  currentIndex.value = (currentIndex.value + 1) % aboutImages.length
  resetTimer()
}

const resetTimer = () => {
  if (isVisible.value) startCarousel()
}

const startCarousel = () => {
  stopCarousel()
  timer = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % aboutImages.length
  }, 5000)
}

const stopCarousel = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

watch(isVisible, (val) => {
  if (val) startCarousel()
  else stopCarousel()
})

onBeforeUnmount(() => stopCarousel())

defineExpose({
  show() { isVisible.value = true },
  hide() { isVisible.value = false; stopCarousel() }
})
</script>

<style scoped>
.about-four {
  position: relative;
  min-height: 100vh;
  height: 100vh;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.bg-video {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
  background: #ffffff;
}

.bg-video__media {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.18;
}

.about-four-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 90px;
  padding: 80px 60px;
  max-width: 1400px;
  position: relative;
  z-index: 1;
}

/* 切换按钮 */
.carousel-btn {
  position: absolute;
  top: 50%;
  right: -72px;
  transform: translateY(-50%);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 10;
}

.carousel-btn svg {
  width: 24px;
  height: 24px;
  color: #111827;
}

.carousel-btn:hover {
  background: #111827;
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
}

.carousel-btn:hover svg { color: #ffffff; }

.carousel-btn:active {
  transform: translateY(-50%) scale(0.95);
}

/* 指示器 */
.carousel-dots {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 10;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.dot:hover { background: rgba(255, 255, 255, 0.9); }
.dot.active { background: #ffffff; transform: scale(1.2); }

/* 轮播动画 - 进入和离开都使用绝对定位避免布局抖动 */
.carousel-fade-enter-active,
.carousel-fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
  will-change: opacity, transform;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
.carousel-fade-enter-from { opacity: 0; transform: scale(1.02); }
.carousel-fade-leave-to { opacity: 0; transform: scale(0.98); }

/* 右侧轮播容器 */
.about-four-carousel {
  position: relative;
  width: 860px;
  height: 484px;
  flex-shrink: 0;
  background: rgba(243, 244, 246, 0.6);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
}

/* 图片始终使用绝对定位 */
.about-four-carousel img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  border-radius: 0;
}

/* 左侧文字 */
.about-four-text {
  flex: 1;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.about-four-title {
  font-size: 42px;
  font-weight: 600;
  color: #111827;
  margin: 0;
  margin-top: -120px;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.about-four-desc {
  font-size: 20px;
  line-height: 1.9;
  color: #374151;
  margin: 0;
  margin-top: 20px;
  max-width: 320px;
}

/* 入场动画 */
@keyframes revealFromLeft {
  0% { opacity: 0; transform: translateX(-60px); filter: blur(10px); }
  100% { opacity: 1; transform: translateX(0); filter: blur(0); }
}

@keyframes revealFromRight {
  0% { opacity: 0; transform: translateX(60px); filter: blur(10px); }
  100% { opacity: 1; transform: translateX(0); filter: blur(0); }
}

.reveal-left {
  opacity: 0;
  transform: translateX(-60px);
  filter: blur(10px);
  will-change: opacity, transform, filter;
}

.reveal-left.animate {
  animation: revealFromLeft 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.reveal-right {
  opacity: 0;
  transform: translateX(60px);
  filter: blur(10px);
  will-change: opacity, transform, filter;
}

.reveal-right.animate {
  animation: revealFromRight 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  animation-delay: 0.3s;
}

@media (max-width: 900px) {
  .about-four {
    height: auto;
    min-height: 100svh;
  }

  .about-four-content {
    width: 100%;
    max-width: 680px;
    padding: 96px 20px 72px;
    flex-direction: column;
    align-items: stretch;
    gap: 32px;
  }

  .about-four-text {
    width: 100%;
    max-width: none;
    gap: 14px;
  }

  .about-four-title {
    margin-top: 0;
    font-size: clamp(34px, 10vw, 44px);
  }

  .about-four-desc {
    max-width: none;
    margin-top: 0;
    font-size: 16px;
    line-height: 1.7;
  }

  .about-four-carousel {
    width: 100%;
    height: auto;
    aspect-ratio: 16 / 9;
  }

  .carousel-btn {
    right: 8px;
    width: 44px;
    height: 44px;
    background: rgba(255, 255, 255, 0.94);
  }
}

@media (prefers-reduced-motion: reduce) {
  .reveal-left,
  .reveal-left.animate,
  .reveal-right,
  .reveal-right.animate {
    opacity: 1;
    animation: none;
    transform: none;
    filter: none;
  }
}
</style>
