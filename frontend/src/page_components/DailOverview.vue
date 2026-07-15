<template>
  <section
    id="dail-overview"
    ref="sectionRef"
    class="dail-overview"
    :class="{
      'dail-overview--visible': isVisible,
      'dail-overview--resetting': isResetting,
    }"
    :lang="i18n.locale"
    aria-labelledby="dail-overview-title"
  >
    <div class="overview-grid">
      <div class="overview-lead">
        <h2 id="dail-overview-title" class="overview-title">
          <span class="overview-title__line overview-title__line--first">
            <span class="overview-title__echo" aria-hidden="true">
              {{ t('dailOverview.titleLine1') }}
            </span>
            <span class="overview-title__text">
              {{ t('dailOverview.titleLine1') }}
            </span>
          </span>
          <span class="overview-title__line overview-title__line--second">
            <span class="overview-title__echo" aria-hidden="true">
              {{ t('dailOverview.titleLine2') }}
            </span>
            <span class="overview-title__text">
              {{ t('dailOverview.titleLine2') }}
            </span>
          </span>
        </h2>
      </div>

      <div class="overview-intro">
        <p>{{ t('dailOverview.intro') }}</p>
      </div>

      <div class="overview-verbs" :aria-label="t('dailOverview.verbAria')">
        <div
          v-for="(verb, index) in verbs"
          :key="verb"
          class="overview-verb"
          :style="{ '--verb-index': index }"
        >
          <span class="overview-verb__word">{{ verb }}</span>
        </div>
      </div>

      <div class="overview-close">
        <p>{{ t('dailOverview.statement') }}</p>
      </div>
    </div>

  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18nStore } from '@/stores/i18n'

const i18n = useI18nStore()
const sectionRef = ref(null)
const isVisible = ref(false)
const isResetting = ref(false)
const t = (key, vars) => i18n.t(key, vars)

const verbs = computed(() => [
  t('dailOverview.verb1'),
  t('dailOverview.verb2'),
  t('dailOverview.verb3'),
])

const ENTRY_THRESHOLD = 0.24
const TOP_RESET_Y = 8

let observer = null
let topCheckFrame = null

const resetAnimationAtTop = async () => {
  if (!isVisible.value || isResetting.value) return

  isResetting.value = true
  isVisible.value = false
  await nextTick()

  // Force the hidden state to settle without reverse animation while the section is offscreen.
  sectionRef.value?.getBoundingClientRect()
  isResetting.value = false
}

const checkTopReset = () => {
  if (window.scrollY <= TOP_RESET_Y) resetAnimationAtTop()
}

const requestTopReset = () => {
  if (topCheckFrame !== null) return

  topCheckFrame = window.requestAnimationFrame(() => {
    topCheckFrame = null
    checkTopReset()
  })
}

onMounted(() => {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  if (reduceMotion || !('IntersectionObserver' in window)) {
    isVisible.value = true
    return
  }

  observer = new IntersectionObserver(
    ([entry]) => {
      if (
        !entry?.isIntersecting
        || entry.intersectionRatio < ENTRY_THRESHOLD
        || window.scrollY <= TOP_RESET_Y
        || isResetting.value
      ) return

      isVisible.value = true
    },
    {
      threshold: [0, ENTRY_THRESHOLD],
      rootMargin: '0px 0px -8% 0px',
    },
  )

  if (sectionRef.value) observer.observe(sectionRef.value)
  window.addEventListener('scroll', requestTopReset, { passive: true })
  requestTopReset()
})

