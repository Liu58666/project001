<template>
  <div
    ref="pageRef"
    :class="['technology-page', { 'technology-page--embedded': embedded }]"
  >
    <section
      ref="networkRef"
      class="network"
      :class="{
        'network--center-visible': centerVisible,
        'network--expanded': expansionStarted,
        'network--handoff-active': handoffActive,
      }"
      aria-labelledby="network-title"
      @transitionend="handleNetworkTransitionEnd"
    >
      <div class="network-copy">
        <h1 id="network-title">{{ t('technologyPage.mapTitle') }}</h1>
        <div class="network-support">
          <p>{{ t('technologyPage.mapInstruction') }}</p>
        </div>
      </div>

    </section>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18nStore } from '@/stores/i18n'

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
})

const embedded = props.embedded

const i18n = useI18nStore()
const pageRef = ref(null)
const networkRef = ref(null)
// 初始状态就保留中央黑框及其文案，扩散动画只负责打开周边区域。
const centerVisible = ref(true)
const expansionStarted = ref(false)
const expansionComplete = ref(false)
const expansionGateActive = ref(false)
const handoffActive = ref(false)
const t = (key, vars) => i18n.t(key, vars)
const EXPANSION_DELAY_MS = 120
const EXPANSION_FALLBACK_MS = 1380
const EXPANSION_TRIGGER_VIEWPORT_RATIO = 0.58
const HANDOFF_DURATION_MS = 960
const HANDOFF_SETTLE_MS = 620
const PINNED_BREAKPOINT = 901

let entryFrame = null
let expansionTimer = null
let completionTimer = null
let handoffFrame = null
let handoffReleaseTimer = null
let handoffInProgress = false
let hasAnimated = false
let inputListenersAttached = false
let interactionZoneActive = false
let lastScrollY = 0
let lastTouchY = null

const prefersReducedMotion = () => (
  window.matchMedia('(prefers-reduced-motion: reduce)').matches
)

const usesPinnedExperience = () => (
  embedded
  && window.matchMedia(`(min-width: ${PINNED_BREAKPOINT}px)`).matches
  && !prefersReducedMotion()
)

function clearNetworkTimers() {
  if (expansionTimer !== null) {
    window.clearTimeout(expansionTimer)
    expansionTimer = null
  }
  if (completionTimer !== null) {
    window.clearTimeout(completionTimer)
    completionTimer = null
  }
}

function setInputCapture(active) {
  if (active && !inputListenersAttached) {
    window.addEventListener('wheel', handleWheelSignal, { passive: false })
    window.addEventListener('keydown', handleKeySignal)
    window.addEventListener('touchstart', handleTouchStart, { passive: true })
    window.addEventListener('touchmove', handleTouchMove, { passive: false })
    window.addEventListener('touchend', handleTouchEnd, { passive: true })
    window.addEventListener('touchcancel', handleTouchEnd, { passive: true })
    inputListenersAttached = true
  } else if (!active && inputListenersAttached) {
    window.removeEventListener('wheel', handleWheelSignal)
    window.removeEventListener('keydown', handleKeySignal)
    window.removeEventListener('touchstart', handleTouchStart)
    window.removeEventListener('touchmove', handleTouchMove)
    window.removeEventListener('touchend', handleTouchEnd)
    window.removeEventListener('touchcancel', handleTouchEnd)
    lastTouchY = null
    inputListenersAttached = false
  }
}

function syncInputCapture() {
  const shouldCapture = usesPinnedExperience() && (
    interactionZoneActive
    || expansionGateActive.value
    || handoffInProgress
  )
  setInputCapture(shouldCapture)
}

function setExpansionGate(active) {
  expansionGateActive.value = active
  syncInputCapture()
}

function finishNetworkExpansion() {
  if (expansionComplete.value) return
  if (completionTimer !== null) {
    window.clearTimeout(completionTimer)
    completionTimer = null
  }
  expansionComplete.value = true
  setExpansionGate(false)
}

