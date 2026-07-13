<template>
    <section class="hero">
     <!-- 全屏背景视频 -->
     <video
       class="hero-bg-video"
       autoplay
       loop
       muted
       playsinline
       :src="bgVideo"
     ></video>
      <div class="hero-inner">
        <div class="hero-left">
          <newscard
            class="hero-newscard fade-in-up"
            :class="{ animate: isMounted }"
            @click="onNewsClick"
          />
          <h1 class="hero-title fade-in-up" :class="{ 'animate': isMounted }">
            {{ t('hero.titleLine1') }}
            <br />
            {{ t('hero.titleLine2') }}
          </h1>
          <p class="hero-subtitle fade-in-up" :class="{ 'animate': isMounted }">
          {{ t('hero.subtitle') }}
        </p>
          <div class="hero-actions fade-in-up" :class="{ 'animate': isMounted }">
            <button class="btn-primary" @click="router.push('/coming-soon')">
              {{ t('hero.tryDail') }}
              <span class="icon-arrow">↗</span>
            </button>
            <button class="btn-ghost" @click="router.push('/coming-soon')">
              {{ t('hero.downloadDail') }}
            </button>
          </div>
        </div>
  
        <div class="hero-right fade-in-up" :class="{ 'animate': isMounted }">
          <div class="hero-card">
          <div class="device-shot">
              <div class="device-screen">
              <Transition name="fade" mode="out-in">
                <img
                  :key="heroImages[activeIndex].src"
                  :src="heroImages[activeIndex].src"
                  class="device-img"
                  :style="{
                    ...heroImages[activeIndex].imgStyle,
                    objectPosition: heroImages[activeIndex].imgStyle.objectPosition || 'center center'
                  }"
                  :alt="t('hero.deviceAlt')"
                />
              </Transition>
            </div>
          </div>
          <Transition name="badge-fade" mode="out-in">
            <div 
              :key="activeIndex"
              class="apollo-badge" 
              :class="heroImages[activeIndex].badgeInfo.position === 'left' ? 'pos-left' : 'pos-right'"
            >
              <span class="badge-text">
                {{ t(heroImages[activeIndex].badgeInfoKey) }}
              </span>
            </div>
          </Transition>
          </div>
  
          <div class="hero-features fade-in-up" :class="{ 'animate': isMounted }">
            <div
              class="feature-item"
              :class="{ 'feature-item--active': activeIndex === 0 }"
            >
              <div class="feature-line">
                <div
                  class="feature-line-inner"
                  :style="{ width: activeIndex === 0 ? progress + '%' : '0%' }"
                ></div>
              </div>
              <div class="feature-index">01</div>
              <div class="feature-body">
              <div class="feature-title">{{ t('hero.feature1') }}</div>
            </div>
            </div>

            <div
              class="feature-item"
              :class="{ 'feature-item--active': activeIndex === 1 }"
            >
              <div class="feature-line">
                <div
                  class="feature-line-inner"
                  :style="{ width: activeIndex === 1 ? progress + '%' : '0%' }"
                ></div>
              </div>
              <div class="feature-index">02</div>
              <div class="feature-body">
                <div class="feature-title">
                {{ t('hero.feature2') }}
              </div>
              </div>
            </div>

            <div
              class="feature-item"
              :class="{ 'feature-item--active': activeIndex === 2 }"
            >
              <div class="feature-line">
                <div
                  class="feature-line-inner"
                  :style="{ width: activeIndex === 2 ? progress + '%' : '0%' }"
                ></div>
              </div>
              <div class="feature-index">03</div>
              <div class="feature-body">
                <div class="feature-title">
                {{ t('hero.feature3') }}
              </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </template>
  
  <script setup>
  import { ref, onMounted, onBeforeUnmount, inject, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import { useI18nStore } from '@/stores/i18n'
  import newscard from '@/components/newscard.vue'
  import hero1 from '@/assets/images/hero-1.png'
  import hero2 from '@/assets/images/hero-2.png'
  import hero3 from '@/assets/images/hero-3.png'

 // 背景视频（应用到整个 hero 区域）
 import bgVideo from '@/assets/images/section4.webm'

const i18n = useI18nStore()
const t = (key, vars) => i18n.t(key, vars)
const router = useRouter()

const heroImages = [
  {
    src: hero1,
    imgStyle: {
      width: '75%',
      height: 'auto',
      top: '100%',
      left: '50%',
      transform: 'translate(-52%, -50%)'
    },
    badgeInfoKey: 'hero.badge1',
    badgeInfo: { position: 'right' },
  },
  {
    src: hero2,
    imgStyle: {
      width: '90%',
      height: '90%',
      bottom: '0',
      left: '0',
      objectPosition: 'left top'
    },
    badgeInfoKey: 'hero.badge2',
    badgeInfo: { position: 'right' },
  },
  {
    src: hero3,
    imgStyle: {
      width: '90%',
      height: '90%',
      bottom: '0%',
      right: '0%',
      objectPosition: 'left top'
    },
    badgeInfoKey: 'hero.badge3',
    badgeInfo: { position: 'left' },
  },
]

const activeIndex = ref(0)
const progress = ref(0)
const TOTAL = 3
const isMounted = ref(false)

let timer = null

  const onNewsClick = () => {
    router.push('/news')
  }

  const startCarousel = () => {
    stopCarousel()
  const duration = 4000
  const stepMs = 40
    const step = 100 / (duration / stepMs)

    timer = window.setInterval(() => {
      progress.value += step
      if (progress.value >= 100) {
        progress.value = 0
        activeIndex.value = (activeIndex.value + 1) % TOTAL
      }
    }, stepMs)
  }

  const stopCarousel = () => {
    if (timer !== null) {
      clearInterval(timer)
      timer = null
    }
  }

  // 注入过场动画完成状态
  const loaderFinished = inject('loaderFinished', ref(false))
  
  // 监听过场动画完成状态
  watch(loaderFinished, (finished) => {
    if (finished) {
      // 强制让浏览器"意识到"初始状态
      document.body.offsetHeight;
      
      // 过场动画结束后，延迟300ms开始动画，让各个组件在1-2秒内逐渐浮现
      setTimeout(() => {
        isMounted.value = true
      }, 300)
      // 启动轮播
      startCarousel()
    }
  }, { immediate: true })
  
  onMounted(() => {
    // 如果过场动画已经完成（比如直接访问首页），立即开始动画
    if (loaderFinished.value) {
      document.body.offsetHeight;
      setTimeout(() => {
        isMounted.value = true
      }, 300)
      startCarousel()
    }
  })
  onBeforeUnmount(stopCarousel)
  </script>
  
  <style scoped>
/* ---------------- 基础布局 (保持不变) ---------------- */
  .hero {
  background: #ffffff;
  padding: 180px 24px 80px; /* 增加顶部留白以容纳绝对定位的导航栏 */
  position: relative;
  overflow: hidden;
}

/* 顶部整体变浅的遮罩（你原来的，不动） */
.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0.6),
    rgba(255, 255, 255, 0.35)
  );
  z-index: 1;
  pointer-events: none;
}

