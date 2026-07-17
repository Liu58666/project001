<template>
  <section
    id="aios-showcase"
    ref="sectionRef"
    class="aios-showcase"
    :class="{ 'aios-showcase--visible': isVisible }"
    :lang="i18n.locale"
    aria-labelledby="aios-showcase-title"
  >
    <div ref="stageRef" class="aios-stage">
      <div class="aios-inner">
        <div class="aios-copy">
          <p class="aios-eyebrow">{{ t('aiosShowcase.eyebrow') }}</p>
          <h2 id="aios-showcase-title" class="aios-title">
            <span>{{ t('aiosShowcase.titleLine1') }}</span>
            <span>{{ t('aiosShowcase.titleLine2') }}</span>
          </h2>
          <p class="aios-description">
            <span>{{ t('aiosShowcase.descriptionLine1') }}</span>
            <span>{{ t('aiosShowcase.descriptionLine2') }}</span>
          </p>
        </div>

        <div class="aios-visual" aria-hidden="true">
          <div class="aios-floor-light"></div>
          <div class="aios-contact-shadow"></div>
          <img
            :src="aiosImage"
            alt=""
            width="1024"
            height="614"
            loading="lazy"
            decoding="async"
          />
        </div>
      </div>

      <div class="aios-handoff-wash" aria-hidden="true"></div>
      <div class="aios-white-fill" aria-hidden="true"></div>
    </div>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import aiosImage from '@/assets/images/prod/AIOS.png'

const i18n = useI18nStore()
const t = (key) => i18n.t(key)

const sectionRef = ref(null)
const stageRef = ref(null)
const isVisible = ref(false)

let observer = null
let animationFrame = 0
let targetFrame = 0
let lastFrameTime = 0
let renderedProgress = 0
let targetProgress = 0
let sceneInitialized = false
let fixedTransitionFrame = 0
let fixedTransitionRunning = false
let fixedTransitionComplete = false
let lastTouchY = null

const SCRUB_RESPONSE_MS = 105
const PROGRESS_EPSILON = 0.00035
const HANDOFF_DURATION_MS = 1200

const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value))
const range = (value, start, end) => clamp((value - start) / (end - start))
const smooth = (value) => {
  const normalized = clamp(value)
  return normalized * normalized * normalized
    * (normalized * (normalized * 6 - 15) + 10)
}

const setSceneVariable = (name, value) => {
  stageRef.value?.style.setProperty(name, value)
}

const renderScene = (progress) => {
  const section = sectionRef.value
  if (!section) return

  const whiteProgress = smooth(range(progress, 0.04, 0.9))
  const contentExit = smooth(range(progress, 0.48, 0.78))
  const whiteFill = smooth(range(progress, 0.86, 0.995))
  const washY = 42 - whiteProgress * 48
  const washScaleX = 0.72 + whiteProgress * 0.3
  const washScaleY = 0.7 + whiteProgress * 0.35

  setSceneVariable('--aios-white-progress', whiteProgress.toFixed(4))
  setSceneVariable('--aios-content-exit', contentExit.toFixed(4))
  setSceneVariable('--aios-wash-y', `${washY.toFixed(2)}%`)
  setSceneVariable('--aios-wash-scale-x', washScaleX.toFixed(4))
  setSceneVariable('--aios-wash-scale-y', washScaleY.toFixed(4))
  setSceneVariable('--aios-white-fill', whiteFill.toFixed(4))

  const bounds = section.getBoundingClientRect()
  const navHeight = document.querySelector('.nav')?.getBoundingClientRect().height || 80
  const sectionIsVisible = bounds.top <= navHeight && bounds.bottom > navHeight
  document.body.classList.toggle(
    'aios-showcase-active',
    sectionIsVisible && whiteFill < 0.18,
  )
}

const animateScene = (timestamp) => {
  animationFrame = 0
  const deltaTime = lastFrameTime ? Math.min(48, timestamp - lastFrameTime) : 16
  lastFrameTime = timestamp
  const blend = 1 - Math.exp(-deltaTime / SCRUB_RESPONSE_MS)
  renderedProgress += (targetProgress - renderedProgress) * blend

  if (Math.abs(targetProgress - renderedProgress) <= PROGRESS_EPSILON) {
    renderedProgress = targetProgress
  }

  renderScene(renderedProgress)
  if (renderedProgress !== targetProgress) {
    animationFrame = window.requestAnimationFrame(animateScene)
  } else {
    lastFrameTime = 0
  }
}