function resetNetworkAnimation() {
  clearNetworkTimers()
  hasAnimated = false
  interactionZoneActive = false
  // 回到页面顶部时只收回扩散层，保留首次打开时的中央黑色内容框。
  centerVisible.value = true
  expansionStarted.value = false
  expansionComplete.value = false
  handoffActive.value = false
  handoffInProgress = false
  if (handoffFrame !== null) {
    window.cancelAnimationFrame(handoffFrame)
    handoffFrame = null
  }
  if (handoffReleaseTimer !== null) {
    window.clearTimeout(handoffReleaseTimer)
    handoffReleaseTimer = null
  }
  setExpansionGate(false)
}

function startNetworkAnimation() {
  if (hasAnimated) return
  hasAnimated = true
  centerVisible.value = true
  expansionComplete.value = false
  // 扩散提前开始；只有真正进入整屏停驻位置且动画尚未完成时才锁住下滑。
  setExpansionGate(false)

  // 手机端不需要桌面的大面积扩散等待；进入区块时直接给出完整内容，
  // 避免短屏设备先看到一整屏空黑区域。
  const compactViewport = window.matchMedia(`(max-width: ${PINNED_BREAKPOINT - 1}px)`).matches
  if (prefersReducedMotion() || compactViewport) {
    expansionStarted.value = true
    expansionComplete.value = true
    setExpansionGate(false)
    return
  }

  expansionTimer = window.setTimeout(() => {
    expansionTimer = null
    expansionStarted.value = true
    // transitionend 是正常完成路径；这个计时器只在浏览器未派发事件时兜底解锁。
    completionTimer = window.setTimeout(finishNetworkExpansion, EXPANSION_FALLBACK_MS)
  }, EXPANSION_DELAY_MS)
}

function handleNetworkTransitionEnd(event) {
  if (event.target !== networkRef.value) return
  if (!String(event.propertyName).includes('clip-path')) return
  if (!expansionStarted.value || expansionComplete.value) return
  finishNetworkExpansion()
}

function updateInteractionZone(rect, viewportHeight) {
  interactionZoneActive = usesPinnedExperience()
    && rect.top <= 1
    && rect.bottom >= viewportHeight - 1

  const shouldGateExpansion = interactionZoneActive
    && hasAnimated
    && !expansionComplete.value
  if (expansionGateActive.value !== shouldGateExpansion) {
    setExpansionGate(shouldGateExpansion)
  } else {
    syncInputCapture()
  }
}

function checkNetworkEntry() {
  if (!pageRef.value || !networkRef.value) return

  const currentScrollY = window.scrollY
  const scrollDelta = currentScrollY - lastScrollY
  lastScrollY = currentScrollY

  const rect = pageRef.value.getBoundingClientRect()
  const viewportHeight = window.innerHeight || 1
  const returnedToPreviousSection = scrollDelta < -1 && rect.top > 1
  const themeSwitchLine = document.querySelector('.nav')?.getBoundingClientRect().height
    || (window.innerWidth <= 900 ? 68 : 80)

  if (embedded) {
    document.body.classList.toggle(
      'technology-theme-active',
      rect.top <= themeSwitchLine && rect.bottom > 0,
    )
  }

  if (
    handoffActive.value
    && !handoffInProgress
    && scrollDelta < -1
    && rect.bottom > 0
  ) {
    handoffActive.value = false
  }

  if (embedded && (currentScrollY <= 8 || returnedToPreviousSection)) {
    if (hasAnimated) resetNetworkAnimation()
    else {
      interactionZoneActive = false
      syncInputCapture()
    }
    return
  }

  const pinnedExperience = usesPinnedExperience()
  if (!pinnedExperience) {
    interactionZoneActive = false
    if (expansionGateActive.value) finishNetworkExpansion()
  }

  updateInteractionZone(rect, viewportHeight)

  if (hasAnimated) return
  if (!embedded) {
    startNetworkAnimation()
    return
  }

  const expansionTriggerLine = pinnedExperience
    ? viewportHeight * EXPANSION_TRIGGER_VIEWPORT_RATIO
    : viewportHeight * 0.5
  if (rect.top <= expansionTriggerLine && rect.bottom > 0) startNetworkAnimation()
}

function requestEntryCheck() {
  if (entryFrame !== null) return
  entryFrame = window.requestAnimationFrame(() => {
    entryFrame = null
    checkNetworkEntry()
  })
}

function preventForwardInput(event) {
  if (event.cancelable) event.preventDefault()
}