onBeforeUnmount(() => {
  observer?.disconnect()
  window.removeEventListener('scroll', requestTopReset)
  if (topCheckFrame !== null) window.cancelAnimationFrame(topCheckFrame)
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
  width: min(100%, 1640px);
  min-height: min(72svh, 760px);
  margin: 0 auto;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  grid-template-rows: auto 1fr;
  column-gap: clamp(18px, 2.5vw, 48px);
  row-gap: clamp(72px, 10vh, 126px);
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
  line-height: 0.96;
  letter-spacing: -0.068em;
  text-wrap: balance;
}

.overview-title__line {
  position: relative;
  display: block;
  padding: 0 0.08em 0.09em 0;
  overflow: hidden;
  perspective: 900px;
}

.overview-title__text,
.overview-title__echo {
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
  transition-delay: 0.2s;
}

.overview-title__line--second .overview-title__text {
  transition-delay: 0.36s;
}

.overview-title__echo {
  position: absolute;
  inset: 0.02em 0 auto;
  color: transparent;
  opacity: 0;
  -webkit-text-stroke: 1px rgba(9, 9, 9, 0.24);
  transform: translateY(112%) skewY(4deg);
}

.overview-intro {
  grid-column: 9 / -1;
  align-self: end;
  padding-bottom: 0.4em;
  opacity: 0;
  clip-path: inset(0 0 100% 0);
  transform: translateY(28px);
  transition: opacity 0.55s ease 0.72s, clip-path 0.9s cubic-bezier(0.22, 1, 0.36, 1) 0.66s,
    transform 0.9s cubic-bezier(0.22, 1, 0.36, 1) 0.66s;
}

.overview-intro p {
  max-width: 33ch;
  font-size: clamp(18px, 1.42vw, 25px);
  font-weight: 430;
  line-height: 1.45;
  letter-spacing: -0.025em;
}

.overview-verbs {
  display: grid;
  grid-column: 1 / span 6;
  align-self: end;
}

.overview-verb {
  display: grid;
  min-height: clamp(68px, 8vh, 92px);
  padding: 8px 0 10px;
  overflow: hidden;
  grid-template-columns: 1fr;
  align-items: end;
}

.overview-verb__word {
  font-size: clamp(38px, 4vw, 70px);
  font-weight: 500;
  line-height: 0.95;
  letter-spacing: -0.07em;
  opacity: 0;
  filter: blur(8px);
  transform: translateX(calc(-42px - var(--verb-index) * 12px)) skewX(-12deg);
  transition: opacity 0.45s ease calc(0.82s + var(--verb-index) * 0.12s),
    filter 0.8s ease calc(0.82s + var(--verb-index) * 0.12s),
    transform 0.9s cubic-bezier(0.16, 1, 0.3, 1) calc(0.82s + var(--verb-index) * 0.12s);
}

.overview-close {
  grid-column: 8 / -1;
  align-self: end;
  padding: clamp(28px, 4vw, 64px) 0 4px clamp(0px, 2vw, 34px);
  opacity: 0;
  transform: translateY(34px);
  transition: opacity 0.65s ease 1.18s, transform 1s cubic-bezier(0.22, 1, 0.36, 1) 1.12s;
}

.overview-close p {
  max-width: 20ch;
  font-size: clamp(27px, 2.7vw, 48px);
  font-weight: 470;
  line-height: 1.12;
  letter-spacing: -0.055em;
  text-wrap: balance;
}

.dail-overview--visible .overview-intro,
.dail-overview--visible .overview-close {
  opacity: 1;
  clip-path: inset(0);
  transform: translateY(0);
}

.dail-overview--visible .overview-title__text,
.dail-overview--visible .overview-verb__word {
  opacity: 1;
  filter: blur(0);
  transform: none;
}

.dail-overview--visible .overview-title__echo {
  animation: overview-title-echo 0.95s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.dail-overview--visible .overview-title__line--first .overview-title__echo {
  animation-delay: 0.14s;
}

.dail-overview--visible .overview-title__line--second .overview-title__echo {
  animation-delay: 0.3s;
}

.dail-overview--resetting .overview-intro,
.dail-overview--resetting .overview-close,
.dail-overview--resetting .overview-title__text,
.dail-overview--resetting .overview-title__echo,
.dail-overview--resetting .overview-verb__word {
  animation: none !important;
  transition: none !important;
}

@keyframes overview-title-echo {
  0% {
    opacity: 0;
    transform: translateY(112%) skewY(4deg);
  }
  38% {
    opacity: 0.52;
  }
  100% {
    opacity: 0;
    transform: translateY(-44%) skewY(-2deg);
  }
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
  .overview-verbs,
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
    padding-bottom: 0;
  }

  .overview-intro p {
    max-width: 34ch;
    font-size: clamp(15px, 4.15vw, 17px);
    line-height: 1.62;
  }

  .overview-verbs {
    width: 100%;
    margin-top: 34px;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
  }

  .overview-verb {
    min-height: 44px;
    padding: 0;
    grid-template-columns: 1fr;
    align-items: center;
  }

  .overview-verb__word {
    font-size: clamp(29px, 8.4vw, 38px);
    line-height: 1;
    letter-spacing: -0.06em;
  }

  .overview-close {
    margin-top: 42px;
    padding: 0;
  }

  .overview-close p {
    max-width: 20ch;
    font-size: clamp(26px, 7.2vw, 34px);
    line-height: 1.14;
    letter-spacing: -0.05em;
  }

  /* 手机端减少模糊和残影运算，并缩短错峰等待。 */
  .overview-title__echo {
    display: none;
  }

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

  .overview-verb__word {
    filter: none;
    transform: translateX(-24px);
    transition: opacity 0.32s ease calc(0.34s + var(--verb-index) * 0.08s),
      transform 0.58s cubic-bezier(0.16, 1, 0.3, 1)
        calc(0.34s + var(--verb-index) * 0.08s);
  }

  .overview-close {
    transition: opacity 0.38s ease 0.54s,
      transform 0.62s cubic-bezier(0.22, 1, 0.36, 1) 0.5s;
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
  .overview-verb__word {
    opacity: 1;
    clip-path: none;
    filter: none;
    transform: none;
    transition: none;
  }

  .overview-title__echo {
    display: none;
    animation: none;
  }
}
</style>
