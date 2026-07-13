<template>
  <section class="news-page">
    <div class="news-container">
      <header class="news-header">
        <h1 class="news-title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }">
          {{ t('news.title') }}
        </h1>
        <p class="news-subtitle reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '140ms' }">
          {{ t('news.subtitle') }}
        </p>
      </header>

      <div class="news-controls reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '220ms' }">
        <div class="menu" role="tablist" :aria-label="t('news.title')">
          <button
            v-for="tab in tabs"
            :key="tab.value"
            class="link"
            :class="{ active: activeTab === tab.value }"
            type="button"
            role="tab"
            :aria-selected="activeTab === tab.value ? 'true' : 'false'"
            @click="activeTab = tab.value"
          >
            <span
              :class="['link-icon', { 'link-icon--sm': tab.value === 'Milestone' || tab.value === 'News' }]"
              aria-hidden="true"
            >
              <!-- ALL -->
              <svg
                v-if="tab.value === 'ALL'"
                xmlns="http://www.w3.org/2000/svg"
                width="28"
                height="28"
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M4 7h16M4 12h16M4 17h16"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                />
              </svg>

              <!-- Alliance -->
              <svg
                v-else-if="tab.value === 'Alliance'"
                xmlns="http://www.w3.org/2000/svg"
                width="28"
                height="28"
                viewBox="0 0 1024 1024"
                fill="none"
              >
                <path
                  d="M512 546.133333c-123.733333 0-221.866667-102.4-221.866667-221.866666S388.266667 98.133333 512 98.133333c123.733333 0 221.866667 102.4 221.866667 221.866667s-98.133333 226.133333-221.866667 226.133333z m0-384c-89.6 0-162.133333 72.533333-162.133333 162.133334s72.533333 157.866667 162.133333 157.866666c89.6 0 162.133333-72.533333 162.133333-162.133333S601.6 162.133333 512 162.133333z"
                  fill="currentColor"
                />
                <path
                  d="M853.333333 887.466667c-17.066667 0-34.133333-12.8-34.133333-34.133334 0-170.666667-140.8-307.2-307.2-307.2-170.666667 0-307.2 136.533333-307.2 307.2 0 17.066667-12.8 34.133333-34.133333 34.133334s-34.133333-12.8-34.133334-34.133334c0-204.8 166.4-371.2 375.466667-371.2 204.8 0 375.466667 166.4 375.466667 371.2 0 17.066667-17.066667 34.133333-34.133334 34.133334zM768 503.466667c-17.066667 0-34.133333-12.8-34.133333-34.133334s17.066667-29.866667 34.133333-29.866666c51.2 0 93.866667-42.666667 93.866667-93.866667s-42.666667-98.133333-93.866667-98.133333c-17.066667 0-34.133333-12.8-34.133333-34.133334s17.066667-29.866667 34.133333-29.866666c89.6 0 162.133333 72.533333 162.133333 162.133333s-72.533333 157.866667-162.133333 157.866667z"
                  fill="currentColor"
                />
                <path
                  d="M981.333333 716.8c-17.066667 0-34.133333-12.8-34.133333-34.133333 0-98.133333-81.066667-179.2-179.2-179.2-17.066667 0-34.133333-12.8-34.133333-34.133334s17.066667-29.866667 34.133333-29.866666c136.533333 0 247.466667 110.933333 247.466667 247.466666 0 12.8-17.066667 29.866667-34.133334 29.866667z"
                  fill="currentColor"
                />
                <path
                  d="M256 503.466667c-89.6 0-162.133333-72.533333-162.133333-162.133334S166.4 183.466667 256 183.466667c17.066667 0 34.133333 12.8 34.133333 34.133333s-17.066667 29.866667-34.133333 29.866667c-51.2 0-93.866667 42.666667-93.866667 93.866666s42.666667 98.133333 93.866667 98.133334c17.066667 0 34.133333 12.8 34.133333 34.133333s-17.066667 29.866667-34.133333 29.866667z"
                  fill="currentColor"
                />
                <path
                  d="M42.666667 716.8c-17.066667 0-34.133333-12.8-34.133334-34.133333 0-136.533333 110.933333-247.466667 247.466667-247.466667 17.066667 0 34.133333 12.8 34.133333 34.133333s-17.066667 34.133333-34.133333 34.133334c-98.133333 0-179.2 81.066667-179.2 179.2 0 17.066667-17.066667 34.133333-34.133333 34.133333z"
                  fill="currentColor"
                />
              </svg>

              <!-- Milestone -->
              <svg
                v-else-if="tab.value === 'Milestone'"
                xmlns="http://www.w3.org/2000/svg"
                width="28"
                height="28"
                viewBox="0 0 1024 1024"
                fill="none"
              >
                <path
                  d="M918.4 62.08c-14.08 5.12-30.72 8.96-48.64 14.08-17.92 5.12-40.32 8.32-65.92 11.52-25.6 2.56-51.84 5.12-78.08 5.12-16.64 0-59.52-3.84-83.84-9.6-57.6-15.36-87.04-23.04-87.04-23.04L470.4 32C442.88 22.4 414.08 14.72 384 8.32 354.56 2.56 325.76 0 299.52 0c-26.24 0-53.12 1.28-78.72 5.12-26.24 3.2-48 7.04-65.28 10.88-16.64 3.84-33.28 8.96-49.92 14.72-16 5.12-26.24 8.96-30.72 10.88-5.12 2.56-8.96 3.84-10.88 5.12v930.56c0 25.6 21.12 46.72 46.72 46.72s46.72-21.12 46.72-46.72v-309.76a629.76 629.76 0 0 1 141.44-15.36c40.32 0.64 70.4 6.4 83.84 9.6l87.04 23.04 83.2 26.88c28.8 8.96 57.6 17.28 87.04 23.04 30.08 6.4 58.24 9.6 83.84 9.6 26.88 0 53.12-1.28 78.72-5.12 26.88-3.84 48-7.04 65.28-11.52 16.64-3.84 33.28-8.32 49.28-14.08a62.72 62.72 0 0 0 41.6-58.88V93.44c0-17.92-14.72-32.64-32.64-32.64-1.92 0-4.48 0.64-7.68 1.28z"
                  fill="currentColor"
                />
              </svg>

              <!-- Partnership -->
              <svg
                v-else-if="tab.value === 'Partnership'"
                xmlns="http://www.w3.org/2000/svg"
                width="28"
                height="28"
                viewBox="0 0 1024 1024"
                fill="none"
              >
                <path
                  d="M512 115.712a384 384 0 1 1 0 768 384 384 0 0 1 0-768z m0 64a320 320 0 1 0 0 640 320 320 0 0 0 0-640z"
                  fill="currentColor"
                />
                <path
                  d="M512 499.712m-160 0a160 160 0 1 0 320 0 160 160 0 1 0-320 0Z"
                  fill="currentColor"
                />
                <path
                  d="M480 27.008m32 0l0 0q32 0 32 32l0 192q0 32-32 32l0 0q-32 0-32-32l0-192q0-32 32-32Z"
                  fill="currentColor"
                />
                <path
                  d="M480 731.008m32 0l0 0q32 0 32 32l0 192q0 32-32 32l0 0q-32 0-32-32l0-192q0-32 32-32Z"
                  fill="currentColor"
                />
                <path
                  d="M992 475.008m0 32l0 0q0 32-32 32l-192 0q-32 0-32-32l0 0q0-32 32-32l192 0q32 0 32 32Z"
                  fill="currentColor"
                />
                <path
                  d="M288 475.008m0 32l0 0q0 32-32 32l-192 0q-32 0-32-32l0 0q0-32 32-32l192 0q32 0 32 32Z"
                  fill="currentColor"
                />
              </svg>

              <!-- New Tools (was News) -->
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                width="28"
                height="28"
                viewBox="0 0 1024 1024"
                fill="none"
              >
                <path
                  d="M1016.832 606.208q2.048 12.288-1.024 29.696t-10.24 35.328-17.408 32.256-22.528 20.48-21.504 6.144-20.48-4.096q-10.24-3.072-25.6-5.632t-31.232-1.024-31.744 6.656-27.136 17.408q-24.576 25.6-28.672 58.368t9.216 62.464q10.24 20.48-3.072 40.96-6.144 8.192-19.456 16.896t-29.184 15.872-33.28 11.264-30.72 4.096q-9.216 0-17.408-7.168t-11.264-15.36l-1.024 0q-11.264-31.744-38.4-54.784t-62.976-23.04q-34.816 0-62.976 23.04t-39.424 53.76q-5.12 12.288-15.36 17.92t-22.528 5.632q-14.336 0-32.256-5.12t-35.84-12.8-32.256-17.92-21.504-20.48q-5.12-7.168-5.632-16.896t7.68-27.136q11.264-23.552 8.704-53.76t-26.112-55.808q-14.336-15.36-34.816-19.968t-38.912-3.584q-21.504 1.024-44.032 8.192-14.336 4.096-28.672-2.048-11.264-4.096-20.992-18.944t-17.408-32.768-11.776-36.864-2.048-31.232q3.072-22.528 20.48-28.672 30.72-12.288 55.296-40.448t24.576-62.976q0-35.84-24.576-62.464t-55.296-38.912q-9.216-3.072-15.36-14.848t-6.144-24.064q0-13.312 4.096-29.696t10.752-31.744 15.36-28.16 18.944-18.944q8.192-5.12 15.872-4.096t16.896 4.096q30.72 12.288 64 7.68t58.88-29.184q12.288-12.288 17.92-30.208t7.168-35.328 0-31.744-2.56-20.48q-2.048-6.144-3.584-14.336t1.536-14.336q6.144-14.336 22.016-25.088t34.304-17.92 35.84-10.752 27.648-3.584q13.312 0 20.992 8.704t10.752 17.92q11.264 27.648 36.864 48.64t60.416 20.992q35.84 0 63.488-19.968t38.912-50.688q4.096-8.192 12.8-16.896t17.92-8.704q14.336 0 31.232 4.096t33.28 11.264 30.208 18.432 22.016 24.576q5.12 8.192 3.072 17.92t-4.096 13.824q-13.312 29.696-8.192 62.464t29.696 57.344 60.416 27.136 66.56-11.776q8.192-5.12 19.968-4.096t19.968 9.216q15.36 14.336 27.136 43.52t15.872 58.88q2.048 17.408-5.632 27.136t-15.872 12.8q-31.744 11.264-54.272 39.424t-22.528 64q0 34.816 18.944 60.928t49.664 37.376q7.168 4.096 12.288 8.192 11.264 9.216 15.36 23.552zM540.672 698.368q46.08 0 87.04-17.408t71.168-48.128 47.616-71.168 17.408-86.528-17.408-86.528-47.616-70.656-71.168-47.616-87.04-17.408-86.528 17.408-70.656 47.616-47.616 70.656-17.408 86.528 17.408 86.528 47.616 71.168 70.656 48.128 86.528 17.408z"
                  fill="currentColor"
                />
              </svg>
            </span>

            <span class="link-title">{{ tab.label }}</span>
          </button>
        </div>
      </div>

      <div class="grid" role="list" :aria-label="t('news.ariaList')">
        <div v-if="isLoading" class="loading reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '320ms' }" role="status" aria-live="polite">
          Loading…
        </div>

        <div v-else-if="filtered.length === 0" class="empty reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '320ms' }" role="status" aria-live="polite">
          No articles yet.
        </div>

        <article
          v-else
          v-for="(item, idx) in filtered"
          :key="item.id"
          :ref="setCardRef"
          class="card reveal"
          :style="{ '--d': `${Math.min(760, 260 + idx * 50)}ms` }"
          role="listitem"
        >
          <RouterLink
            class="card-hit"
            :to="item.slug ? { name: 'news-detail', params: { slug: item.slug } } : { name: 'news' }"
            :aria-label="`Open: ${item.title}`"
          >
            <span class="sr-only">Open</span>
          </RouterLink>
          <div class="thumb" aria-hidden="true">
            <div class="thumb-title">{{ item.title }}</div>
          </div>
          <div class="meta">
            <span class="meta-line">
              <span class="meta-item meta-tag">{{ t(`news.categories.${item.category}`) }}</span>
              <span class="meta-sep" aria-hidden="true">|</span>
              <span class="meta-item meta-date">{{ formatDateText(item.publishedAt) }}</span>
            </span>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import { listNews } from '@/services/newsService'
