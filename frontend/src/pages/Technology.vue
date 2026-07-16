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
        'network--branches-visible': branchesVisible,
        'network--branches-interactive': branchesInteractive,
        'network--branches-retreated': branchesRetreated,
      }"
      aria-labelledby="network-title"
      @transitionend="handleNetworkTransitionEnd"
    >
      <svg class="network-lines" viewBox="0 0 1600 900" preserveAspectRatio="none" aria-hidden="true">
        <defs>
          <linearGradient id="nl1" gradientUnits="userSpaceOnUse" x1="700" y1="432" x2="300" y2="252">
            <stop offset="0" stop-color="#faf9f5" stop-opacity="0" />
            <stop offset="0.55" stop-color="#faf9f5" stop-opacity="0.06" />
            <stop offset="1" stop-color="#faf9f5" stop-opacity="0.34" />
          </linearGradient>
          <linearGradient id="nl2" gradientUnits="userSpaceOnUse" x1="900" y1="432" x2="1320" y2="200">
            <stop offset="0" stop-color="#faf9f5" stop-opacity="0" />
            <stop offset="0.55" stop-color="#faf9f5" stop-opacity="0.06" />
            <stop offset="1" stop-color="#faf9f5" stop-opacity="0.34" />
          </linearGradient>
          <linearGradient id="nl3" gradientUnits="userSpaceOnUse" x1="700" y1="468" x2="330" y2="694">
            <stop offset="0" stop-color="#faf9f5" stop-opacity="0" />
            <stop offset="0.55" stop-color="#faf9f5" stop-opacity="0.06" />
            <stop offset="1" stop-color="#faf9f5" stop-opacity="0.34" />
          </linearGradient>
          <linearGradient id="nl4" gradientUnits="userSpaceOnUse" x1="900" y1="468" x2="1300" y2="742">
            <stop offset="0" stop-color="#faf9f5" stop-opacity="0" />
            <stop offset="0.55" stop-color="#faf9f5" stop-opacity="0.06" />
            <stop offset="1" stop-color="#faf9f5" stop-opacity="0.34" />
          </linearGradient>
        </defs>
        <path class="nl-line nl-line--1" pathLength="1" stroke="url(#nl1)" d="M700 432 L300 252" />
        <path class="nl-line nl-line--2" pathLength="1" stroke="url(#nl2)" d="M900 432 L1320 200" />
        <path class="nl-line nl-line--3" pathLength="1" stroke="url(#nl3)" d="M700 468 L330 694" />
        <path class="nl-line nl-line--4" pathLength="1" stroke="url(#nl4)" d="M900 468 L1300 742" />
      </svg>

      <div class="network-topics" :aria-hidden="!branchesInteractive">
        <button
          v-for="(topic, index) in topics"
          :key="topic.id"
          class="topic"
          :class="`topic--${index + 1}`"
          type="button"
          :tabindex="branchesInteractive ? 0 : -1"
          @click="selectTopic(topic)"
        >
          <span class="topic-name">{{ topic.title }}</span>
        </button>
      </div>

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
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
})

const embedded = props.embedded

const i18n = useI18nStore()
const router = useRouter()
const pageRef = ref(null)
const networkRef = ref(null)
// 初始状态就保留中央黑框及其文案，扩散动画只负责打开周边区域。
const centerVisible = ref(true)
const expansionStarted = ref(false)
const expansionComplete = ref(false)
const expansionGateActive = ref(false)
const branchesVisible = ref(false)
const branchesRetreated = ref(false)
const branchRetreatActive = ref(false)
const t = (key, vars) => i18n.t(key, vars)
const topicIds = ['data-governance', 'model-engineering', 'agent-development', 'platform-build']
const EXPANSION_DELAY_MS = 120
const EXPANSION_FALLBACK_MS = 1380
const BRANCH_RETREAT_MS = 760
const EXPANSION_TRIGGER_VIEWPORT_RATIO = 0.58
const RETREAT_TRIGGER_VIEWPORT_RATIO = 0.3
const PINNED_BREAKPOINT = 901

const topics = computed(() => topicIds.map((id, index) => ({
  id,
  index: String(index + 1).padStart(2, '0'),
  title: t(`technologyPage.topics.${id}.title`),
  question: t(`technologyPage.topics.${id}.question`),
  summary: t(`technologyPage.topics.${id}.summary`),
  points: [1, 2, 3, 4].map((point) => t(`technologyPage.topics.${id}.point${point}`)),
})))

const branchesInteractive = computed(() => (
  branchesVisible.value && !branchesRetreated.value
))

