<template>
  <section
    id="dail-overview"
    ref="sectionRef"
    class="dail-overview"
    :class="{ 'dail-overview--visible': isVisible }"
    :lang="i18n.locale"
    aria-labelledby="dail-overview-title"
  >
    <div class="overview-grid">
      <div class="overview-lead">
        <h2 id="dail-overview-title" class="overview-title">
          <span class="overview-title__line overview-title__line--first">
            <span class="overview-title__text">
              {{ t('dailOverview.titleLine1') }}
            </span>
          </span>
          <span class="overview-title__line overview-title__line--second">
            <span class="overview-title__text">
              {{ t('dailOverview.titleLine2') }}
            </span>
          </span>
        </h2>
      </div>

      <div
        class="overview-display"
        :class="{ 'overview-display--active': isInteractive }"
      >
        <div class="overview-display__frame">
          <div class="overview-intro">
            <p>{{ t('dailOverview.intro') }}</p>
          </div>
          <div
            v-for="(point, index) in points"
            :key="point.key"
            class="overview-display__img"
            :class="{ 'is-active': isInteractive && activePoint === index }"
            :style="{ backgroundImage: `url(${point.img})` }"
            aria-hidden="true"
          ></div>
        </div>
      </div>

      <ol class="overview-points" :aria-label="t('dailOverview.pointsAria')">
        <li
          v-for="(point, index) in points"
          :key="point.key"
          class="overview-point"
          :class="{
            'is-active': isInteractive && activePoint === index,
            'is-dim': isInteractive && activePoint !== index,
          }"
          :style="{ '--point-index': index }"
          tabindex="0"
          @mouseenter="setActive(index)"
          @mouseleave="clearActive"
          @focusin="setActive(index)"
          @focusout="clearActive"
        >
          <span class="overview-point__line" aria-hidden="true">
            <span
              class="overview-point__line-inner"
              :style="{
                width: isInteractive && activePoint === index ? `${pointProgress}%` : '0%',
              }"
            ></span>
          </span>
          <span class="overview-point__num" aria-hidden="true">
            {{ String(index + 1).padStart(2, '0') }}
          </span>
          <span class="overview-point__key">{{ point.key }}</span>
          <p class="overview-point__desc">{{ point.desc }}</p>
        </li>
      </ol>

      <div class="overview-close">
        <p>{{ t('dailOverview.statement') }}</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import imgData from '@/assets/images/overview/data.png'
import imgModels from '@/assets/images/overview/models.png'
import imgAgents from '@/assets/images/overview/agents.png'
import imgPlatform from '@/assets/images/overview/platform.png'

const i18n = useI18nStore()
const sectionRef = ref(null)
const isVisible = ref(false)
const t = (key, vars) => i18n.t(key, vars)

const pointImages = [imgData, imgModels, imgAgents, imgPlatform]

const points = computed(() => [
  { key: t('dailOverview.point1Key'), desc: t('dailOverview.point1Desc'), img: pointImages[0] },
  { key: t('dailOverview.point2Key'), desc: t('dailOverview.point2Desc'), img: pointImages[1] },
  { key: t('dailOverview.point3Key'), desc: t('dailOverview.point3Desc'), img: pointImages[2] },
  { key: t('dailOverview.point4Key'), desc: t('dailOverview.point4Desc'), img: pointImages[3] },
])

const ENTRY_THRESHOLD = 0.24
// 与首页 Main.vue 首屏轮播保持一致。
const CAROUSEL_DURATION = 4000
const CAROUSEL_STEP_MS = 40
const POINT_COUNT = 4

const activePoint = ref(0)
const pointProgress = ref(0)
const isInteractive = ref(false)
const isUserControlling = ref(false)
const prefersReducedMotion = ref(false)

let carouselTimer = null

const stopCarousel = () => {
  if (carouselTimer === null) return
  window.clearInterval(carouselTimer)
  carouselTimer = null
}

const startCarousel = () => {
  stopCarousel()
  if (
    !isVisible.value ||
    !isInteractive.value ||
    isUserControlling.value ||
    prefersReducedMotion.value
  ) return

  const step = 100 / (CAROUSEL_DURATION / CAROUSEL_STEP_MS)
  carouselTimer = window.setInterval(() => {
    pointProgress.value += step
    if (pointProgress.value < 100) return
    pointProgress.value = 0
    activePoint.value = (activePoint.value + 1) % POINT_COUNT
  }, CAROUSEL_STEP_MS)
}

const setActive = (index) => {
  if (!isInteractive.value) return
  isUserControlling.value = true
  stopCarousel()
  activePoint.value = index
  pointProgress.value = prefersReducedMotion.value ? 100 : 0
}