import { useErrorStore } from '@/stores/error'

const i18n = useI18nStore()
const t = (key, vars) => i18n.t(key, vars)
const errorStore = useErrorStore()

const pageEnter = ref(false)

const tabs = computed(() => [
  { label: t('news.tabs.all'), value: 'ALL' },
  { label: t('news.tabs.alliance'), value: 'Alliance' },
  { label: t('news.tabs.milestone'), value: 'Milestone' },
  { label: t('news.tabs.partnership'), value: 'Partnership' },
  { label: t('news.tabs.companyNews'), value: 'News' },
])

const activeTab = ref('ALL')

const items = ref([])
const isLoading = ref(false)

function formatDateText(input) {
  if (!input) return ''
  const d = new Date(input)
  if (Number.isNaN(d.getTime())) return String(input)
  return new Intl.DateTimeFormat('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
    .format(d)
    .toUpperCase()
}

let io = null
function setCardRef(el) {
  if (!el || !io) return
  io.observe(el)
}

async function loadNews() {
  isLoading.value = true
  try {
    items.value = await listNews({ limit: 50, offset: 0 })
  } catch (e) {
    errorStore.showError(e?.message || 'Failed to load news')
    items.value = []
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  io = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue
        e.target.classList.add('is-in')
        io?.unobserve(e.target)
      }
    },
    { threshold: 0.18, rootMargin: '0px 0px -10% 0px' }
  )

  requestAnimationFrame(() => {
    pageEnter.value = true
  })
  loadNews()
})