function startHandoff() {
  if (
    handoffActive.value
    || handoffInProgress
    || !pageRef.value
  ) return

  const nextSection = pageRef.value.nextElementSibling
  if (!(nextSection instanceof HTMLElement)) return

  handoffActive.value = true
  handoffInProgress = true
  if (handoffReleaseTimer !== null) {
    window.clearTimeout(handoffReleaseTimer)
    handoffReleaseTimer = null
  }
  syncInputCapture()

  const startY = window.scrollY
  const targetY = startY + nextSection.getBoundingClientRect().top
  const distance = targetY - startY
  let startTime = null

  const animateHandoff = (timestamp) => {
    if (startTime === null) startTime = timestamp
    const progress = Math.min(1, (timestamp - startTime) / HANDOFF_DURATION_MS)
    const easedProgress = progress < 0.5
      ? 4 * progress * progress * progress
      : 1 - Math.pow(-2 * progress + 2, 3) / 2

    window.scrollTo(0, startY + distance * easedProgress)

    if (progress < 1) {
      handoffFrame = window.requestAnimationFrame(animateHandoff)
      return
    }

    handoffFrame = null
    window.scrollTo(0, targetY)
    handoffReleaseTimer = window.setTimeout(() => {
      handoffReleaseTimer = null
      handoffInProgress = false
      syncInputCapture()
    }, HANDOFF_SETTLE_MS)
  }

  handoffFrame = window.requestAnimationFrame(animateHandoff)
}

function handleForwardIntent(event) {
  if (expansionGateActive.value || handoffInProgress) {
    preventForwardInput(event)
    return true
  }

  if (
    usesPinnedExperience()
    && interactionZoneActive
    && expansionComplete.value
    && !handoffActive.value
  ) {
    preventForwardInput(event)
    startHandoff()
    return true
  }

  return false
}

function handleWheelSignal(event) {
  if (event.deltaY <= 0 || event.ctrlKey) return

  handleForwardIntent(event)
}

function handleKeySignal(event) {
  const target = event.target
  if (
    target instanceof HTMLElement
    && (target.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName))
  ) return

  const isForwardSpace = event.key === ' ' && !event.shiftKey
  const isForwardKey = isForwardSpace || ['ArrowDown', 'PageDown', 'End'].includes(event.key)
  if (!isForwardKey) return
  if (isForwardSpace && target instanceof HTMLButtonElement) return

  handleForwardIntent(event)
}

function handleTouchStart(event) {
  lastTouchY = event.touches.length === 1
    ? event.touches[0].clientY
    : null
}

function handleTouchMove(event) {
  if (expansionGateActive.value) {
    preventForwardInput(event)
    return
  }

  if (event.touches.length !== 1) {
    lastTouchY = null
    return
  }

  const currentTouchY = event.touches[0].clientY
  if (lastTouchY === null) {
    lastTouchY = currentTouchY
    return
  }

  const forwardDistance = lastTouchY - currentTouchY
  lastTouchY = currentTouchY
  if (forwardDistance > 0) handleForwardIntent(event)
}

function handleTouchEnd(event) {
  lastTouchY = event.touches.length === 1
    ? event.touches[0].clientY
    : null
}

onMounted(() => {
  lastScrollY = window.scrollY
  window.addEventListener('scroll', requestEntryCheck, { passive: true })
  window.addEventListener('resize', requestEntryCheck, { passive: true })
  requestEntryCheck()
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', requestEntryCheck)
  window.removeEventListener('resize', requestEntryCheck)
  if (entryFrame !== null) window.cancelAnimationFrame(entryFrame)
  if (handoffFrame !== null) window.cancelAnimationFrame(handoffFrame)
  if (handoffReleaseTimer !== null) window.clearTimeout(handoffReleaseTimer)
  clearNetworkTimers()
  expansionGateActive.value = false
  handoffInProgress = false
  interactionZoneActive = false
  setInputCapture(false)
  document.body.classList.remove('technology-theme-active')
})
</script>

<style scoped>
.technology-page {
  min-width: 0;
  min-height: 100svh;
  padding-top: 80px;
  background: #ffffff;
}

.technology-page--embedded {
  position: relative;
  display: grid;
  min-height: 100svh;
  margin: 0;
  padding-top: 0;
  padding-block: 0;
  border: 0;
  background: #ffffff;
  place-items: center;
  box-sizing: border-box;
}

