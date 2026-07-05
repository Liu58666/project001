<template>
  <section class="about-page">
    <!-- 顶部背景视频 -->
    <video
      class="about-bg-video"
      autoplay
      loop
      muted
      playsinline
      :src="aboutVideo"
    ></video>

    <!-- 内容区域 -->
    <div class="about-content">
      <h1 class="about-title reveal-scale" :class="{ animate: isMounted }">
        {{ t('about.title') }}
      </h1>
      <p class="about-subtitle reveal-blur" :class="{ animate: isMounted }">
        {{ t('about.subtitle') }}
      </p>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, inject, watch } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import aboutVideo from '@/assets/images/about.mp4'

const i18n = useI18nStore()
const t = (key, vars) => i18n.t(key, vars)

const isMounted = ref(false)
const loaderFinished = inject('loaderFinished', ref(true))

watch(loaderFinished, (finished) => {
  if (finished) {
    document.body.offsetHeight
    setTimeout(() => {
      isMounted.value = true
    }, 300)
  }
}, { immediate: true })

onMounted(() => {
  if (loaderFinished.value) {
    document.body.offsetHeight
    setTimeout(() => {
      isMounted.value = true
    }, 300)
  }
})
</script>

<style scoped>
.about-page {
  position: relative;
  min-height: 100vh;
  background: #ffffff;
  overflow: hidden;
}

/* 背景视频 */
.about-bg-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
  filter: brightness(0.9);
}

/* 视频上方的渐变遮罩 */
.about-page::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0.5) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0.6) 100%
  );
  z-index: 1;
  pointer-events: none;
}

/* 内容区域 */
.about-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 90vh;
  padding: 120px 24px 80px;
  text-align: center;
}

/* 大标题 */
.about-title {
  font-size: 96px;
  line-height: 1.1;
  letter-spacing: -0.03em;
  font-weight: 600;
  color: #111827;
  margin: 0 0 24px;
}

/* 小标题 */
.about-subtitle {
  font-size: 18px;
  line-height: 1.7;
  color: #4b5563;
  max-width: 700px;
  margin-top: 20px;
}

/* ========== About 页面独特动画 ========== */

/* 大标题：缩放 + 淡入动画 */
@keyframes revealScale {
  0% {
    opacity: 0;
    transform: scale(0.85);
    filter: blur(8px);
  }
  60% {
    opacity: 1;
    filter: blur(0);
  }
  100% {
    opacity: 1;
    transform: scale(1);
    filter: blur(0);
  }
}

.reveal-scale {
  opacity: 0;
  transform: scale(0.85);
  filter: blur(8px);
  will-change: opacity, transform, filter;
}

.reveal-scale.animate {
  animation: revealScale 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* 小标题：模糊淡入 + 从下方滑入 */
@keyframes revealBlur {
  0% {
    opacity: 0;
    transform: translateY(30px);
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
  transform: translateY(30px);
  filter: blur(12px);
  will-change: opacity, transform, filter;
}

.reveal-blur.animate {
  animation: revealBlur 1s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
  animation-delay: 0.5s;
}
</style>