onBeforeUnmount(() => {
  io?.disconnect()
  io = null
})

const filtered = computed(() => {
  return items.value.filter((x) => {
    const tabOk = activeTab.value === 'ALL' || x.category === activeTab.value
    return tabOk
  })
})

watch(
  () => filtered.value,
  async () => {
    // When tabs change / data loads, re-arm observer for newly rendered cards
    await nextTick()
    // cards will call setCardRef on mount; no further action needed
  }
)
</script>

<style scoped>
.reveal {
  opacity: 0;
  transform: translate3d(0, 22px, 0);
  filter: blur(10px);
  transition:
    opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.9s cubic-bezier(0.16, 1, 0.3, 1),
    filter 0.9s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--d, 0ms);
  will-change: opacity, transform, filter;
}

.reveal.is-in {
  opacity: 1;
  transform: translate3d(0, 0, 0);
  filter: blur(0);
}

@media (prefers-reduced-motion: reduce) {
  .reveal {
    transition: none;
    opacity: 1;
    transform: none;
    filter: none;
  }
}

.news-page {
  background: #fbfbfb;
  padding: 120px 24px 72px; /* 预留顶部固定导航高度 */
}

.news-container {
  max-width: 1400px;
  margin: 0 auto;
}

.news-title {
  font-size: 72px;
  line-height: 1.02;
  letter-spacing: -0.04em;
  font-weight: 500;
  color: #0b0f19;
  margin: 0 0 10px;
}