const updateSceneTarget = (immediate = false) => {
  targetFrame = 0
  const section = sectionRef.value
  if (!section) return

  if (window.matchMedia('(max-width: 900px)').matches) {
    if (fixedTransitionFrame) window.cancelAnimationFrame(fixedTransitionFrame)
    fixedTransitionFrame = 0
    fixedTransitionRunning = false
    fixedTransitionComplete = false
    if (animationFrame) window.cancelAnimationFrame(animationFrame)
    animationFrame = 0
    lastFrameTime = 0
    sceneInitialized = false

    const bounds = section.getBoundingClientRect()
    const navHeight = document.querySelector('.nav')?.getBoundingClientRect().height || 68
    const navProgress = clamp((navHeight - bounds.top) / Math.max(1, bounds.height))
    const sectionIsVisible = bounds.top <= navHeight && bounds.bottom > navHeight
    document.body.classList.toggle(
      'aios-showcase-active',
      sectionIsVisible && navProgress < 0.72,
    )
    return
  }

  if (fixedTransitionRunning) return

  const bounds = section.getBoundingClientRect()
  const stageHeight = stageRef.value?.offsetHeight || window.innerHeight
  const scrollDistance = Math.max(1, section.offsetHeight - stageHeight)
  targetProgress = clamp(-bounds.top / scrollDistance)
  if (targetProgress <= 0.015) fixedTransitionComplete = false

  if (!sceneInitialized || immediate) {
    sceneInitialized = true
    renderedProgress = targetProgress
    renderScene(renderedProgress)
    return
  }

  if (!animationFrame) {
    lastFrameTime = 0
    animationFrame = window.requestAnimationFrame(animateScene)
  }
}

const requestSceneUpdate = () => {
  if (fixedTransitionRunning) return
  if (targetFrame) return
  targetFrame = window.requestAnimationFrame(() => updateSceneTarget())
}

const preventForwardInput = (event) => {
  if (event.cancelable) event.preventDefault()
}

const isFixedTransitionZoneActive = () => {
  const section = sectionRef.value
  if (!section || window.matchMedia('(max-width: 900px)').matches) return false

  const bounds = section.getBoundingClientRect()
  const navHeight = document.querySelector('.nav')?.getBoundingClientRect().height || 80
  const viewportHeight = window.innerHeight || 1
  const terminalY = section.offsetTop + Math.max(0, section.offsetHeight - viewportHeight)

  return (
    bounds.top <= navHeight + 2
    && bounds.bottom >= viewportHeight - 2
    && window.scrollY <= terminalY + 2
  )
}

const startFixedTransition = () => {
  if (
    fixedTransitionRunning
    || fixedTransitionComplete
    || window.matchMedia('(max-width: 900px)').matches
    || window.matchMedia('(prefers-reduced-motion: reduce)').matches
  ) return

  const section = sectionRef.value
  const stage = stageRef.value
  if (!section || !stage) return

  if (animationFrame) window.cancelAnimationFrame(animationFrame)
  if (targetFrame) window.cancelAnimationFrame(targetFrame)
  animationFrame = 0
  targetFrame = 0
  lastFrameTime = 0

  const startY = section.offsetTop
  const scrollDistance = Math.max(1, section.offsetHeight - stage.offsetHeight)
  const endY = startY + scrollDistance
  const startedAt = performance.now()

  fixedTransitionRunning = true
  sceneInitialized = true
  targetProgress = 0
  renderedProgress = 0
  window.scrollTo({ top: startY, left: 0, behavior: 'instant' })
  renderScene(0)

  const step = (timestamp) => {
    const elapsed = timestamp - startedAt
    const linearProgress = clamp(elapsed / HANDOFF_DURATION_MS)
    const easedProgress = smooth(linearProgress)

    targetProgress = easedProgress
    renderedProgress = easedProgress
    window.scrollTo({
      top: startY + scrollDistance * easedProgress,
      left: 0,
      behavior: 'instant',
    })
    renderScene(easedProgress)

    if (linearProgress < 1) {
      fixedTransitionFrame = window.requestAnimationFrame(step)
      return
    }

    fixedTransitionFrame = 0
    fixedTransitionRunning = false
    fixedTransitionComplete = true
    targetProgress = 1
    renderedProgress = 1
    window.scrollTo({ top: endY, left: 0, behavior: 'instant' })
    renderScene(1)
  }

  fixedTransitionFrame = window.requestAnimationFrame(step)
}

