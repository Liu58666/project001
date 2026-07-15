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
        <path pathLength="1" d="M735 425 L395 275" />
        <path pathLength="1" d="M865 425 L1205 215" />
        <path pathLength="1" d="M735 475 L405 665" />
        <path pathLength="1" d="M865 475 L1200 690" />
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
          <span class="topic-number">{{ topic.index }}</span>
          <span class="topic-name">{{ topic.title }}</span>
          <span class="topic-arrow" aria-hidden="true">↗</span>
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
    inputListenersAttached = true
  } else if (!active && inputListenersAttached) {
    window.removeEventListener('wheel', handleWheelSignal)
    window.removeEventListener('keydown', handleKeySignal)
    inputListenersAttached = false
  }
}

function syncInputCapture() {
  const shouldCapture = usesPinnedExperience() && (
    expansionGateActive.value
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

  if (prefersReducedMotion()) {
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

function handleWheelSignal(event) {
  if (event.deltaY <= 0) return

  if (expansionGateActive.value || branchRetreatActive.value) {
    event.preventDefault()
  }
}

function handleKeySignal(event) {
  const target = event.target
  if (
    target instanceof HTMLElement
    && (target.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON'].includes(target.tagName))
  ) return

  const isForwardSpace = event.key === ' ' && !event.shiftKey
  const isForwardKey = isForwardSpace || ['ArrowDown', 'PageDown', 'End'].includes(event.key)
  if (!isForwardKey) return

  if (expansionGateActive.value || branchRetreatActive.value) {
    event.preventDefault()
  }
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
    padding-top: 0;
    padding-block: 0;
  }

  .technology-page--embedded .network {
    width: 100%;
    min-height: 100svh;
    border-radius: 0;
    clip-path: inset(
      max(0px, calc((100svh - 520px) / 2))
      7%
      round 20px
    );
  }

  .technology-page--embedded .network.network--expanded {
    clip-path: inset(0 round 0);
  }

  .network {
    min-height: calc(100svh - 68px);
    padding: 56px 20px 34px;
    box-sizing: border-box;
  }

  .network-lines,
  .network-copy {
    position: static;
    width: 100%;
    text-align: left;
    transform: translateY(18px);
  }

  .network-topics {
    position: static;
    width: 100%;
    transform: none;
  }

  .network--center-visible .network-copy {
    transform: translateY(0);
  }

  .network-support > p {
    margin-left: 0;
  }

  h1 {
    max-width: 10ch;
    font-size: clamp(46px, 13vw, 72px);
  }

  .topic,
  .topic--1,
  .topic--2,
  .topic--3,
  .topic--4 {
    position: relative;
    inset: auto;
    width: 100%;
    margin-top: 22px;
    transform: translateY(14px);
  }

  .topic--1 {
    margin-top: 52px;
  }

  .topic-name {
    font-size: 30px;
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
</style>