.technology-page--embedded::after {
  content: '';
  position: absolute;
  z-index: 3;
  right: 0;
  bottom: -2px;
  left: 0;
  height: 4px;
  background: #000000;
  pointer-events: none;
}

.technology-page--embedded .network {
  width: 100%;
  min-height: 100svh;
  margin-inline: auto;
  border-radius: 0;
  clip-path: inset(
    max(0px, calc((100svh - 430px) / 2))
    19%
    round 28px
  );
  transition: clip-path 1.2s cubic-bezier(0.22, 1, 0.36, 1);
}

.technology-page--embedded .network.network--expanded {
  clip-path: inset(0 round 0);
}

.network {
  position: relative;
  min-height: calc(100svh - 80px);
  overflow: hidden;
  background: #000000;
  color: #faf9f5;
  isolation: isolate;
}

.network-lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 1;
  pointer-events: none;
  transition: opacity 0.72s cubic-bezier(0.22, 1, 0.36, 1);
}

.network-lines path {
  fill: none;
  stroke: rgba(250, 249, 245, 0.23);
  stroke-width: 1.2;
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  opacity: 0;
  vector-effect: non-scaling-stroke;
  transition: stroke-dashoffset 0.9s ease, opacity 0.55s ease;
}

.network--branches-visible .network-lines path {
  stroke-dashoffset: 0;
  opacity: 1;
}

.network-copy {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 2;
  width: min(46vw, 740px);
  text-align: center;
  opacity: 0;
  filter: blur(7px);
  transition: opacity 0.75s ease, filter 0.75s ease, transform 0.75s ease;
  transform: translate(-50%, calc(-50% + 18px));
  transform-origin: center;
  will-change: transform, opacity, filter;
}

.network--center-visible .network-copy {
  opacity: 1;
  filter: blur(0);
  transform: translate(-50%, -50%);
}

.network--handoff-active .network-copy,
.network--center-visible.network--handoff-active .network-copy {
  opacity: 0;
  filter: blur(8px);
  transform: translate(-50%, calc(-50% - 58px)) scale(0.955);
  transition-duration: 0.82s;
}

h1 {
  margin: 0;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(48px, 5vw, 82px);
  font-weight: 400;
  line-height: 0.98;
  letter-spacing: -0.055em;
}

.network-support {
  opacity: 1;
  transform: translateY(0);
  transition:
    opacity 0.72s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.72s cubic-bezier(0.22, 1, 0.36, 1);
}

.network-support > p {
  max-width: 650px;
  margin: 28px auto 0;
  color: rgba(250, 249, 245, 0.72);
  font-size: clamp(15px, 1.25vw, 19px);
  line-height: 1.6;
}

.network-topics {
  position: absolute;
  z-index: 2;
  inset: 0;
  opacity: 1;
  transform: translateY(0);
  pointer-events: none;
  transition:
    opacity 0.72s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.72s cubic-bezier(0.22, 1, 0.36, 1);
}

.network--branches-retreated .network-lines,
.network--branches-retreated .network-support,
.network--branches-retreated .network-topics {
  opacity: 0;
}

.network--branches-retreated .network-support,
.network--branches-retreated .network-topics {
  transform: translateY(-22px);
}

.topic {
  position: absolute;
  z-index: 2;
  display: grid;
  width: clamp(180px, 17vw, 280px);
  padding: 12px 0;
  grid-template-columns: auto 1fr auto;
  align-items: end;
  gap: 10px;
  border: 0;
  background: transparent;
  color: #ffffff;
  text-align: left;
  cursor: pointer;
  opacity: 0;
  transform: translateY(18px);
  pointer-events: none;
  transition: color 0.2s ease, opacity 0.6s ease, transform 0.6s ease;
}

.network--branches-visible .topic {
  opacity: 1;
  transform: translateY(0);
}

.network--branches-interactive .topic {
  pointer-events: auto;
}

.network--branches-visible .topic--2 { transition-delay: 0.08s; }
.network--branches-visible .topic--3 { transition-delay: 0.16s; }
.network--branches-visible .topic--4 { transition-delay: 0.24s; }

.topic:hover,
.topic:focus-visible,
.topic--active {
  color: #faf9f5;
  outline: none;
}

