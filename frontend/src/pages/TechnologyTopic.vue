<template>
  <div v-if="topic" class="topic-page">
    <main class="topic-hero" :aria-labelledby="`topic-title-${topic.id}`">
      <div :class="['topic-copy', { 'topic-copy--visible': pageEnter }]">
        <p class="topic-index topic-reveal">{{ topic.index }} / 04 · DAIL TECH</p>

        <h1 :id="`topic-title-${topic.id}`" :aria-label="topic.title">
          <span
            v-for="(segment, index) in titleSegments"
            :key="`${topic.id}-${index}-${segment}`"
            class="topic-title-segment"
            aria-hidden="true"
          >
            <span
              class="topic-title-inner"
              :style="{ '--segment-delay': `${index * 58}ms` }"
            >{{ segment }}</span>
          </span>
        </h1>

        <p class="topic-summary topic-reveal">{{ topic.summary }}</p>
        <button class="topic-back topic-reveal" type="button" @click="router.push('/coming-soon')">
          {{ t('technologyPage.moreHardQuestions') }}
          <span aria-hidden="true">→</span>
        </button>
      </div>
    </main>

    <End />
  </div>
</template>

<script setup>
import { computed, inject, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'
import End from '@/page_components/End.vue'

const route = useRoute()
const router = useRouter()
const i18n = useI18nStore()
const loaderFinished = inject('loaderFinished', ref(true))
const pageEnter = ref(false)
const t = (key, vars) => i18n.t(key, vars)
const topicIds = ['data-governance', 'model-engineering', 'agent-development', 'platform-build']
let revealFrame = null

const topic = computed(() => {
  const index = topicIds.indexOf(String(route.params.topicId))
  if (index === -1) return null

  const id = topicIds[index]
  return {
    id,
    index: String(index + 1).padStart(2, '0'),
    title: t(`technologyPage.topics.${id}.title`),
    summary: t(`technologyPage.topics.${id}.summary`),
  }
})

const titleSegments = computed(() => {
  if (!topic.value) return []
  const title = topic.value.title
  if (!title.includes(' ')) return Array.from(title)

  const words = title.split(' ')
  return words.map((word, index) => (index < words.length - 1 ? `${word}\u00a0` : word))
})

const playReveal = async () => {
  pageEnter.value = false
  await nextTick()
  if (revealFrame !== null) window.cancelAnimationFrame(revealFrame)
  revealFrame = window.requestAnimationFrame(() => {
    revealFrame = window.requestAnimationFrame(() => {
      revealFrame = null
      pageEnter.value = true
    })
  })
}

watch(topic, (value) => {
  if (!value) router.replace('/technology')
}, { immediate: true })

watch(
  [() => route.params.topicId, loaderFinished],
  ([, isLoaderFinished]) => {
    if (topic.value && isLoaderFinished) playReveal()
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  if (revealFrame !== null) window.cancelAnimationFrame(revealFrame)
})
</script>

<style scoped>
.topic-page {
  min-height: 100svh;
  background: #ffffff;
  color: #141413;
}

.topic-hero {
  display: grid;
  min-height: max(620px, 82svh);
  padding: 140px 7vw 96px;
  place-items: center;
  background: #ffffff;
}

.topic-copy {
  width: min(100%, 820px);
  text-align: left;
}

.topic-reveal {
  opacity: 0;
  visibility: hidden;
  transform: translateY(16px);
  transition:
    opacity 0.68s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.68s cubic-bezier(0.16, 1, 0.3, 1),
    visibility 0s linear 0.68s;
  will-change: opacity, transform;
}

.topic-index {
  margin: 0 0 34px;
  color: #777772;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.16em;
  transition-delay: 0.02s;
}

h1 {
  display: flex;
  flex-wrap: wrap;
  margin: 0;
  font-family: 'Songti SC', STSong, Georgia, 'Times New Roman', serif;
  font-size: clamp(76px, 10vw, 150px);
  font-weight: 400;
  line-height: 0.94;
  letter-spacing: -0.065em;
}

.topic-title-segment {
  display: inline-block;
  overflow: hidden;
  padding-bottom: 0.08em;
  margin-bottom: -0.08em;
}

.topic-title-inner {
  display: inline-block;
  opacity: 0;
  visibility: hidden;
  transform: translateY(45%);
  transition:
    opacity 0.62s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.62s cubic-bezier(0.16, 1, 0.3, 1),
    visibility 0s linear 0.62s;
  transition-delay: calc(0.08s + var(--segment-delay, 0ms));
  will-change: opacity, transform;
}

.topic-copy--visible .topic-title-inner {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
  transition-property: opacity, transform, visibility;
  transition-delay: calc(0.08s + var(--segment-delay, 0ms));
}

.topic-copy--visible .topic-reveal {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.topic-copy--visible .topic-index {
  transition-delay: 0.02s;
}

.topic-summary {
  max-width: 710px;
  margin: 52px 0 0;
  color: #73736d;
  font-size: clamp(17px, 1.45vw, 21px);
  line-height: 1.62;
  transition-delay: 0.42s;
}

.topic-back {
  display: inline-flex;
  margin-top: 34px;
  padding: 12px 18px;
  align-items: center;
  gap: 54px;
  border: 1px solid #141413;
  border-radius: 8px;
  background: #141413;
  color: #ffffff;
  font-size: 14px;
  cursor: pointer;
  transition:
    background 0.2s ease,
    color 0.2s ease,
    opacity 0.68s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.68s cubic-bezier(0.16, 1, 0.3, 1),
    visibility 0s linear 0.68s;
  transition-delay: 0s, 0s, 0.54s, 0.54s, 0.54s;
}

.topic-copy--visible .topic-back {
  transition-delay: 0s, 0s, 0.54s, 0.54s, 0.54s;
}

.topic-back:hover,
.topic-back:focus-visible {
  background: #ffffff;
  color: #141413;
  outline: none;
}

@media (max-width: 900px) {
  .topic-hero {
    min-height: 76svh;
    padding: 126px 24px 76px;
  }

  .topic-copy {
    text-align: left;
  }

  .topic-index {
    margin-bottom: 26px;
  }

  h1 {
    font-size: clamp(60px, 18vw, 96px);
    letter-spacing: -0.055em;
  }

  .topic-summary {
    margin-top: 34px;
    font-size: 17px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .topic-reveal,
  .topic-title-inner,
  .topic-back {
    opacity: 1;
    visibility: visible;
    transform: none;
    transition: none;
  }
}
</style>