.news-subtitle {
  margin: 0 0 42px; /* more space: subtitle -> filters */
  max-width: 760px;
  font-size: 15px;
  line-height: 1.7;
  color: rgba(17, 24, 39, 0.62);
}

.news-controls {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 18px;
  margin-bottom: 52px; /* more space: filters -> news list */
}

/* Expandable menu tabs (based on the provided template; converted to plain CSS) */
.menu {
  padding: 0.25rem;
  background-color: transparent;
  position: relative;
  display: flex;
  justify-content: center;
  border: none;
  border-radius: 0;
  box-shadow: none;
  gap: 6px;
  flex-wrap: wrap;
}

.link {
  display: inline-flex;
  justify-content: flex-start;
  align-items: center;
  width: 48px; /* collapsed */
  height: 42px;
  border-radius: 8px;
  position: relative;
  z-index: 1;
  overflow: hidden;
  transform-origin: center left;
  transition: width 0.2s ease-in, color 0.2s ease-in, background-color 0.2s ease-in;
  text-decoration: none;
  color: #000000; /* pure black */
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 0 12px;
  gap: 8px;
}

.link::before {
  position: absolute;
  z-index: 0;
  content: '';
  display: block;
  border-radius: 8px;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  transform: translateX(100%);
  transition: transform 0.2s ease-in;
  transform-origin: center right;
  background-color: #eee;
}

.link:hover,
.link:focus-visible {
  outline: 0;
  width: 142px; /* expanded (smaller overall) */
}

.link:hover::before,
.link:focus-visible::before {
  transform: translateX(0);
}