const clearActive = () => {
  if (!isInteractive.value) return
  isUserControlling.value = false
  pointProgress.value = prefersReducedMotion.value ? 100 : 0
  startCarousel()
}

let observer = null
let desktopQuery = null
let reduceMotionQuery = null

const syncInteractive = (event) => {
  isInteractive.value = event.matches
  isUserControlling.value = false
  activePoint.value = 0
  pointProgress.value = prefersReducedMotion.value ? 100 : 0
  if (event.matches) startCarousel()
  else stopCarousel()
}

const syncReducedMotion = (event) => {
  prefersReducedMotion.value = event.matches
  pointProgress.value = event.matches ? 100 : 0
  if (event.matches) stopCarousel()
  else startCarousel()
}

const reveal = () => {
  isVisible.value = true
  observer?.disconnect()
  observer = null
  startCarousel()
}

onMounted(() => {
  desktopQuery = window.matchMedia('(min-width: 901px)')
  isInteractive.value = desktopQuery.matches
  desktopQuery.addEventListener('change', syncInteractive)

  reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  prefersReducedMotion.value = reduceMotionQuery.matches
  pointProgress.value = reduceMotionQuery.matches ? 100 : 0
  reduceMotionQuery.addEventListener('change', syncReducedMotion)

  if (prefersReducedMotion.value || !('IntersectionObserver' in window)) {
    isVisible.value = true
    startCarousel()
    return
  }

  observer = new IntersectionObserver(
    ([entry]) => {
      if (!entry?.isIntersecting || entry.intersectionRatio < ENTRY_THRESHOLD) return
      // Play the entrance once; keep everything visible afterwards.
      reveal()
    },
    {
      threshold: [0, ENTRY_THRESHOLD],
      rootMargin: '0px 0px -8% 0px',
    },
  )

  if (sectionRef.value) observer.observe(sectionRef.value)
})

onBeforeUnmount(() => {
  stopCarousel()
  observer?.disconnect()
  desktopQuery?.removeEventListener('change', syncInteractive)
  reduceMotionQuery?.removeEventListener('change', syncReducedMotion)
})
</script>

<style scoped>
.dail-overview {
  position: relative;
  display: grid;
  min-height: 100svh;
  padding: clamp(104px, 12vh, 150px) clamp(28px, 7vw, 132px)
    clamp(64px, 9vh, 108px);
  overflow: hidden;
  align-items: center;
  background: #ffffff;
  color: #090909;
  isolation: isolate;
}

.overview-grid {
  position: relative;
  z-index: 1;
  display: grid;
  width: min(100%, 1580px);
  margin: 0 auto;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  grid-template-rows: auto auto;
  column-gap: clamp(28px, 4vw, 84px);
  row-gap: clamp(52px, 8vh, 104px);
}

/* 64 开：左区（标题 + 关键点）占约 6，右区（展示图/说明 + 理念句）占约 4。 */
.overview-lead {
  grid-column: 1 / span 7;
  grid-row: 1;
  align-self: start;
}

.overview-display {
  grid-column: 8 / -1;
  grid-row: 1;
  align-self: start;
}

.overview-points {
  grid-column: 1 / span 7;
  grid-row: 2;
}

.overview-close {
  grid-column: 8 / -1;
  grid-row: 2;
}

.overview-title {
  max-width: none;
  margin: 0;
  font: inherit;
  font-size: clamp(52px, 4.55vw, 88px);
  font-weight: 520;
  line-height: 0.94;
  letter-spacing: -0.072em;
  text-wrap: balance;
}

.overview-title__line {
  position: relative;
  display: block;
  padding: 0.02em 0.08em 0.2em 0;
  overflow: hidden;
  perspective: 900px;
}

.overview-title__text {
  display: block;
  transform-origin: left bottom;
}

.overview-title__text {
  opacity: 0;
  filter: blur(12px);
  transform: translateY(112%) rotateX(-32deg) skewY(3deg);
  transition: opacity 0.35s ease, filter 0.95s cubic-bezier(0.22, 1, 0.36, 1),
    transform 1.05s cubic-bezier(0.16, 1, 0.3, 1);
}

.overview-title__line--first .overview-title__text {
  font-weight: 470;
  transition-delay: 0.06s;
}

.overview-title__line--second .overview-title__text {
  font-weight: 545;
  transition-delay: 0.2s;
}

/* 右上区：默认显示说明文字，hover 关键点时切换为对应展示图，比例固定不跳动。 */
.overview-display__frame {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
}

.overview-intro {
  position: absolute;
  inset: 0;
  padding-top: 0.35em;
  opacity: 0;
  clip-path: inset(0 0 100% 0);
  transform: translateY(22px);
  transition: opacity 0.5s ease 0.34s,
    clip-path 0.85s cubic-bezier(0.22, 1, 0.36, 1) 0.3s,
    transform 0.85s cubic-bezier(0.22, 1, 0.36, 1) 0.3s;
}