const handleForwardIntent = (event) => {
  if (
    window.matchMedia('(max-width: 900px)').matches
    || window.matchMedia('(prefers-reduced-motion: reduce)').matches
  ) return

  if (fixedTransitionRunning) {
    preventForwardInput(event)
    return
  }

  if (!fixedTransitionComplete && isFixedTransitionZoneActive()) {
    preventForwardInput(event)
    startFixedTransition()
  }
}

const handleWheel = (event) => {
  if (event.deltaY <= 0 || event.ctrlKey) return
  handleForwardIntent(event)
}

const handleKeyDown = (event) => {
  const target = event.target
  if (
    target instanceof HTMLElement
    && (target.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName))
  ) return

  const isForwardSpace = event.key === ' ' && !event.shiftKey
  if (!isForwardSpace && !['ArrowDown', 'PageDown', 'End'].includes(event.key)) return
  if (isForwardSpace && target instanceof HTMLButtonElement) return
  handleForwardIntent(event)
}

const handleTouchStart = (event) => {
  lastTouchY = event.touches.length === 1 ? event.touches[0].clientY : null
}

const handleTouchMove = (event) => {
  if (event.touches.length !== 1) {
    lastTouchY = null
    return
  }

  const currentTouchY = event.touches[0].clientY
  if (lastTouchY !== null && lastTouchY - currentTouchY > 0) {
    handleForwardIntent(event)
  }
  lastTouchY = currentTouchY
}

const handleTouchEnd = () => {
  lastTouchY = null
}

onMounted(async () => {
  const section = sectionRef.value
  if (!section) return

  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting && entry.intersectionRatio >= 0.18) {
        isVisible.value = true
      }
    },
    { threshold: [0, 0.18, 0.5] },
  )
  observer.observe(section)

  await nextTick()
  updateSceneTarget(true)
  window.addEventListener('scroll', requestSceneUpdate, { passive: true })
  window.addEventListener('resize', requestSceneUpdate, { passive: true })
  window.addEventListener('wheel', handleWheel, { passive: false })
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('touchstart', handleTouchStart, { passive: true })
  window.addEventListener('touchmove', handleTouchMove, { passive: false })
  window.addEventListener('touchend', handleTouchEnd, { passive: true })
  window.addEventListener('touchcancel', handleTouchEnd, { passive: true })
})

onBeforeUnmount(() => {
  observer?.disconnect()
  window.removeEventListener('scroll', requestSceneUpdate)
  window.removeEventListener('resize', requestSceneUpdate)
  window.removeEventListener('wheel', handleWheel)
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('touchstart', handleTouchStart)
  window.removeEventListener('touchmove', handleTouchMove)
  window.removeEventListener('touchend', handleTouchEnd)
  window.removeEventListener('touchcancel', handleTouchEnd)
  if (animationFrame) window.cancelAnimationFrame(animationFrame)
  if (targetFrame) window.cancelAnimationFrame(targetFrame)
  if (fixedTransitionFrame) window.cancelAnimationFrame(fixedTransitionFrame)
  document.body.classList.remove('aios-showcase-active')
})
</script>

<style scoped>
.aios-showcase {
  position: relative;
  z-index: 2;
  height: 150vh;
  height: 150svh;
  background: #000000;
  color: #ffffff;
}

.aios-stage {
  --aios-white-progress: 0;
  --aios-content-exit: 0;
  --aios-wash-y: 42%;
  --aios-wash-scale-x: 0.72;
  --aios-wash-scale-y: 0.7;
  --aios-white-fill: 0;
  position: sticky;
  top: 0;
  width: 100%;
  height: 100vh;
  height: 100svh;
  overflow: hidden;
  background: #000000;
  isolation: isolate;
}