.topic--1 { top: 28%; left: 7%; }
.topic--2 { top: 17%; right: 8%; }
.topic--3 { bottom: 17%; left: 11%; }
.topic--4 { right: 9%; bottom: 12%; }

.topic-number {
  align-self: start;
  color: rgba(250, 249, 245, 0.38);
  font-size: 10px;
  letter-spacing: 0.12em;
}

.topic-name {
  color: #ffffff;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(22px, 2.3vw, 38px);
  line-height: 1;
}

.topic-arrow {
  font-size: 14px;
}

@media (min-width: 901px) {
  .technology-page--embedded {
    display: block;
    min-height: 155svh;
  }

  .technology-page--embedded .network {
    position: sticky;
    top: 0;
    height: 100svh;
  }
}

@media (max-width: 900px) {
  .technology-page {
    padding-top: 68px;
  }

  .technology-page--embedded {
    display: block;
    min-height: 0;
    padding-top: 0;
    padding-block: 0;
  }

  .technology-page--embedded .network {
    width: 100%;
    min-height: 0;
    height: auto;
    border-radius: 0;
    clip-path: none;
    transition: none;
  }

  .technology-page--embedded .network.network--expanded {
    clip-path: inset(0 round 0);
  }

  .network {
    display: flex;
    min-height: 100svh;
    padding: clamp(82px, 11svh, 112px) 18px 38px;
    flex-direction: column;
    box-sizing: border-box;
  }

  .network-lines {
    display: none;
  }

  .network-copy {
    position: relative;
    top: auto;
    left: auto;
    width: min(100%, 440px);
    margin: 0 auto;
    order: 1;
    text-align: center;
    transform: translateY(14px);
  }

  .network-topics {
    position: relative;
    inset: auto;
    display: grid;
    width: min(100%, 440px);
    margin: clamp(72px, 10svh, 92px) auto 0;
    order: 2;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    transform: none;
  }

  .network--center-visible .network-copy {
    transform: translateY(0);
  }

  .network-support > p {
    max-width: 31ch;
    margin: 16px auto 0;
    font-size: clamp(12px, 3.4vw, 15px);
    line-height: 1.5;
  }

  h1 {
    max-width: 11ch;
    margin: 0 auto;
    font-size: clamp(36px, 10.4vw, 52px);
    line-height: 0.98;
  }

  .topic,
  .topic--1,
  .topic--2,
  .topic--3,
  .topic--4 {
    position: relative;
    inset: auto;
    width: auto;
    min-width: 0;
    min-height: 82px;
    margin: 0;
    padding: 12px;
    grid-template-columns: 1fr auto;
    grid-template-rows: auto 1fr;
    align-items: start;
    gap: 8px 6px;
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.035);
    transform: translateY(10px);
    transition: color 0.2s ease, opacity 0.3s ease, transform 0.3s ease;
  }

  .network-topics::before,
  .network-topics::after,
  .topic::before {
    content: '';
    position: absolute;
    background: rgba(250, 249, 245, 0.26);
    pointer-events: none;
  }

  .network-topics::before {
    left: 50%;
    top: -58px;
    width: 1px;
    height: 38px;
  }

  .network-topics::after {
    top: -20px;
    left: 25%;
    right: 25%;
    height: 1px;
  }

  .topic::before {
    left: 50%;
    top: -20px;
    width: 1px;
    height: 20px;
  }

  .topic--3::before,
  .topic--4::before {
    top: -15px;
    height: 15px;
  }

  .topic-name {
    grid-column: 1 / -1;
    grid-row: 2;
    align-self: end;
    font-size: clamp(17px, 5vw, 22px);
    line-height: 1.05;
  }

  .topic-number {
    grid-column: 1;
    grid-row: 1;
    font-size: 9px;
  }

  .topic-arrow {
    grid-column: 2;
    grid-row: 1;
    font-size: 12px;
  }

  .network--branches-visible .topic--2 {
    transition-delay: 0.03s;
  }

  .network--branches-visible .topic--3 {
    transition-delay: 0.06s;
  }

  .network--branches-visible .topic--4 {
    transition-delay: 0.09s;
  }

}

