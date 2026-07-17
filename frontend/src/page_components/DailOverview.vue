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

        <div class="overview-close">
          <p>{{ t('dailOverview.statement') }}</p>
        </div>
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
            'is-user-active': isInteractive && isUserControlling && activePoint === index,
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

      <nav
        class="overview-links"
        :aria-label="t('dailOverview.linksAria')"
        @mouseleave="activeOverviewLink = 0"
      >
        <RouterLink
          v-for="(link, index) in overviewLinks"
          :key="link.to"
          :to="link.to"
          class="overview-link"
          :class="{ 'is-active': activeOverviewLink === index }"
          :style="{ '--card-image': `url(${link.bg})` }"
          @mouseenter="activeOverviewLink = index"
          @focus="activeOverviewLink = index"
        >
          <span class="overview-link__content">
            <span class="overview-link__heading">
              <span class="overview-link__title">{{ link.label }}</span>
              <span class="overview-link__arrow" aria-hidden="true">
                <svg
                  v-for="arrowIndex in 3"
                  :key="arrowIndex"
                  class="overview-link__arrow-icon"
                  viewBox="0 0 1024 1024"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M697.91129336 988.38337432c-12.56723411 0-24.06944838-5.21859722-34.40014083-15.44278768-141.22163074-140.47611687-282.4432615-281.05873572-423.66489226-421.74785654l-7.02913093-7.02913092c-9.79818253-9.79818253-15.33628569-24.49545633-15.12328173-40.47075392 0.10650198-15.22978371 5.64460515-29.18154361 15.01677972-38.23421225 143.03216448-138.02657124 285.85132499-276.26614644 428.77698749-414.29271767 10.33069243-10.01118649 21.9394087-15.12328173 34.50664282-15.12328173 21.40689878 0 43.34630748 15.86879561 52.18597215 37.70170233 4.68608729 11.71521823 9.37217459 34.6131448-12.78023806 56.02004356l-150.59380537 145.5882121c-77.00093441 74.44488681-154.00186884 148.78327162-230.89630125 223.22815843l-7.13563292 6.92262895L503.43867061 661.52878549c77.95945226 77.63994631 155.91890453 155.17339065 233.87835682 232.70683501 15.97529761 15.97529761 20.44838092 36.63668249 12.03472418 56.87205943-9.05266863 21.9394087-30.24656345 37.27569439-51.44045825 37.27569439z"
                    fill="currentColor"
                  />
                </svg>
              </span>
            </span>
            <span class="overview-link__desc">{{ link.desc }}</span>
          </span>
        </RouterLink>
      </nav>
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
import colorBgOne from '@/assets/images/color_bg/one.png'
import colorBgTwo from '@/assets/images/color_bg/two.png'
import colorBgThree from '@/assets/images/color_bg/three.png'

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

const overviewLinks = computed(() => [
  {
    label: t('dailOverview.linkTechnology'),
    desc: t('dailOverview.linkTechnologyDesc'),
    bg: colorBgOne,
    to: '/technology',
  },
  {
    label: t('dailOverview.linkCases'),
    desc: t('dailOverview.linkCasesDesc'),
    bg: colorBgTwo,
    to: '/news',
  },
  {
    label: t('dailOverview.linkTeam'),
    desc: t('dailOverview.linkTeamDesc'),
    bg: colorBgThree,
    to: '/team',
  },
])

const ENTRY_THRESHOLD = 0.24
// 与首页 Main.vue 首屏轮播保持一致。
const CAROUSEL_DURATION = 4000
const CAROUSEL_STEP_MS = 40
const POINT_COUNT = 4

const activePoint = ref(0)
const activeOverviewLink = ref(0)
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
  padding: clamp(140px, 16vh, 180px) 24px clamp(72px, 9vh, 96px);
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
  width: min(100%, 1500px);
  margin: 0 auto;
  padding-inline: clamp(20px, 5vw, 40px);
  grid-template-columns: repeat(12, minmax(0, 1fr));
  grid-template-rows: auto auto;
  column-gap: 40px;
  row-gap: clamp(24px, 3.2vh, 36px);
  box-sizing: border-box;
}