.aios-inner {
  position: relative;
  z-index: 3;
  display: grid;
  width: min(100%, 1720px);
  min-height: 100vh;
  min-height: 100svh;
  margin: 0 auto;
  padding: clamp(110px, 14vh, 152px) clamp(34px, 5.5vw, 104px) clamp(64px, 8vh, 92px);
  grid-template-columns: minmax(520px, 1.08fr) minmax(360px, 0.92fr);
  align-items: center;
  gap: clamp(28px, 3vw, 58px);
  box-sizing: border-box;
  opacity: calc(1 - var(--aios-content-exit));
  filter: blur(calc(var(--aios-content-exit) * 12px));
  transform: translateY(calc(var(--aios-content-exit) * -3vh));
  will-change: opacity, filter, transform;
}

.aios-copy {
  position: relative;
  right: clamp(-72px, -3.5vw, -30px);
  z-index: 3;
  order: 2;
  width: min(42vw, 680px);
  justify-self: end;
  opacity: 0;
  transform: translate3d(0, 54px, 0);
  transition:
    opacity 0.8s ease 0.08s,
    transform 1s cubic-bezier(0.16, 1, 0.3, 1) 0.08s;
}

.aios-showcase--visible .aios-copy {
  opacity: 1;
  transform: translate3d(0, 0, 0);
}

.aios-eyebrow {
  margin: 0 0 clamp(24px, 3.5vh, 38px);
  color: rgba(226, 233, 243, 0.62);
  font-family: 'IBM Plex Mono', 'JetBrains Mono', ui-monospace, monospace;
  font-size: clamp(10px, 0.72vw, 12px);
  font-weight: 500;
  letter-spacing: 0.18em;
  line-height: 1.5;
  text-transform: uppercase;
}

.aios-title {
  margin: 0;
  font-size: clamp(48px, 4.7vw, 82px);
  font-weight: 430;
  letter-spacing: -0.06em;
  line-height: 1.02;
  text-wrap: balance;
}

.aios-title span,
.aios-description span {
  display: block;
}

.aios-description {
  max-width: 35rem;
  margin: clamp(28px, 4.5vh, 46px) 0 0;
  color: rgba(225, 234, 246, 0.7);
  font-size: clamp(15px, 1.12vw, 19px);
  line-height: 1.72;
}

.aios-visual {
  position: relative;
  left: clamp(-90px, -3vw, -40px);
  z-index: 2;
  order: 1;
  width: min(54vw, 980px);
  justify-self: start;
  opacity: 0;
  transform: translate3d(-70px, 38px, 0) scale(0.94);
  transform-origin: center;
  isolation: isolate;
  transition:
    opacity 0.9s ease 0.16s,
    transform 1.15s cubic-bezier(0.16, 1, 0.3, 1) 0.12s;
  will-change: transform, opacity;
}

.aios-showcase--visible .aios-visual {
  opacity: 1;
  transform: translate3d(0, 0, 0) scale(1);
}

.aios-visual::after {
  content: '';
  position: absolute;
  z-index: 0;
  top: 5%;
  right: 8%;
  bottom: 12%;
  left: 8%;
  background: radial-gradient(
    ellipse at 48% 68%,
    rgba(221, 235, 255, 0.17) 0%,
    rgba(93, 132, 188, 0.1) 34%,
    transparent 72%
  );
  filter: blur(42px);
  pointer-events: none;
}

.aios-floor-light {
  position: absolute;
  z-index: 1;
  left: 50%;
  bottom: -8%;
  width: 126%;
  height: 34%;
  border-radius: 50%;
  background: radial-gradient(
    ellipse at center,
    rgba(240, 247, 255, 0.62) 0%,
    rgba(187, 207, 235, 0.34) 24%,
    rgba(95, 128, 172, 0.17) 48%,
    rgba(27, 47, 75, 0.08) 64%,
    transparent 78%
  );
  filter: blur(18px);
  opacity: 0;
  transform: translateX(-50%) scaleX(0.78) scaleY(0.28);
  transform-origin: center;
  transition:
    opacity 1s ease 0.28s,
    transform 1.15s cubic-bezier(0.16, 1, 0.3, 1) 0.2s;
  pointer-events: none;
}