/* 新增：底部过渡 + 左右透明度变化的遮罩带 */
.hero::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;              /* 往下压 1px，避免出现一条细线 */
  height: 200px;             /* 比原来的 120px 高，过渡更长更柔和 */
  pointer-events: none;
  z-index: 1;

  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0) 0%,    /* 上方完全透明，保留视频颜色 */
    rgba(255, 255, 255, 0.6) 45%, /* 中间开始明显变浅 */
    rgba(255, 255, 255, 0.8) 75%, /* 中间开始明显变浅 */
    rgba(255, 255, 255, 1) 100%   /* 底部完全白色，和下方白底无缝衔接 */
  );

}

  /* 两个方向叠加：
     1. 从下往上渐变到透明（和下方白底融合）
     2. 从左到右透明度不同，制造颜色交错感
   */


.hero-bg-video {
  position: absolute;
  left: 0;
  right: 0;
  top: -10%;
  width: 100%;
  height: 140%;
  object-fit: cover;
  z-index: 0;
  filter: brightness(0.9);
}

  .hero-inner {
  max-width: 1500px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 40px;
  align-items: center;
  box-sizing: border-box;
  padding-inline: clamp(20px, 5vw, 40px);
  position: relative;
  z-index: 2;
  }

  .hero-left {
    display: flex;
    flex-direction: column;
    gap: 24px;
    margin-top: -80px; /* 左半部分整体上移*/
  }

  .hero-newscard {
    align-self: flex-start;
    margin-bottom: 18px; /* 拉开与下方标题的距离 */
  }
  /* ---------------- 动画样式修正 ---------------- */

  /* 1. 基础状态：强制隐藏并下移 */
  .fade-in-up {
    opacity: 0;
    transform: translateY(40px);
    will-change: opacity, transform;
    transition: opacity 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94),
                transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  }

  /* 2. 激活状态：回到正常位置并显示 */
  .fade-in-up.animate {
    opacity: 1;
    transform: translateY(0);
  }

  /* 3. 延迟控制 - 在1-2秒内依次浮现 */
  .hero-title.fade-in-up {
    transition-delay: 0s;
  }

  .hero-right.fade-in-up {
    transition-delay: 0.2s;
  }

  .hero-subtitle.fade-in-up {
    transition-delay: 0.4s;
  }

  .hero-actions.fade-in-up {
    transition-delay: 0.6s;
  }

  .hero-features.fade-in-up {
    transition-delay: 0.8s;
  }

  .hero-title {
    font-size: 56px;
    line-height: 1.2;
    letter-spacing: -0.03em;
    font-weight: 500;
    color: #111827;}
  
  .hero-subtitle {
    margin-top: 12px;
    max-width: 640px;
    font-size: 15px;
    line-height: 1.7;
    color: #4b5563;
  }
  
  /* 按钮区 */
  .hero-actions {
    display: flex;
    align-items: center;
    gap: 24px;
    margin-top: 28px;
  }
  
  .btn-primary {
  border-radius: 0.625em;
    padding: 12px 28px;
    font-size: 15px;
    font-weight: 500;
    border: 1px solid transparent;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease,
      transform 0.18s ease, border-color 0.18s ease;
    background: black;
    color: white;
    border: none;
    position: relative;
    z-index: 1;
    overflow: hidden;
    box-shadow: none;
  }
  
  .btn-primary:hover {
    color: black;
    transform: none;
    box-shadow: none;
  }
  
  .btn-primary:after {
    content: "";
    background: white;
    position: absolute;
    z-index: -1;
    left: -20%;
    right: -20%;
    top: 0;
    bottom: 0;
    transform: skewX(-45deg) scale(0, 1);
    transition: all 0.5s;
  }
  
  .btn-primary:hover:after {
    transform: skewX(-45deg) scale(1, 1);
}

.btn-ghost {
  position: relative;
  font-size: 15px;
  text-decoration: none;
  padding: 12px 28px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  border-radius: 0.625em;
  transition: all 0.2s;
  border: none;
  font-family: inherit;
  font-weight: 500;
  color: black;
  background-color: white;
  }
  
  .btn-ghost:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  }

  .btn-ghost:active {
    transform: translateY(-1px);
    box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
  }

  .btn-ghost::after {
    content: "";
    display: inline-block;
    height: 100%;
    width: 100%;
  border-radius: 0.625em;
    position: absolute;
    top: 0;
    left: 0;
    z-index: -1;
    transition: all 0.4s;
    background-color: #fff;
  }

  .btn-ghost:hover::after {
    transform: scaleX(1.4) scaleY(1.6);
    opacity: 0;
  }
  
  .icon-arrow {
    font-size: 13px;
  }
  
  