.overview-intro p {
  max-width: 35ch;
  margin: 0;
  font-size: clamp(18px, 1.42vw, 25px);
  font-weight: 430;
  line-height: 1.5;
  letter-spacing: -0.022em;
}

.overview-display__img {
  position: absolute;
  inset: 0;
  background-color: #ffffff;
  background-position: center;
  background-repeat: no-repeat;
  background-size: cover;
  border-radius: 2px;
  opacity: 0;
  filter: blur(10px);
  transform: scale(1.03);
  transition: opacity 0.6s cubic-bezier(0.22, 1, 0.36, 1),
    filter 0.7s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.9s cubic-bezier(0.16, 1, 0.3, 1);
  pointer-events: none;
}

.dail-overview:not(.dail-overview--visible) .overview-display__img {
  transform: translateY(30px) scale(1.025);
}

.dail-overview--visible .overview-display__img.is-active {
  opacity: 1;
  filter: blur(0);
  transform: translateY(0) scale(1);
}

/* hover 激活某个关键点时，说明文字克制地上移淡出。 */
.dail-overview--visible .overview-display--active .overview-intro {
  opacity: 0;
  clip-path: inset(0 0 0 0);
  transform: translateY(-10px);
  filter: blur(6px);
  transition: opacity 0.4s ease, transform 0.55s cubic-bezier(0.22, 1, 0.36, 1),
    filter 0.45s ease;
}

.overview-points {
  display: grid;
  margin: 0;
  padding: 0;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  column-gap: clamp(18px, 2vw, 40px);
  list-style: none;
}

.overview-point {
  position: relative;
  display: grid;
  align-content: start;
  padding-top: clamp(16px, 1.5vw, 24px);
  row-gap: clamp(12px, 1.1vw, 18px);
  cursor: default;
  outline: none;
  transition: opacity 0.45s ease;
}

/* 与首页首屏一致的 2px 自动播放进度条。 */
.overview-point__line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  overflow: hidden;
  background: #e5e7eb;
}

.overview-point__line-inner {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 0;
  background: #111827;
  transition: width 0.08s linear;
}

.overview-point.is-dim {
  opacity: 0.4;
}

.overview-point__num {
  font-size: 14px;
  font-weight: 400;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-variant-numeric: tabular-nums;
  color: #6b7280;
}

.overview-point.is-active .overview-point__num {
  color: #111827;
}

.overview-point__key {
  font-size: clamp(26px, 2.35vw, 42px);
  font-weight: 530;
  line-height: 1;
  letter-spacing: -0.045em;
}

.overview-point__desc {
  max-width: 22ch;
  margin: 0;
  font-size: clamp(14px, 1.02vw, 17px);
  font-weight: 420;
  line-height: 1.5;
  letter-spacing: -0.012em;
  color: rgba(9, 9, 9, 0.7);
}

.overview-point__num,
.overview-point__key,
.overview-point__desc {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.5s ease calc(0.5s + var(--point-index) * 0.1s),
    transform 0.72s cubic-bezier(0.16, 1, 0.3, 1)
      calc(0.5s + var(--point-index) * 0.1s);
}

.overview-close {
  align-self: end;
  justify-self: end;
  padding: 0;
  text-align: right;
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.6s ease 0.98s,
    transform 0.9s cubic-bezier(0.22, 1, 0.36, 1) 0.94s;
}

.overview-close p {
  max-width: 40ch;
  margin: 0;
  font-size: clamp(20px, 1.9vw, 32px);
  font-weight: 460;
  line-height: 1.24;
  letter-spacing: -0.03em;
  text-wrap: balance;
  color: rgba(9, 9, 9, 0.86);
}

.dail-overview--visible .overview-intro,
.dail-overview--visible .overview-close {
  opacity: 1;
  clip-path: inset(0);
  transform: translateY(0);
}

.dail-overview--visible .overview-point__num,
.dail-overview--visible .overview-point__key,
.dail-overview--visible .overview-point__desc {
  opacity: 1;
  transform: none;
}

.dail-overview--visible .overview-title__text {
  opacity: 1;
  filter: blur(0);
  transform: none;
}

