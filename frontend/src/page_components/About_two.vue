<template>
  <section class="about-two">
    <!-- 背景视频（不影响布局） -->
    <div class="bg-video" aria-hidden="true">
      <video class="bg-video__media" autoplay muted loop playsinline>
        <source :src="bgVideoSrc" type="video/webm" />
      </video>
    </div>
    <div class="about-two-content">
      <!-- 轮播图片区域 -->
      <div class="carousel reveal-scale" :class="{ animate: isVisible }">
        <!-- 左箭头 -->
        <button class="carousel-btn carousel-btn-prev" @click="prev" aria-label="Previous">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
        
        <transition name="carousel-fade" mode="out-in">
          <img 
            :key="currentIndex" 
            :src="aboutImages[currentIndex]" 
            :alt="`DAIL Tech ${currentIndex + 1}`" 
          />
        </transition>
        
        <!-- 右箭头 -->
        <button class="carousel-btn carousel-btn-next" @click="next" aria-label="Next">
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
      <!-- 文字区域 -->
      <p class="about-two-desc reveal-blur" :class="{ animate: isVisible }">
        {{ t('about.section2Desc') }}
      </p>
    </div>
  </section>
</template>

<script setup>
import { ref, onBeforeUnmount, watch } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import bgVideoSrc from '@/assets/images/section4.webm'

const baseUrl = 'https://pages-1327732770.cos.ap-guangzhou.myqcloud.com/about'
const imgVersion = 'v2' // 更新图片后修改此版本号
const aboutImages = [
  `${baseUrl}/1.jpg?${imgVersion}`,
  `${baseUrl}/2.jpg?${imgVersion}`,
  `${baseUrl}/3.jpg?${imgVersion}`
]

const i18n = useI18nStore()
const t = (key, vars) => i18n.t(key, vars)

const isVisible = ref(false)
const currentIndex = ref(0)
let timer = null

const goTo = (idx) => {
  currentIndex.value = idx
  resetTimer()
}

const prev = () => {
  currentIndex.value = (currentIndex.value - 1 + aboutImages.length) % aboutImages.length
  resetTimer()
}

const next = () => {
  currentIndex.value = (currentIndex.value + 1) % aboutImages.length
  resetTimer()
}

const resetTimer = () => {
  if (isVisible.value) {
    startCarousel()
  }
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
  if (val) {
    startCarousel()
  } else {
    stopCarousel()
  }
})

onBeforeUnmount(() => {
  stopCarousel()
})

defineExpose({
  show() {
    isVisible.value = true
  },
  hide() {
    isVisible.value = false
    stopCarousel()
  }
})
</script>

<style scoped>
.about-two {
  position: relative;
  min-height: 100vh;
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
}

.bg-video__media {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.18;
}

.about-two-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  padding: 80px 24px;
  max-width: 1200px;
  position: relative;
  z-index: 1;
}

/* 轮播区域 */
.carousel {
  position: relative;
  width: 900px;
  height: 600px;
}

.carousel img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

/* 左右切换按钮 */
.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  /* box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15); */
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
  transition: transform 0.3s ease;
}

.carousel-btn:hover {
  background: #111827;
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
}

.carousel-btn:hover svg {
  color: #ffffff;
}

.carousel-btn:active {
  transform: translateY(-50%) scale(0.95);
}

.carousel-btn-prev {
  left: -100px;
}

.carousel-btn-next {
  right: -100px;
}

/* 轮播指示器 */
.carousel-dots {
  position: absolute;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: none;
  background: #d1d5db;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
}

.dot:hover {
  background: #9ca3af;
}

.dot.active {
  background: #111827;
  transform: scale(1.2);
}

/* 轮播切换动画 */
.carousel-fade-enter-active,
.carousel-fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.carousel-fade-enter-from {
  opacity: 0;
  transform: scale(1.10);
}

.carousel-fade-leave-to {
  opacity: 0;
  transform: scale(0.98);
}

/* 文字区域 */
.about-two-desc {
  font-size: 20px;
  line-height: 1.8;
  color: #374151;
  text-align: center;
  max-width: 800px;
  margin-top: 20px;
}

/* ========== 动画 ========== */
@keyframes revealScale {
  0% {
    opacity: 0;
    transform: scale(0.9);
    filter: blur(8px);
  }
  100% {
    opacity: 1;
    transform: scale(1);
    filter: blur(0);
  }
}

.reveal-scale {
  opacity: 0;
  transform: scale(0.9);
  filter: blur(8px);
  will-change: opacity, transform, filter;
}

.reveal-scale.animate {
  animation: revealScale 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes revealBlur {
  0% {
    opacity: 0;
    transform: translateY(20px);
    filter: blur(12px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }
}

.reveal-blur {
  opacity: 0;
  transform: translateY(20px);
  filter: blur(12px);
  will-change: opacity, transform, filter;
}

.reveal-blur.animate {
  animation: revealBlur 1s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
  animation-delay: 0.4s;
}

@media (max-width: 900px) {
  .about-two {
    min-height: 100svh;
  }

  .about-two-content {
    width: 100%;
    max-width: 680px;
    gap: 40px;
    padding: 96px 20px 72px;
  }

  .carousel {
    width: 100%;
    height: auto;
    aspect-ratio: 3 / 2;
  }

  .carousel-btn {
    width: 44px;
    height: 44px;
    background: rgba(255, 255, 255, 0.94);
  }

  .carousel-btn-prev {
    left: 8px;
  }

  .carousel-btn-next {
    right: 8px;
  }

  .carousel-dots {
    bottom: -28px;
  }

  .about-two-desc {
    margin-top: 8px;
    font-size: 16px;
    line-height: 1.7;
  }
}

@media (prefers-reduced-motion: reduce) {
  .reveal-scale,
  .reveal-scale.animate,
  .reveal-blur,
  .reveal-blur.animate {
    opacity: 1;
    animation: none;
    transform: none;
    filter: none;
  }
}
</style>