.aios-contact-shadow {
  position: absolute;
  z-index: 2;
  left: 50%;
  bottom: 1.5%;
  width: 48%;
  height: 9%;
  border-radius: 50%;
  background: radial-gradient(
    ellipse at center,
    rgba(0, 0, 0, 0.84) 0%,
    rgba(0, 0, 0, 0.52) 38%,
    rgba(0, 0, 0, 0.16) 66%,
    transparent 82%
  );
  filter: blur(10px);
  opacity: 0;
  transform: translateX(-50%) scaleX(0.72);
  transition:
    opacity 0.85s ease 0.34s,
    transform 1s cubic-bezier(0.16, 1, 0.3, 1) 0.26s;
  pointer-events: none;
}

.aios-showcase--visible .aios-floor-light {
  opacity: 0.72;
  transform: translateX(-50%) scaleX(1) scaleY(0.36);
}

.aios-showcase--visible .aios-contact-shadow {
  opacity: 0.82;
  transform: translateX(-50%) scaleX(1);
}

.aios-visual img {
  position: relative;
  z-index: 3;
  display: block;
  width: 100%;
  height: auto;
  filter: saturate(1.02) contrast(1.015);
  user-select: none;
}

.aios-handoff-wash {
  position: absolute;
  z-index: 5;
  left: 50%;
  top: -12%;
  width: 164vw;
  height: 150vh;
  background:
    radial-gradient(
      ellipse 56% 72% at 47% 84%,
      #ffffff 0%,
      rgba(255, 255, 255, 0.99) 32%,
      rgba(231, 247, 250, 0.96) 47%,
      rgba(147, 219, 230, 0.8) 61%,
      rgba(56, 151, 170, 0.48) 74%,
      rgba(9, 51, 61, 0.14) 86%,
      transparent 100%
    ),
    radial-gradient(
      ellipse 31% 54% at 53% 31%,
      rgba(84, 204, 226, 0.78) 0%,
      rgba(49, 159, 181, 0.5) 42%,
      rgba(16, 75, 89, 0.16) 70%,
      transparent 100%
    ),
    radial-gradient(
      ellipse 28% 43% at 31% 56%,
      rgba(74, 185, 204, 0.34) 0%,
      rgba(25, 99, 115, 0.16) 54%,
      transparent 100%
    ),
    radial-gradient(
      ellipse 32% 48% at 76% 59%,
      rgba(92, 192, 208, 0.3) 0%,
      rgba(22, 89, 103, 0.13) 56%,
      transparent 100%
    );
  filter: blur(34px);
  opacity: clamp(0, calc(var(--aios-white-progress) * 1.4), 1);
  transform:
    translateX(-50%)
    translateY(var(--aios-wash-y))
    scaleX(var(--aios-wash-scale-x))
    scaleY(var(--aios-wash-scale-y));
  transform-origin: center 78%;
  will-change: transform, opacity;
  pointer-events: none;
}

.aios-handoff-wash::before {
  content: '';
  position: absolute;
  z-index: 1;
  left: 15%;
  right: 10%;
  bottom: -8%;
  height: 58%;
  background: radial-gradient(
    ellipse 68% 100% at 49% 100%,
    rgba(255, 255, 255, 0.98) 0%,
    rgba(255, 255, 255, 0.86) 45%,
    rgba(228, 246, 249, 0.5) 70%,
    transparent 100%
  );
  filter: blur(42px);
  transform: translateX(-3%) skewX(-4deg);
  pointer-events: none;
}

.aios-handoff-wash::after {
  content: '';
  position: absolute;
  z-index: 2;
  left: -8%;
  right: -12%;
  bottom: -18%;
  height: 56%;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(255, 255, 255, 0.76) 34%,
    #ffffff 72%
  );
  filter: blur(36px);
  transform: rotate(-1.5deg);
  pointer-events: none;
}

.aios-white-fill {
  position: absolute;
  z-index: 7;
  inset: -2px;
  background: #ffffff;
  opacity: var(--aios-white-fill);
  pointer-events: none;
}