/* ---------------- 右侧核心逻辑 ---------------- */
  .hero-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
  }

  .hero-card {
    position: relative;
    width: 100%;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.5);
  padding: 0 0 0 0px;
}

/* 设备容器 - 最外层框架 */
  .device-shot {
  position: relative;
  background-color: transparent;
  isolation: isolate;
  height: 440px;
  border-radius: 24px 24px 0 0;
}

/* 新增：屏幕容器 - 负责圆角和裁剪图片 */
.device-screen {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 10px;
  overflow: hidden;
  z-index: 10;
}

/* --- 修改：图片样式 --- */
.device-img {
  position: absolute;
  object-fit: cover;
  will-change: opacity, transform;
  width: 100%;
  height: 100%;
}

/* 动画相关 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.6s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 保留绝对定位和层级即可，不去动 top/left/width/height */
.fade-leave-active {
  position: absolute;
  pointer-events: none;
  width: 100%;
  height: 100%;
}


/* Badge 浮现动画 */
.badge-fade-enter-active {
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.badge-fade-leave-active {
  transition: all 0.3s ease-in;
}

.badge-fade-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(-10px);
}

.badge-fade-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* Badge 基础样式 */
  .apollo-badge {
    position: absolute;
    top: 40px;
    width: 104px;
    height: 104px;
    border-radius: 26px;
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid transparent;
    box-shadow: 0 12px 22px rgba(15, 23, 42, 0.18);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 20;
    transition: all 0.8s cubic-bezier(0.25, 0.8, 0.25, 1);
    font-size: 14px;
    font-weight: 600;
    color: #111827;
    text-align: center;
    line-height: 1.2;
    padding: 10px;
}