/* 64 开：左区（标题 + 关键点）占约 6，右区（展示图/说明 + 理念句）占约 4。 */
.overview-lead {
  grid-column: 1 / span 6;
  grid-row: 1;
  align-self: center;
}

.overview-display {
  grid-column: 7 / -1;
  grid-row: 1;
  align-self: center;
}

.overview-points {
  grid-column: 1 / span 6;
  grid-row: 2;
}

.overview-links {
  grid-column: 7 / -1;
  grid-row: 2;
  align-self: stretch;
}

.overview-title {
  max-width: none;
  margin: 0;
  font: inherit;
  font-size: clamp(36px, 3.4vw, 64px);
  font-weight: 500;
  line-height: 1;
  letter-spacing: -0.055em;
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
  overflow: hidden;
  border-radius: 10px;
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
  border-radius: 10px;
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
  column-gap: clamp(14px, 1.6vw, 28px);
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
  opacity: 0.56;
}

.overview-point__num {
  font-size: 12px;
  font-weight: 400;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-variant-numeric: tabular-nums;
  color: #6b7280;
}

.overview-point.is-active .overview-point__num {
  color: #000000;
}

.overview-point.is-active .overview-point__key,
.overview-point.is-active .overview-point__desc {
  color: #000000;
}

.overview-point.is-user-active .overview-point__line-inner {
  width: 100% !important;
  background: #000000;
}

.overview-point__key {
  font-size: clamp(18px, 1.65vw, 30px);
  font-weight: 530;
  line-height: 1;
  letter-spacing: -0.045em;
}