let entryFrame = null
let expansionTimer = null
let completionTimer = null
let branchRetreatTimer = null
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
  if (branchRetreatTimer !== null) {
    window.clearTimeout(branchRetreatTimer)
    branchRetreatTimer = null
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
    || branchRetreatActive.value
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
  branchesVisible.value = true
  setExpansionGate(false)
}

function finishBranchRetreat() {
  branchRetreatTimer = null
  branchRetreatActive.value = false
  syncInputCapture()
}

function startBranchRetreat() {
  if (
    !usesPinnedExperience()
    || !interactionZoneActive
    || !expansionComplete.value
    || branchesRetreated.value
    || branchRetreatActive.value
  ) return

  branchesRetreated.value = true
  branchRetreatActive.value = true
  syncInputCapture()
  branchRetreatTimer = window.setTimeout(finishBranchRetreat, BRANCH_RETREAT_MS)
}

function revealBranches() {
  if (branchRetreatTimer !== null) {
    window.clearTimeout(branchRetreatTimer)
    branchRetreatTimer = null
  }
  branchRetreatActive.value = false
  branchesRetreated.value = false
  syncInputCapture()
}

function resetNetworkAnimation() {
  clearNetworkTimers()
  hasAnimated = false
  interactionZoneActive = false
  // 回到页面顶部时只收回扩散层，保留首次打开时的中央黑色内容框。
  centerVisible.value = true
  expansionStarted.value = false
  expansionComplete.value = false
  branchesVisible.value = false
  branchesRetreated.value = false
  branchRetreatActive.value = false
  setExpansionGate(false)
}