/* 位置 1 - 右上角 (保持原样) */
.pos-right {
  right: 40px;
  left: auto;
  top: 20px;
}

/* 位置 2 - 左上角 */
.pos-left {
  right: auto;
  left: 40px;
  top: 20px;
}

/* 特性条 (保持不变) */
  .hero-features {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 32px;
    font-size: 13px;
  }
  
  .feature-item {
    display: flex;
    flex-direction: column;
    gap: 10px;
    color: #4b5563;
  }
  
  .feature-line {
    width: 100%;
    height: 2px;
  background: #e5e7eb;
    overflow: hidden;
    position: relative;
  }

  .feature-line-inner {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 0;
  background: #111827;
    transition: width 0.08s linear;
  }

  .feature-item--active .feature-title {
    color: #111827;
  }

  .feature-item--active .feature-index {
    color: #111827;
  }
  
  .feature-index {
    font-size: 14px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #6b7280;
  }
  
  .feature-title {
    font-size: 15px;
    font-weight: 500;
    color: #111827;
  }

@media (max-width: 900px) {
  .hero {
    padding: 112px 20px 64px;
  }

  .hero::after {
    height: 120px;
  }

  .hero-bg-video {
    top: 0;
    height: 100%;
  }

  .hero-inner {
    width: 100%;
    max-width: 680px;
    grid-template-columns: minmax(0, 1fr);
    gap: 48px;
    padding-inline: 0;
  }

  .hero-left {
    min-width: 0;
    gap: 16px;
    margin-top: 0;
  }

  .hero-newscard {
    max-width: 100%;
    margin-bottom: 4px;
  }

  .hero-title {
    max-width: 12ch;
    font-size: clamp(38px, 11vw, 52px);
    line-height: 1.06;
  }

  .hero-subtitle {
    margin-top: 4px;
    font-size: 16px;
    line-height: 1.65;
  }

  .hero-actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-top: 14px;
  }

  .btn-primary,
  .btn-ghost {
    min-height: 48px;
    padding: 12px 16px;
    justify-content: center;
  }

  .hero-right {
    min-width: 0;
    gap: 28px;
  }

  .device-shot {
    height: clamp(260px, 78vw, 360px);
  }

  .device-img {
    inset: 0 !important;
    width: 100% !important;
    height: 100% !important;
    transform: none !important;
    object-fit: cover !important;
    object-position: left top !important;
  }

  .apollo-badge {
    width: 88px;
    height: 88px;
    border-radius: 22px;
    font-size: 12px;
  }

  .pos-right {
    right: 14px;
    top: 14px;
  }

  .pos-left {
    left: 14px;
    top: 14px;
  }

  .hero-features {
    grid-template-columns: minmax(0, 1fr);
    gap: 16px;
  }

  .feature-item {
    display: grid;
    grid-template-columns: 42px minmax(0, 1fr);
    gap: 6px 12px;
  }

  .feature-line {
    grid-column: 1 / -1;
  }

  .feature-index {
    font-size: 13px;
  }

  .feature-title {
    font-size: 14px;
    line-height: 1.45;
  }
}

@media (max-width: 420px) {
  .hero-actions {
    grid-template-columns: minmax(0, 1fr);
  }
}
  
  </style>