@media (max-width: 420px) and (max-height: 720px) {
  .network {
    padding: 74px 16px 26px;
  }

  .network-copy {
    width: 100%;
  }

  h1 {
    font-size: clamp(30px, 9.2vw, 38px);
  }

  .network-support > p {
    margin-top: 12px;
    font-size: 11px;
  }

  .network-topics {
    margin-top: 58px;
    gap: 12px;
  }

  .topic,
  .topic--1,
  .topic--2,
  .topic--3,
  .topic--4 {
    min-height: 68px;
    padding: 10px;
  }

  .topic-name {
    font-size: clamp(15px, 4.8vw, 18px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .topic,
  .network-lines,
  .network-topics,
  .network-support {
    transition: none;
  }

  .network-copy,
  .topic {
    opacity: 1;
    filter: none;
    transform: none;
  }

  .technology-page--embedded .network {
    position: relative;
    top: auto;
    width: 100%;
    min-height: 100svh;
    height: auto;
    border-radius: 0;
    clip-path: inset(0 round 0);
    transition: none;
  }

  .technology-page--embedded {
    min-height: 100svh;
  }

  .network-lines path {
    stroke-dashoffset: 0;
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) and (max-width: 900px) {
  .technology-page--embedded,
  .technology-page--embedded .network {
    min-height: 0;
    height: auto;
  }
}
</style>

<style>
.nav,
.nav.scrolled {
  transition:
    background-color 0.28s ease,
    box-shadow 0.28s ease,
    backdrop-filter 0.28s ease;
}

.nav .logo {
  transition:
    filter 0.32s ease,
    transform 0.3s ease;
}

.nav .menu-link,
.nav .mobile-language-toggle,
.nav .btn-12,
.nav .wave-group .input,
.nav .wave-group .label,
.nav .wave-group .bar::before,
.nav .wave-group .bar::after,
.nav .login-icon,
.nav .login-icon img,
.nav .user-avatar,
.nav .menu-toggle span {
  transition-duration: 0.32s;
  transition-timing-function: ease;
}

body.technology-theme-active .nav,
body.technology-theme-active .nav.scrolled {
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
}

body.technology-theme-active .nav .logo {
  filter: invert(1) grayscale(1) brightness(1.8);
}

body.technology-theme-active .nav .menu-link,
body.technology-theme-active .nav .mobile-language-toggle {
  color: rgba(255, 255, 255, 0.82);
}

body.technology-theme-active .nav .btn-12 {
  background-color: #ffffff;
  color: #050505;
}

body.technology-theme-active .nav .wave-group .input {
  color: #ffffff;
  border-bottom-color: rgba(255, 255, 255, 0.72);
}

body.technology-theme-active .nav .wave-group .label {
  color: rgba(255, 255, 255, 0.7);
}

body.technology-theme-active .nav .wave-group .bar::before,
body.technology-theme-active .nav .wave-group .bar::after {
  background: #ffffff;
}

body.technology-theme-active .nav .login-icon {
  border-color: rgba(255, 255, 255, 0.88);
}

body.technology-theme-active .nav .login-icon:not(.login-icon--has-photo) img {
  filter: invert(1);
}

body.technology-theme-active .nav .user-avatar {
  color: #ffffff;
}

body.technology-theme-active .nav .menu-toggle span {
  background: #ffffff;
}

@media (max-width: 900px) {
  body.technology-theme-active .nav,
  body.technology-theme-active .nav.scrolled {
    background: transparent;
    box-shadow: none;
    backdrop-filter: none;
  }

  body.technology-theme-active .nav:has(.menu--open),
  body.technology-theme-active .nav.scrolled:has(.menu--open) {
    background: rgba(255, 255, 255, 0.98);
    box-shadow: 0 1px 0 rgba(15, 23, 42, 0.08);
  }

  body.technology-theme-active .nav:has(.menu--open) .logo {
    filter: none;
  }

  body.technology-theme-active .nav:has(.menu--open) .mobile-language-toggle {
    color: rgba(17, 24, 39, 0.68);
  }

  body.technology-theme-active .nav:has(.menu--open) .login-icon {
    border-color: #111827;
  }

  body.technology-theme-active .nav:has(.menu--open) .menu-toggle span {
    background: #111827;
  }
}

@media (prefers-reduced-motion: reduce) {
  .nav,
  .nav *,
  .nav *::before,
  .nav *::after {
    transition-duration: 0.01ms !important;
  }
}
</style>