function startNetworkAnimation() {
  if (hasAnimated) return
  hasAnimated = true
  centerVisible.value = true
  expansionComplete.value = false
  branchesRetreated.value = false
  branchRetreatActive.value = false
  // 扩散提前开始；只有真正进入整屏停驻位置且动画尚未完成时才锁住下滑。
  setExpansionGate(false)

  // 手机端不需要桌面的大面积扩散等待；进入区块时直接给出完整内容，
  // 避免短屏设备先看到一整屏空黑区域。
  const compactViewport = window.matchMedia(`(max-width: ${PINNED_BREAKPOINT - 1}px)`).matches
  if (prefersReducedMotion() || compactViewport) {
    expansionStarted.value = true
    expansionComplete.value = true
    branchesVisible.value = true
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

  if (embedded && currentScrollY <= 8) {
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
    if (branchesRetreated.value || branchRetreatActive.value) revealBranches()
    if (expansionGateActive.value) finishNetworkExpansion()
  }

  const rect = pageRef.value.getBoundingClientRect()
  const viewportHeight = window.innerHeight || 1
  const pinnedDistance = Math.max(0, -rect.top)
  const retreatTriggerDistance = viewportHeight * RETREAT_TRIGGER_VIEWPORT_RATIO
  updateInteractionZone(rect, viewportHeight)

  if (
    branchesRetreated.value
    && scrollDelta < -1
    && rect.top < viewportHeight * 0.4
    && rect.bottom > viewportHeight * 0.6
  ) revealBranches()

  // 先在停驻区内向下移动约三成屏高，再用方向信号启动一次定时退场。
  if (
    scrollDelta > 1
    && interactionZoneActive
    && pinnedDistance >= retreatTriggerDistance
    && expansionComplete.value
    && !branchesRetreated.value
    && !branchRetreatActive.value
  ) startBranchRetreat()

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

function selectTopic(topic) {
  router.push({ name: 'technology-topic', params: { topicId: topic.id } })
}

function preventForwardInput(event) {
  if (event.cancelable) event.preventDefault()
}

function handleForwardIntent(event, forwardDistance) {
  if (expansionGateActive.value || branchRetreatActive.value) {
    preventForwardInput(event)
    return true
  }

  if (
    !interactionZoneActive
    || !expansionComplete.value
    || branchesRetreated.value
  ) return false

  const page = pageRef.value
  if (!page) return false

  const viewportHeight = window.innerHeight || 1
  const rect = page.getBoundingClientRect()
  const stillPinned = rect.top <= 1 && rect.bottom >= viewportHeight - 1
  if (!stillPinned) return false

  const pinnedDistance = Math.max(0, -rect.top)
  const retreatTriggerDistance = viewportHeight * RETREAT_TRIGGER_VIEWPORT_RATIO
  const remainingDistance = Math.max(0, retreatTriggerDistance - pinnedDistance)
  if (forwardDistance < remainingDistance) return false

  preventForwardInput(event)
  if (remainingDistance > 1) {
    window.scrollTo({
      top: window.scrollY + remainingDistance,
      behavior: 'instant',
    })
  }
  startBranchRetreat()
  return true
}

function handleWheelSignal(event) {
  if (event.deltaY <= 0 || event.ctrlKey) return

  const deltaScale = event.deltaMode === 1
    ? 16
    : event.deltaMode === 2
      ? window.innerHeight
      : 1
  handleForwardIntent(event, event.deltaY * deltaScale)
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

  const forwardDistance = event.key === 'ArrowDown'
    ? 48
    : event.key === 'End'
      ? Number.POSITIVE_INFINITY
      : window.innerHeight * 0.9
  handleForwardIntent(event, forwardDistance)
}

function handleTouchStart(event) {
  lastTouchY = event.touches.length === 1
    ? event.touches[0].clientY
    : null
}

function handleTouchMove(event) {
  if (expansionGateActive.value || branchRetreatActive.value) {
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
  if (forwardDistance > 0) handleForwardIntent(event, forwardDistance)
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
  clearNetworkTimers()
  expansionGateActive.value = false
  branchRetreatActive.value = false
  interactionZoneActive = false
  setInputCapture(false)
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
  z-index: 1;
  width: 100%;
  height: 100%;
  pointer-events: none;
  transition: opacity 0.72s cubic-bezier(0.22, 1, 0.36, 1);
}

.nl-line {
  fill: none;
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  opacity: 0;
  vector-effect: non-scaling-stroke;
  transition:
    stroke-dashoffset 1.15s cubic-bezier(0.22, 1, 0.36, 1),
    opacity 0.7s ease;
}

.network--branches-visible .nl-line {
  stroke-dashoffset: 0;
  opacity: 1;
}

.network--branches-visible .nl-line--2 { transition-delay: 0.09s; }
.network--branches-visible .nl-line--3 { transition-delay: 0.18s; }
.network--branches-visible .nl-line--4 { transition-delay: 0.27s; }

.network--branches-retreated .network-lines {
  opacity: 0;
}

.network-copy {
  position: absolute;
  top: 50%;
  left: 50%;
  z-index: 2;
  width: min(46vw, 740px);
  text-align: center;
  transform: translate(-50%, -50%);
  opacity: 0;
  filter: blur(7px);
  transition: opacity 0.75s ease, filter 0.75s ease, transform 0.75s ease;
  transform: translate(-50%, calc(-50% + 18px));
}

.network--center-visible .network-copy {
  opacity: 1;
  filter: blur(0);
  transform: translate(-50%, -50%);
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
  display: block;
  width: clamp(200px, 17vw, 268px);
  padding: 0;
  border: 0;
  background: transparent;
  color: rgba(250, 249, 245, 0.58);
  text-align: left;
  cursor: pointer;
  opacity: 0;
  transform: translateY(14px);
  pointer-events: none;
  transition: color 0.35s ease, opacity 0.7s ease, transform 0.7s ease;
}

.network--branches-visible .topic {
  opacity: 1;
  transform: translateY(0);
}

.network--branches-interactive .topic {
  pointer-events: auto;
}

.network--branches-visible .topic--2 { transition-delay: 0.09s; }
.network--branches-visible .topic--3 { transition-delay: 0.18s; }
.network--branches-visible .topic--4 { transition-delay: 0.27s; }

.topic:hover,
.topic:focus-visible,
.topic--active {
  color: #faf9f5;
  outline: none;
}

/* 非对称散布：靠近中央、松散呼应第一张的星座式排布 */
.topic--1 { top: 27%; left: 8.5%; text-align: left; }
.topic--2 { top: 20%; right: 8%; text-align: right; }
.topic--3 { bottom: 22%; left: 11.5%; text-align: left; }
.topic--4 { right: 9.5%; bottom: 16%; text-align: right; }

.topic-name {
  display: block;
  font-size: clamp(19px, 1.9vw, 30px);
  font-weight: 400;
  line-height: 1.2;
  letter-spacing: 0.02em;
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
    width: min(100%, 420px);
    margin: clamp(56px, 8svh, 76px) auto 0;
    order: 2;
    grid-template-columns: minmax(0, 1fr);
    gap: 22px;
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
    margin: 0;
    padding: 0;
    border: 0;
    border-radius: 0;
    background: transparent;
    text-align: center;
    transform: translateY(10px);
    transition: color 0.2s ease, opacity 0.3s ease, transform 0.3s ease;
  }

  .topic-name {
    font-size: clamp(18px, 5vw, 24px);
    line-height: 1.3;
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

  .topic-name {
    font-size: clamp(15px, 4.8vw, 18px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .topic,
  .network-lines,
  .nl-line,
  .network-topics,
  .network-support {
    transition: none;
  }

  .nl-line {
    stroke-dashoffset: 0;
    opacity: 1;
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
}

@media (prefers-reduced-motion: reduce) and (max-width: 900px) {
  .technology-page--embedded,
  .technology-page--embedded .network {
    min-height: 0;
    height: auto;
  }
}
</style>