.overview-point__desc {
  max-width: 22ch;
  margin: 0;
  font-size: clamp(12px, 0.86vw, 15px);
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

.overview-links {
  display: grid;
  opacity: 0;
  transform: translateY(20px);
  transition:
    opacity 0.55s ease 0.88s,
    transform 0.72s cubic-bezier(0.16, 1, 0.3, 1) 0.84s;
}

.overview-link {
  position: relative;
  display: grid;
  min-width: 0;
  padding: 0 clamp(4px, 0.6vw, 10px);
  grid-template-columns: minmax(0, 1fr);
  align-items: center;
  justify-content: flex-end;
  gap: clamp(12px, 1.2vw, 20px);
  border: 1px solid rgba(64, 69, 79, 0.16);
  border-radius: 8px;
  background-color: #e5e7eb;
  background-image: var(--card-image);
  background-position: center;
  background-repeat: no-repeat;
  background-size: cover;
  color: rgba(9, 9, 9, 0.52);
  font-size: clamp(14px, 1.05vw, 17px);
  font-weight: 450;
  letter-spacing: -0.01em;
  line-height: 1.3;
  text-decoration: none;
  text-align: right;
  isolation: isolate;
  overflow: hidden;
  transition:
    color 0.28s ease,
    background-color 0.28s ease,
    border-color 0.28s ease;
}

.overview-link::before {
  content: '';
  position: absolute;
  z-index: 0;
  inset: 0;
  display: none;
  border-radius: inherit;
  background:
    radial-gradient(circle at 12% 18%, var(--card-color-a) 0%, transparent 58%),
    radial-gradient(circle at 88% 82%, var(--card-color-b) 0%, transparent 62%),
    linear-gradient(135deg, var(--card-color-a), var(--card-color-b));
  opacity: 0;
  transition: opacity 0.45s cubic-bezier(0.22, 1, 0.36, 1);
}

.overview-link::after {
  content: '';
  position: absolute;
  z-index: 0;
  inset: 0;
  border-radius: inherit;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.82' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='.72'/%3E%3C/svg%3E");
  background-size: 150px 150px;
  mix-blend-mode: soft-light;
  opacity: 0.16;
  pointer-events: none;
}

.overview-link__content {
  position: relative;
  z-index: 1;
  display: grid;
  min-width: 0;
  gap: 0;
  text-align: right;
}

.overview-link__heading {
  position: relative;
  z-index: 1;
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: flex-end;
  gap: clamp(5px, 0.55vw, 8px);
}

.overview-link__title {
  position: relative;
  z-index: 1;
  font: inherit;
  font-weight: 530;
}

.overview-link__desc {
  position: relative;
  z-index: 1;
  max-height: 0;
  overflow: hidden;
  color: rgba(9, 9, 9, 0.64);
  font-size: clamp(12px, 0.84vw, 14px);
  font-weight: 400;
  line-height: 1.5;
  opacity: 0;
  transform: translateY(8px);
  transition:
    max-height 0.5s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.3s ease,
    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}

.overview-link__arrow {
  position: relative;
  z-index: 1;
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  color: #000000;
  transition:
    color 0.28s ease,
    transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.overview-link__arrow-icon {
  display: block;
  width: 0.78em;
  height: 0.78em;
  transform: rotate(180deg);
}

.overview-link__arrow-icon + .overview-link__arrow-icon {
  margin-left: -0.39em;
}

.overview-link.is-active {
  background-image: var(--card-image);
  color: #111827;
}

.overview-link:not(.is-active) {
  color: #000000;
}

.overview-link.is-active::before {
  opacity: 1;
}

.overview-link:focus-visible {
  outline: 2px solid rgba(111, 119, 135, 0.42);
  outline-offset: 2px;
}

.overview-link.is-active .overview-link__content {
  gap: 6px;
  text-align: left;
}

.overview-link.is-active .overview-link__heading {
  justify-content: flex-start;
}

.overview-link.is-active .overview-link__title {
  font-size: clamp(17px, 4.2vw, 21px);
  font-weight: 500;
}

.overview-link.is-active .overview-link__desc {
  max-height: 72px;
  opacity: 1;
  transform: none;
}

.overview-link.is-active .overview-link__arrow {
  align-self: center;
  color: #000000;
  font-size: clamp(17px, 4.2vw, 21px);
  transform: none;
}

.overview-link:not(.is-active) .overview-link__arrow {
  font-size: clamp(11px, 2.8vw, 14px);
}

.overview-link:active .overview-link__arrow {
  transform: translate3d(4px, 0, 0) scale(0.94);
}

.overview-close {
  max-width: 42rem;
  margin-top: clamp(22px, 3vh, 34px);
  text-align: left;
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.55s ease 0.36s,
    transform 0.8s cubic-bezier(0.22, 1, 0.36, 1) 0.32s;
}

.overview-close p {
  max-width: 42ch;
  margin: 0;
  font-size: clamp(14px, 1vw, 17px);
  font-weight: 400;
  line-height: 1.65;
  letter-spacing: -0.01em;
  text-wrap: balance;
  color: #4b5563;
}

.dail-overview--visible .overview-intro,
.dail-overview--visible .overview-close,
.dail-overview--visible .overview-links {
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
  .overview-lead {
    position: relative;
    grid-column: 1 / span 5;
    top: calc(clamp(18px, 2.5vh, 28px) * -1);
  }

  .overview-title {
    width: 100%;
    font-size: clamp(32px, 3vw, 56px);
    transform: none;
  }

  .overview-points {
    position: static;
    width: 100%;
    height: clamp(180px, 21vh, 210px);
    justify-self: stretch;
    transform: none;
    display: flex;
    align-items: stretch;
    justify-content: flex-start;
    gap: 12px;
  }

  .overview-links {
    width: calc(100% + 40px);
    height: clamp(180px, 21vh, 210px);
    margin-inline-start: -40px;
    justify-self: start;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .overview-link {
    min-width: 0;
    min-height: 0;
    width: 100%;
    height: auto;
    padding: 0 clamp(14px, 1.4vw, 22px);
    flex: 1 1 0;
    grid-template-columns: minmax(0, 1fr);
    align-content: center;
    justify-items: stretch;
    gap: clamp(12px, 1.2vw, 20px);
    border: 1px solid rgba(64, 69, 79, 0.16);
    border-radius: 8px;
    background-color: #e5e7eb;
    background-image: var(--card-image);
    background-position: center;
    background-repeat: no-repeat;
    background-size: cover;
    color: rgba(9, 9, 9, 0.58);
    box-sizing: border-box;
    text-align: right;
    transition:
      flex-grow 0.65s cubic-bezier(0.22, 1, 0.36, 1),
      color 0.35s ease,
      background-color 0.35s ease,
      border-color 0.35s ease;
  }

  .overview-link__content {
    justify-items: end;
    text-align: right;
  }

  .overview-link__title {
    font-size: clamp(16px, 1.15vw, 21px);
    font-weight: 530;
    line-height: 1.15;
    white-space: nowrap;
    transition: font-size 0.5s cubic-bezier(0.22, 1, 0.36, 1);
  }

  .overview-link__arrow {
    position: static;
    align-self: center;
    color: #000000;
    font-size: clamp(16px, 1.15vw, 21px);
    opacity: 0.86;
    transform: none;
  }

  .overview-link:not(.is-active) .overview-link__arrow {
    font-size: clamp(11px, 0.78vw, 15px);
  }

  .overview-link.is-active {
    flex-grow: 2;
    align-content: center;
    justify-items: stretch;
    column-gap: clamp(10px, 1vw, 14px);
    row-gap: 7px;
    padding-top: clamp(16px, 2vh, 20px);
    padding-bottom: clamp(16px, 2vh, 20px);
    border-color: rgba(111, 119, 135, 0.18);
    color: #111827;
    text-align: left;
  }

  .overview-link.is-active .overview-link__content {
    display: grid;
    justify-items: stretch;
    gap: clamp(7px, 0.7vw, 10px);
    text-align: left;
  }

  .overview-link.is-active .overview-link__title {
    font-size: clamp(21px, 1.55vw, 28px);
    font-weight: 500;
  }

  .overview-link.is-active .overview-link__desc {
    max-height: 78px;
    color: rgba(17, 24, 39, 0.68);
    opacity: 1;
    transform: none;
  }

  .overview-link.is-active .overview-link__arrow {
    position: static;
    align-self: center;
    color: #000000;
    font-size: clamp(21px, 1.55vw, 28px);
    opacity: 1;
    transform: none;
  }

  .overview-point {
    min-width: 0;
    min-height: 0;
    height: 100%;
    padding: clamp(26px, 3vh, 34px) clamp(18px, 1.6vw, 26px)
      clamp(20px, 2.4vh, 28px);
    flex: 0 0 calc((100% - 36px) * 0.165);
    align-content: center;
    justify-items: center;
    gap: 0;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 8px;
    background: #121212;
    color: #ffffff;
    opacity: 1;
    box-sizing: border-box;
    container-type: inline-size;
    text-align: center;
    transition:
      flex-basis 0.72s cubic-bezier(0.22, 1, 0.36, 1),
      background-color 0.45s ease,
      border-color 0.45s ease,
      opacity 0.45s ease;
  }

  .overview-point.is-active {
    flex-basis: calc((100% - 36px) * 0.45);
    align-content: start;
    justify-items: stretch;
    gap: clamp(9px, 0.9vw, 13px);
    background: #000000;
    border-color: rgba(255, 255, 255, 0.2);
    text-align: left;
  }

  .overview-point.is-dim {
    opacity: 1;
  }

  .overview-point__line {
    position: relative;
    top: auto;
    left: auto;
    flex: 0 0 auto;
    background: rgba(255, 255, 255, 0.14);
    opacity: 1;
    transition: opacity 0.3s ease;
  }

  .overview-point:not(.is-active) .overview-point__line {
    opacity: 0;
  }

  .overview-point__line-inner {
    background: #ffffff;
  }

  .overview-point__key {
    overflow: hidden;
    color: #ffffff;
    white-space: nowrap;
    text-overflow: ellipsis;
    transition:
      opacity 0.45s ease,
      transform 0.55s cubic-bezier(0.22, 1, 0.36, 1),
      font-size 0.55s cubic-bezier(0.22, 1, 0.36, 1);
  }

  .overview-point.is-active .overview-point__key {
    font-size: clamp(20px, 1.65vw, 30px);
    color: #ffffff;
  }

  .overview-point:not(.is-active) {
    padding-right: clamp(10px, 1vw, 14px);
    padding-left: clamp(10px, 1vw, 14px);
  }

  .overview-point:not(.is-active) .overview-point__key {
    overflow: visible;
    /* 跟随折叠卡片自身宽度缩放，尽可能放大但不溢出。 */
    font-size: clamp(18px, 18cqi, 30px);
    white-space: nowrap;
    text-overflow: clip;
  }

  .dail-overview:lang(zh) .overview-point:not(.is-active) .overview-point__key {
    font-size: clamp(24px, 28cqi, 38px);
  }

  .overview-point.is-user-active .overview-point__line-inner {
    background: #ffffff;
  }

  .overview-point:not(.is-active) .overview-point__num,
  .overview-point:not(.is-active) .overview-point__desc {
    max-height: 0;
    margin: 0;
    overflow: hidden;
    opacity: 0;
    transform: translateY(10px);
    pointer-events: none;
  }

  .overview-point.is-active .overview-point__num {
    max-height: 24px;
    color: rgba(255, 255, 255, 0.68);
  }

  .overview-point.is-active .overview-point__desc {
    max-width: 36ch;
    max-height: 90px;
    color: rgba(255, 255, 255, 0.72);
  }

  .overview-point__num,
  .overview-point__desc {
    transition:
      max-height 0.55s cubic-bezier(0.22, 1, 0.36, 1),
      opacity 0.4s ease,
      transform 0.55s cubic-bezier(0.22, 1, 0.36, 1);
  }

  .dail-overview:lang(en) .overview-title {
    font-size: clamp(30px, 2.8vw, 52px);
    line-height: 0.98;
    letter-spacing: -0.055em;
  }

  .dail-overview:lang(en) .overview-title__line {
    white-space: nowrap;
  }

  /* 图片主体与左侧标题顶部呼应；理念句与左侧关键点标题行对齐。 */
  .overview-display {
    position: relative;
    width: calc(100% + clamp(120px, 8vw, 180px));
    grid-column: 6 / -1;
    inset-inline-start: calc(clamp(30px, 2.5vw, 48px) * -1);
    top: calc(clamp(44px, 5.5vh, 62px) * -1);
  }

  .dail-overview:lang(en) .overview-display {
    width: calc(100% + clamp(120px, 8vw, 180px));
    inset-inline-start: calc(clamp(30px, 2.5vw, 48px) * -1);
  }

  .dail-overview:lang(zh) .overview-title__line {
    white-space: nowrap;
  }

  .dail-overview:lang(zh) .overview-close p {
    max-width: none;
    white-space: nowrap;
  }

  .overview-close p {
    font-size: clamp(13px, 0.86vw, 15px);
  }
}

@media (max-width: 900px) {
  .dail-overview {
    min-height: auto;
    padding: 96px 20px 64px;
  }

  .overview-grid {
    min-height: 0;
    padding-inline: 0;
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    row-gap: 0;
  }

  .overview-lead,
  .overview-display,
  .overview-points,
  .overview-links,
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

  .overview-links {
    height: auto;
    margin-top: 34px;
    grid-template-rows: repeat(3, minmax(54px, auto));
  }

  .overview-link {
    min-height: 54px;
    padding-inline: 4px;
    font-size: 14px;
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
    margin-top: 24px;
    padding: 0;
    text-align: left;
  }

  .overview-close p {
    max-width: 34ch;
    font-size: clamp(14px, 4vw, 17px);
    line-height: 1.62;
    letter-spacing: -0.01em;
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
  .overview-display__img,
  .overview-links {
    opacity: 1;
    clip-path: none;
    filter: none;
    transform: none;
    transition: none;
  }

  .overview-point__line-inner {
    transition: none;
  }

  .overview-link,
  .overview-link__arrow {
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
