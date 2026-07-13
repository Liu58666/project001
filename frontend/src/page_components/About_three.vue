<template>
  <section class="about-three">
    <!-- 背景视频（不影响布局） -->
    <div class="bg-video" aria-hidden="true">
      <video class="bg-video__media" autoplay muted loop playsinline>
        <source :src="bgVideoSrc" type="video/mp4" />
      </video>
    </div>
    <div class="about-three-content">
      <!-- 左侧图片 -->
      <div class="about-three-image reveal-left" :class="{ animate: isVisible }">
        <img :src="aboutImage" alt="DAIL Tech Journey" />
      </div>
      <!-- 右侧文字 -->
      <div class="about-three-text reveal-right" :class="{ animate: isVisible }">
        <h2 class="about-three-title">{{ t('about.section3Title') }}</h2>
        <p class="about-three-desc">{{ t('about.section3Desc') }}</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import bgVideoSrc from '@/assets/images/about.mp4'

const aboutImage = 'https://pages-1327732770.cos.ap-guangzhou.myqcloud.com/about/4.jpg?v2'

const i18n = useI18nStore()
const t = (key, vars) => i18n.t(key, vars)

const isVisible = ref(false)

defineExpose({
  show() {
    isVisible.value = true
  },
  hide() {
    isVisible.value = false
  }
})
</script>

<style scoped>
.about-three {
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

.about-three-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 120px;
  padding: 80px 60px;
  max-width: 1400px;
  position: relative;
  z-index: 1;
}

/* 左侧图片 */
.about-three-image {
  flex: 1.8;
  max-width: 1200px;
}

.about-three-image img {
  width: 100%;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
}

/* 右侧文字 */
.about-three-text {
  flex: 0.8;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: flex-start;
  text-align: left;
  margin-left: 0px;
}

.about-three-title {
  font-size: 42px;
  font-weight: 600;
  color: #111827;
  margin: 0;
  margin-top: -120px;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.about-three-desc {
  font-size: 20px;
  line-height: 1.9;
  color: #374151;
  margin: 0;
  margin-top: 20px;
  max-width: 320px;
}

/* ========== 动画 ========== */
@keyframes revealFromLeft {
  0% {
    opacity: 0;
    transform: translateX(-60px);
    filter: blur(10px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
    filter: blur(0);
  }
}

@keyframes revealFromRight {
  0% {
    opacity: 0;
    transform: translateX(60px);
    filter: blur(10px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
    filter: blur(0);
  }
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
  .about-three {
    min-height: 100svh;
  }

  .about-three-content {
    width: 100%;
    max-width: 680px;
    padding: 96px 20px 72px;
    flex-direction: column;
    align-items: stretch;
    gap: 32px;
  }

  .about-three-image,
  .about-three-text {
    width: 100%;
    max-width: none;
  }

  .about-three-text {
    gap: 14px;
  }

  .about-three-title {
    margin-top: 0;
    font-size: clamp(34px, 10vw, 44px);
  }

  .about-three-desc {
    max-width: none;
    margin-top: 0;
    font-size: 16px;
    line-height: 1.7;
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
