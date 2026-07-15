<template>
  <button class="news-card" type="button" @click="emit('click', latest)">
    <span class="inner">
      <span class="left">
        <span class="icon" aria-hidden="true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path
              d="M7 4h13v13a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3Z"
              stroke="currentColor"
              stroke-width="1.7"
              stroke-linejoin="round"
            />
            <path
              d="M8 8h8M8 12h8M8 16h6"
              stroke="currentColor"
              stroke-width="1.7"
              stroke-linecap="round"
            />
          </svg>
        </span>
        <span class="label">{{ t('news.title') }}</span>
      </span>

      <span class="summary" :title="displayText">{{ displayText }}</span>
    </span>
  </button>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import { listNews } from '@/services/newsService'

const i18n = useI18nStore()
const t = (key, vars) => i18n.t(key, vars)

const props = defineProps({
  // fallback text (when not loaded / error)
  summary: { type: String, default: 'More tools are added to DAIL' },
})

const emit = defineEmits(['click'])

const latest = ref(null)

function idLastDigit(item) {
  const raw = item?.id
  if (raw == null) return -1
  const s = String(raw).trim()
  if (!s) return -1
  const last = s.slice(-1)
  const n = Number(last)
  return Number.isFinite(n) ? n : -1
}

function pickLatest(list) {
  if (!Array.isArray(list) || list.length === 0) return null
  // Prefer "latest" by sorting on the last digit of id (desc).
  // If ids are missing/unusable, fallback to publishedAt (desc), otherwise keep first.
  const hasUsableId = list.some((x) => idLastDigit(x) >= 0)
  if (hasUsableId) {
    const sorted = [...list].sort((a, b) => {
      const bd = idLastDigit(b)
      const ad = idLastDigit(a)
      if (bd !== ad) return bd - ad
      return String(b?.publishedAt || '').localeCompare(String(a?.publishedAt || ''))
    })
    return sorted[0]
  }

  const hasDate = list.some((x) => x?.publishedAt)
  if (hasDate) {
    const sorted = [...list].sort((a, b) => String(b?.publishedAt || '').localeCompare(String(a?.publishedAt || '')))
    return sorted[0]
  }

  return list[0]
}

onMounted(async () => {
  try {
    const list = await listNews({ limit: 20, offset: 0 })
    latest.value = pickLatest(list)
  } catch {
    latest.value = null
  }
})

const displayText = computed(() => {
  const x = latest.value
  const title = String(x?.title || '').trim()
  if (title) return title
  const slug = String(x?.slug || '').trim()
  if (slug) return slug
  return props.summary
})
</script>

<style scoped>
.news-card {
  appearance: none;
  border: none;
  background: transparent;
  color: #111827;
  border-radius: 999px;
  padding: 1px; /* 彩色描边厚度（更扁平） */
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  min-height: 36px;
  width: min(400px, 100%);
  cursor: pointer;
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), border-color 0.15s ease, box-shadow 0.2s ease,
    background 0.15s ease;
  position: relative;
  isolation: isolate;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

.news-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 999px;
  z-index: 0;
  background: linear-gradient(
    90deg,
    #a855f7 0%,
    #ec4899 25%,
    #f97316 50%,
    #22c55e 75%,
    #a855f7 100%
  );
  /* 固定渐变，动画用 hue-rotate 做无缝流转，避免首尾突兀 */
  filter: saturate(1.05);
  will-change: filter;
}

.news-card::after {
  content: '';
  position: absolute;
  inset: 1px; /* 留出描边 */
  border-radius: 999px;
  z-index: 1;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.06);
  transition: background 0.15s ease, box-shadow 0.15s ease;
}

.news-card > * {
  position: relative;
  z-index: 2;
}

.inner {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 7px 16px; /* 内部左右留白（更扁平） */
  border-radius: 999px;
  min-width: 0;
}

.news-card:hover {
  transform: translateY(-2px) scale(1.02);
}

.news-card:hover::after {
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 14px 32px rgba(0, 0, 0, 0.08);
}

.news-card:active {
  transform: translateY(0) scale(0.97);
  transition: transform 0.1s cubic-bezier(0.4, 0, 0.2, 1);
}

.news-card:active::after {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.news-card:focus-visible {
  outline: 2px solid rgba(147, 51, 234, 0.55);
  outline-offset: 2px;
}

.news-card:hover::before,
.news-card:active::before,
.news-card:focus-visible::before {
  animation: border-hue 1.2s linear infinite;
}

.left,
.summary {
  min-width: 0;
}

.left {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.summary {
  flex: 1 1 auto;
  font-size: 14px;
  font-weight: 500;
  color: rgba(17, 24, 39, 0.9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.label {
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-weight: 700;
}

.icon {
  width: 24px;
  height: 24px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(17, 24, 39, 0.06);
}

@keyframes border-hue {
  from {
    filter: saturate(1.05) hue-rotate(0deg);
  }
  to {
    filter: saturate(1.05) hue-rotate(360deg);
  }
}

@media (max-width: 900px) {
  .news-card {
    min-height: 42px;
  }

  .inner {
    gap: 10px;
    padding: 6px 11px;
  }

  .left {
    flex: 0 0 auto;
    gap: 6px;
  }

  .label {
    white-space: nowrap;
    font-size: 11px;
    letter-spacing: 0.08em;
  }

  .summary {
    font-size: 13px;
  }

  .icon {
    width: 22px;
    height: 22px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .news-card:hover::before,
  .news-card:active::before,
  .news-card:focus-visible::before {
    animation: none;
  }
}
</style>


