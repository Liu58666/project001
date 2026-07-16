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

      <div class="overview-intro">
        <p>{{ t('dailOverview.intro') }}</p>
      </div>

      <ol class="overview-points" :aria-label="t('dailOverview.pointsAria')">
        <li
          v-for="(point, index) in points"
          :key="point.key"
          class="overview-point"
          :style="{ '--point-index': index }"
        >
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

const i18n = useI18nStore()
const sectionRef = ref(null)
const isVisible = ref(false)
const t = (key, vars) => i18n.t(key, vars)

const points = computed(() => [
  { key: t('dailOverview.point1Key'), desc: t('dailOverview.point1Desc') },
  { key: t('dailOverview.point2Key'), desc: t('dailOverview.point2Desc') },
  { key: t('dailOverview.point3Key'), desc: t('dailOverview.point3Desc') },
  { key: t('dailOverview.point4Key'), desc: t('dailOverview.point4Desc') },
])

const ENTRY_THRESHOLD = 0.24

let observer = null

const reveal = () => {
  isVisible.value = true
  observer?.disconnect()
  observer = null
}

onMounted(() => {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  if (reduceMotion || !('IntersectionObserver' in window)) {
    isVisible.value = true
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
  observer?.disconnect()
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
  grid-template-rows: auto auto auto;
  column-gap: clamp(18px, 2.5vw, 48px);
  row-gap: clamp(52px, 8vh, 104px);
}

.overview-lead {
  grid-column: 1 / span 8;
}

.overview-title {
  max-width: none;
  margin: 0;
  font: inherit;
  font-size: clamp(56px, 4.85vw, 94px);
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

.overview-intro {
  grid-column: 9 / -1;
  align-self: start;
  padding-top: 0.55em;
  opacity: 0;
  clip-path: inset(0 0 100% 0);
  transform: translateY(22px);
  transition: opacity 0.5s ease 0.34s,
    clip-path 0.85s cubic-bezier(0.22, 1, 0.36, 1) 0.3s,
    transform 0.85s cubic-bezier(0.22, 1, 0.36, 1) 0.3s;
}

.overview-intro p {
  max-width: 35ch;
  font-size: clamp(18px, 1.42vw, 25px);
  font-weight: 430;
  line-height: 1.5;
  letter-spacing: -0.022em;
}

.overview-points {
  grid-column: 1 / -1;
  display: grid;
  margin: 0;
  padding: 0;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  column-gap: clamp(20px, 3vw, 56px);
  list-style: none;
}

.overview-point {
  position: relative;
  display: grid;
  align-content: start;
  padding-top: clamp(16px, 1.5vw, 24px);
  row-gap: clamp(12px, 1.1vw, 18px);
}

.overview-point__num {
  font-size: clamp(13px, 0.95vw, 15px);
  font-weight: 520;
  letter-spacing: 0.04em;
  font-variant-numeric: tabular-nums;
  color: rgba(9, 9, 9, 0.42);
}

.overview-point__key {
  font-size: clamp(28px, 2.55vw, 46px);
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
  grid-column: 1 / -1;
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
  .overview-intro,
  .overview-points,
  .overview-close {
    grid-column: 1;
  }

  .overview-title {
    max-width: 100%;
    font-size: clamp(40px, 11.8vw, 54px);
    line-height: 0.96;
    letter-spacing: -0.07em;
  }

  .overview-intro {
    width: 100%;
    max-width: 34rem;
    margin-top: 28px;
    justify-self: start;
    padding-top: 0;
    padding-bottom: 0;
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
  .overview-point__desc {
    opacity: 1;
    clip-path: none;
    filter: none;
    transform: none;
    transition: none;
  }
}
</style>
