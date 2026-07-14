<template>
  <div
    :class="['technology-page', { 'technology-page--embedded': embedded }]"
  >
    <section
      ref="networkRef"
      class="network"
      :class="{
        'network--center-visible': centerVisible,
        'network--expanded': expansionStarted,
        'network--branches-visible': branchesVisible,
      }"
      aria-labelledby="network-title"
    >
      <svg class="network-lines" viewBox="0 0 1600 900" preserveAspectRatio="none" aria-hidden="true">
        <path pathLength="1" d="M735 425 L395 275" />
        <path pathLength="1" d="M865 425 L1205 215" />
        <path pathLength="1" d="M735 475 L405 665" />
        <path pathLength="1" d="M865 475 L1200 690" />
      </svg>

      <button
        v-for="(topic, index) in topics"
        :key="topic.id"
        class="topic"
        :class="`topic--${index + 1}`"
        type="button"
        @click="selectTopic(topic)"
      >
        <span class="topic-number">{{ topic.index }}</span>
        <span class="topic-name">{{ topic.title }}</span>
        <span class="topic-arrow" aria-hidden="true">↗</span>
      </button>

      <div class="network-copy">
        <h1 id="network-title">{{ t('technologyPage.mapTitle') }}</h1>
        <p>{{ t('technologyPage.mapInstruction') }}</p>
        <button class="network-action" type="button" @click="selectTopic(topics[0])">
          {{ t('technologyPage.explore') }}
          <span aria-hidden="true">→</span>
        </button>
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
const networkRef = ref(null)
// 初始状态就保留中央黑框及其文案，扩散动画只负责打开周边区域。
const centerVisible = ref(true)
const expansionStarted = ref(false)
const branchesVisible = ref(false)
const t = (key, vars) => i18n.t(key, vars)
const topicIds = ['data-governance', 'model-engineering', 'agent-development', 'platform-build']

const topics = computed(() => topicIds.map((id, index) => ({
  id,
  index: String(index + 1).padStart(2, '0'),
  title: t(`technologyPage.topics.${id}.title`),
  summary: t(`technologyPage.topics.${id}.summary`),
  points: [1, 2, 3, 4].map((point) => t(`technologyPage.topics.${id}.point${point}`)),
})))

let entryFrame = null
let expansionTimer = null
let branchesTimer = null
let hasAnimated = false

const clearNetworkTimers = () => {
  if (expansionTimer !== null) {
    window.clearTimeout(expansionTimer)
    expansionTimer = null
  }
  if (branchesTimer !== null) {
    window.clearTimeout(branchesTimer)
    branchesTimer = null
  }
}

const resetNetworkAnimation = () => {
  clearNetworkTimers()
  hasAnimated = false
  // 回到页面顶部时只收回扩散层，保留首次打开时的中央黑色内容框。
  centerVisible.value = true
  expansionStarted.value = false
  branchesVisible.value = false
}

const startNetworkAnimation = () => {
  if (hasAnimated) return
  hasAnimated = true
  centerVisible.value = true

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (reduceMotion) {
    expansionStarted.value = true
    branchesVisible.value = true
    return
  }

  expansionTimer = window.setTimeout(() => {
    expansionStarted.value = true
  }, 120)

  branchesTimer = window.setTimeout(() => {
    branchesVisible.value = true
  }, 1500)
}

const checkNetworkEntry = () => {
  if (!networkRef.value) return

  if (embedded && window.scrollY <= 8) {
    if (hasAnimated) resetNetworkAnimation()
    return
  }

  if (hasAnimated) return
  if (!embedded) {
    startNetworkAnimation()
    return
  }

  const rect = networkRef.value.getBoundingClientRect()
  const viewportHeight = window.innerHeight || 1
  const expansionTriggerLine = viewportHeight * 0.5
  if (rect.top <= expansionTriggerLine && rect.bottom > 0) startNetworkAnimation()
}

const requestEntryCheck = () => {
  if (entryFrame !== null) return
  entryFrame = window.requestAnimationFrame(() => {
    entryFrame = null
    checkNetworkEntry()
  })
}

const selectTopic = (topic) => {
  router.push({ name: 'technology-topic', params: { topicId: topic.id } })
}

onMounted(() => {
  window.addEventListener('scroll', requestEntryCheck, { passive: true })
  window.addEventListener('resize', requestEntryCheck, { passive: true })
  requestEntryCheck()
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', requestEntryCheck)
  window.removeEventListener('resize', requestEntryCheck)
  if (entryFrame !== null) window.cancelAnimationFrame(entryFrame)
  clearNetworkTimers()
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
  pointer-events: none;
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

.network-copy > p {
  max-width: 650px;
  margin: 28px auto 0;
  color: rgba(250, 249, 245, 0.72);
  font-size: clamp(15px, 1.25vw, 19px);
  line-height: 1.6;
}

.network-action {
  display: inline-flex;
  margin-top: 30px;
  padding: 11px 16px;
  align-items: center;
  gap: 28px;
  border: 1px solid #faf9f5;
  border-radius: 8px;
  background: #faf9f5;
  color: #141413;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.network-action:hover {
  background: transparent;
  color: #faf9f5;
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

  .network--center-visible .network-copy {
    transform: translateY(0);
  }

  .network-copy > p {
    margin-left: 0;
  }

  h1 {
    max-width: 10ch;
    font-size: clamp(46px, 13vw, 72px);
  }

  .network-action {
    margin-top: 22px;
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
  .network-action,
  .topic {
    transition: none;
  }

  .network-copy,
  .topic {
    opacity: 1;
    filter: none;
    transform: none;
  }

  .technology-page--embedded .network {
    width: 100%;
    min-height: 100svh;
    border-radius: 0;
    clip-path: inset(0 round 0);
    transition: none;
  }

  .network-lines path {
    stroke-dashoffset: 0;
    opacity: 1;
  }
}
</style>