.link-icon {
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.link-icon svg {
  width: 24px;
  height: 24px;
}

/* Smaller icon size for Milestone + New Tools */
.link-icon--sm svg {
  width: 20px;
  height: 20px;
}

.link-title {
  position: relative;
  z-index: 1;
  transform: translateX(100%);
  opacity: 0;
  transition: transform 0.2s ease-in, opacity 0.2s ease-in;
  transform-origin: center right;
  display: block;
  text-align: left;
  width: auto;
  font-size: 12px;
  letter-spacing: 0.04em;
  font-weight: 700;
  text-transform: none;
  white-space: nowrap;
}

.link:hover .link-title,
.link:focus-visible .link-title {
  transform: translateX(0);
  opacity: 1;
}

/* Active tab should look "expanded" even without hover */
.link.active {
  width: 142px;
  color: #ffffff; /* invert icon/text */
}

.link.active::before {
  transform: translateX(0);
  background-color: #000000; /* active highlight is black, not grey */
}

.link.active .link-title {
  transform: translateX(0);
  opacity: 1;
}

.link:focus-visible {
  box-shadow: 0 0 0 3px rgba(147, 51, 234, 0.25);
}

.grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 52px; /* wider spacing between cards */
}

.loading,
.empty {
  grid-column: 1 / -1;
  padding: 22px 0 10px;
  color: rgba(17, 24, 39, 0.62);
  font-size: 14px;
}

.card {
  position: relative;
  justify-self: center; /* keep smaller card centered within its grid cell */
  width: 100%;
  max-width: 300px; /* smaller card */
  cursor: pointer;
  outline: none;
}

.card-hit {
  position: absolute;
  inset: 0;
  z-index: 5;
  border-radius: 14px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.card:focus-within .thumb,
.card:hover .thumb {
  box-shadow: 0 16px 34px rgba(15, 23, 42, 0.10);
  transform: translateY(-2px);
}

.thumb {
  width: 100%;
  aspect-ratio: 1 / 1; /* 正方形封面占位 */
  border-radius: 14px;
  background-color: #ffffff;
  background-image: url('../assets/images/News_bg.png');
  background-repeat: no-repeat;
  background-position: center;
  background-size: 100%;
  border: none; /* remove cover border */
  display: grid;
  place-items: center;
  padding: 18px;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background-size 0.25s ease,
    background-color 0.25s ease, color 0.25s ease;
  overflow: hidden;
  color: #111827; /* default text color */
  position: relative;
}

.thumb-title {
  text-align: center;
  font-size: 18px;
  line-height: 1.35;
  font-weight: 700;
  max-width: 92%;
  display: -webkit-box;
  line-clamp: 3;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  padding-top: 8px;
  display: flex;
  align-items: baseline;
  justify-content: flex-start;
  padding-left: 8px; /* 左下角对齐到封面边缘 */
}

.meta-line {
  display: inline-flex;
  align-items: baseline;
  gap: 10px;
  white-space: nowrap;
}

.meta-item {
  font-size: 12px;
  line-height: 1.35;
  font-weight: 500;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(17, 24, 39, 0.72);
}

.meta-sep {
  font-size: 12px;
  line-height: 1.35;
  font-weight: 500;
  letter-spacing: 0.14em;
  color: rgba(17, 24, 39, 0.55);
}

/* Removed `.headline`: title is now centered on the cover image */

/* Touch/hover state: zoom bg + invert colors */
.card:hover .thumb,
.card:focus-within .thumb,
.card:active .thumb {
  background-size: 110%;
  background-color: #000000;
  color: #ffffff;
}

@media (max-width: 900px) {
  .news-page { padding: 104px 20px 64px; }
  .news-title { font-size: clamp(44px, 12vw, 60px); }
  .news-subtitle { margin-bottom: 30px; font-size: 16px; }
  .news-controls { margin-bottom: 36px; }
  .menu { width: 100%; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .link, .link.active, .link:hover, .link:focus-visible { width: 100%; min-height: 44px; }
  .link::before { transform: translateX(0); background: #eeeeee; }
  .link-title, .link:hover .link-title, .link:focus-visible .link-title { opacity: 1; transform: none; }
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 28px 18px; }
  .card { max-width: none; }
}

@media (max-width: 560px) {
  .grid { grid-template-columns: minmax(0, 1fr); }
}

</style>