@media (min-width: 901px) {
  .aios-showcase:lang(zh) .aios-title {
    font-size: clamp(44px, 4vw, 68px);
  }

  .aios-showcase:lang(zh) .aios-title span {
    white-space: nowrap;
  }
}

@media (max-width: 900px) {
  .aios-showcase {
    --aios-mobile-handoff: linear-gradient(
      180deg,
      #000000 0%,
      #000000 74%,
      #111212 80%,
      #404242 86%,
      #8f9191 91%,
      #d6d7d7 96%,
      #ffffff 100%
    );
    height: auto;
    min-height: 122svh;
    margin-bottom: -1px;
    background: var(--aios-mobile-handoff);
  }

  .aios-stage {
    position: relative;
    top: auto;
    height: auto;
    min-height: 122svh;
    background: var(--aios-mobile-handoff);
  }

  .aios-inner {
    min-height: 100svh;
    padding: 102px 20px 54px;
    grid-template-columns: minmax(0, 1fr);
    align-content: center;
    gap: 42px;
    opacity: 1;
    filter: none;
    transform: none;
  }

  .aios-copy {
    right: auto;
    order: 1;
    width: min(100%, 620px);
    justify-self: start;
  }

  .aios-eyebrow {
    margin-bottom: 18px;
    font-size: 9px;
  }

  .aios-title {
    font-size: clamp(38px, 10.4vw, 54px);
    line-height: 1.04;
  }

  .aios-description {
    margin-top: 22px;
    font-size: clamp(13px, 3.7vw, 16px);
    line-height: 1.6;
  }

  .aios-visual {
    left: 0;
    order: 2;
    width: 118vw;
    max-width: none;
    margin-right: -24vw;
    justify-self: end;
    transform: translate3d(48px, 34px, 0) scale(0.96);
  }

  .aios-handoff-wash,
  .aios-white-fill {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .aios-copy,
  .aios-visual,
  .aios-showcase--visible .aios-copy,
  .aios-showcase--visible .aios-visual {
    opacity: 1;
    transform: none;
    transition: none;
  }

  .aios-floor-light,
  .aios-contact-shadow,
  .aios-showcase--visible .aios-floor-light,
  .aios-showcase--visible .aios-contact-shadow {
    opacity: 0.7;
    transition: none;
  }

  .aios-floor-light,
  .aios-showcase--visible .aios-floor-light {
    transform: translateX(-50%) scaleX(1) scaleY(0.36);
  }

  .aios-contact-shadow,
  .aios-showcase--visible .aios-contact-shadow {
    transform: translateX(-50%) scaleX(1);
  }
}
</style>

<style>
body.aios-showcase-active .nav,
body.aios-showcase-active .nav.scrolled {
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
}

body.aios-showcase-active .nav .logo {
  filter: invert(1) grayscale(1) brightness(1.8);
}

body.aios-showcase-active .nav .menu-link,
body.aios-showcase-active .nav .mobile-language-toggle {
  color: rgba(255, 255, 255, 0.82);
}

body.aios-showcase-active .nav .btn-12 {
  background-color: #ffffff;
  color: #050505;
}

body.aios-showcase-active .nav .login-icon {
  border-color: rgba(255, 255, 255, 0.88);
}

body.aios-showcase-active .nav .login-icon:not(.login-icon--has-photo) img {
  filter: invert(1);
}

body.aios-showcase-active .nav .user-avatar {
  color: #ffffff;
}

body.aios-showcase-active .nav .menu-toggle span {
  background: #ffffff;
}

@media (max-width: 900px) {
  body.aios-showcase-active .nav:has(.menu--open),
  body.aios-showcase-active .nav.scrolled:has(.menu--open) {
    background: rgba(255, 255, 255, 0.98);
  }

  body.aios-showcase-active .nav:has(.menu--open) .logo {
    filter: none;
  }

  body.aios-showcase-active .nav:has(.menu--open) .mobile-language-toggle {
    color: rgba(17, 24, 39, 0.68);
  }

  body.aios-showcase-active .nav:has(.menu--open) .login-icon {
    border-color: #111827;
  }

  body.aios-showcase-active .nav:has(.menu--open) .menu-toggle span {
    background: #111827;
  }
}
</style>