@media (min-width: 901px) {
  .overview-title {
    --title-shift: clamp(5px, 0.5vw, 9px);
    width: calc(100% + clamp(72px, 5.5vw, 96px));
    transform: translateX(calc(var(--title-shift) * -1));
  }

  .dail-overview:lang(en) .overview-title {
    font-size: clamp(35px, 3.45vw, 66px);
    line-height: 0.98;
    letter-spacing: -0.055em;
  }

  .dail-overview:lang(en) .overview-title__line {
    white-space: nowrap;
  }

  /* 图片主体与左侧标题顶部呼应；理念句与左侧关键点标题行对齐。 */
  .overview-display {
    position: relative;
    inset-inline-start: clamp(22px, 2vw, 36px);
    top: calc(clamp(40px, 6vh, 56px) * -1);
  }

  .dail-overview:lang(en) .overview-display {
    width: calc(100% + clamp(64px, 4.5vw, 90px));
    inset-inline-start: calc(clamp(16px, 1.4vw, 26px) * -1);
  }

  .overview-close {
    position: relative;
    align-self: start;
    inset-inline-start: calc(clamp(12px, 1.2vw, 24px) * -1);
    top: 0;
    padding-top: calc(
      clamp(16px, 1.5vw, 24px) + 17px + clamp(12px, 1.1vw, 18px)
    );
  }

  .dail-overview:lang(zh) .overview-title__line {
    white-space: nowrap;
  }
}

@media (max-width: 900px) {
  .dail-overview {
    min-height: auto;
    padding: 96px 20px 64px;
  }

  .overview-grid {
    min-height: 0;
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    row-gap: 0;
  }

  .overview-lead,
  .overview-display,
  .overview-points,
  .overview-close {
    grid-column: 1;
    grid-row: auto;
  }

  .overview-title {
    max-width: 100%;
    font-size: clamp(40px, 11.8vw, 54px);
    line-height: 0.96;
    letter-spacing: -0.07em;
  }

  /* 移动端不启用 hover 图片切换，右上区仅保留说明文字，恢复自然流。 */
  .overview-display {
    width: 100%;
    max-width: 34rem;
    margin-top: 28px;
    justify-self: start;
  }

  .overview-display__frame {
    aspect-ratio: auto;
  }

  .overview-intro {
    position: static;
    inset: auto;
    padding-top: 0;
  }

  .overview-display__img {
    display: none;
  }

  .overview-intro p {
    max-width: 34ch;
    font-size: clamp(15px, 4.15vw, 17px);
    line-height: 1.62;
  }

  .overview-points {
    width: 100%;
    margin-top: 34px;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    column-gap: 18px;
    row-gap: 26px;
  }

  .overview-point {
    padding-top: 12px;
    row-gap: 8px;
  }

  .overview-point__num {
    font-size: 13px;
  }

  .overview-point__key {
    font-size: clamp(24px, 6.6vw, 32px);
  }

  .overview-point__desc {
    max-width: none;
    font-size: clamp(13px, 3.6vw, 15px);
    line-height: 1.5;
  }

  .overview-close {
    margin-top: 40px;
    padding: 0;
    justify-self: start;
    text-align: left;
  }

  .overview-close p {
    max-width: 26ch;
    font-size: clamp(20px, 5.6vw, 26px);
    line-height: 1.24;
    letter-spacing: -0.03em;
  }

  /* 手机端减少模糊运算，并缩短错峰等待。 */
  .overview-title__text {
    filter: none;
    transform: translateY(46%);
    transition: opacity 0.3s ease 0.08s,
      transform 0.58s cubic-bezier(0.16, 1, 0.3, 1) 0.08s;
  }

  .overview-title__line--first .overview-title__text {
    transition-delay: 0.08s;
  }

  .overview-title__line--second .overview-title__text {
    transition-delay: 0.16s;
  }

  .overview-intro {
    transition: opacity 0.35s ease 0.22s,
      clip-path 0.58s cubic-bezier(0.22, 1, 0.36, 1) 0.2s,
      transform 0.58s cubic-bezier(0.22, 1, 0.36, 1) 0.2s;
  }

  .overview-point__num,
  .overview-point__key,
  .overview-point__desc {
    transform: translateY(14px);
    transition: opacity 0.32s ease calc(0.3s + var(--point-index) * 0.08s),
      transform 0.55s cubic-bezier(0.16, 1, 0.3, 1)
        calc(0.3s + var(--point-index) * 0.08s);
  }

  .overview-close {
    transition: opacity 0.38s ease 0.62s,
      transform 0.62s cubic-bezier(0.22, 1, 0.36, 1) 0.58s;
  }
}

@media (max-width: 520px) {
  .overview-title {
    font-size: clamp(38px, 11.6vw, 48px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .overview-intro,
  .overview-close,
  .overview-title__text,
  .overview-point__num,
  .overview-point__key,
  .overview-point__desc,
  .overview-display__img {
    opacity: 1;
    clip-path: none;
    filter: none;
    transform: none;
    transition: none;
  }

  .overview-point__line-inner {
    transition: none;
  }

  .overview-display__img {
    opacity: 0;
  }

  .overview-display__img.is-active {
    opacity: 1;
  }
}
</style>
