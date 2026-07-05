<template>
  <section class="detail-page">

    
    <div class="detail-container">
      <button
        class="back-btn"
        :class="{ 'is-open': isBackOpen, 'is-pressed': isBackPressed, 'is-dragging': isBackDragging }"
        type="button"
        :aria-label="backAriaLabel"
        @click="onBack"
        @pointerenter="openBack()"
        @pointerleave="onBackPointerLeave"
        @focusin="openBack()"
        @focusout="closeBackNow()"
        @pointerdown="onBackPointerDown"
        @pointermove="onBackPointerMove"
        @pointerup="onBackPointerUp"
        @pointercancel="onBackPointerCancel"
        :style="backBtnStyle"
      >
        <span v-show="!isBackOpen" class="back-btn__chev back-btn__chev--right" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path
              d="M729.6 448H128v85.333333h601.6L597.333333 665.6l59.733334 59.733333 234.666666-234.666666L661.333333 256l-59.733333 59.733333 128 132.266667z"
              fill="currentColor"
            ></path>
          </svg>
        </span>

        <span v-show="isBackOpen" class="back-btn__chev back-btn__chev--left" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path
              d="M290.133333 448H896v85.333333H290.133333l132.266667 132.266667L362.666667 725.333333 128 490.666667 362.666667 256l59.733333 59.733333-132.266667 132.266667z"
              fill="currentColor"
            ></path>
          </svg>
        </span>

        <span v-show="isBackOpen" class="back-btn__text">{{ backText }}</span>
      </button>

      <div v-if="isLoading" class="loading" role="status" aria-live="polite">
        Loading…
      </div>

      <div v-else-if="article" class="detail">
        <header class="hero" aria-label="Article header">
          <div class="hero-meta reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '90ms' }" role="group" aria-label="Article meta">
            <time class="hero-meta__item" :datetime="article.publishedAt">
              {{ formatDateLong(article.publishedAt, i18n.locale) }}
            </time>
            <span class="hero-meta__dot" aria-hidden="true"></span>
            <span class="hero-meta__item">{{ t(`news.categories.${article.category}`) }}</span>
          </div>

          <h1 class="hero-title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '150ms' }">{{ article.title }}</h1>
          <p v-if="dekText" class="hero-dek reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '220ms' }">
            {{ dekText }}
          </p>

          <!-- 封面图 -->
          <div v-if="coverImageUrl" class="hero-cover reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '280ms' }">
            <img :src="coverImageUrl" :alt="article.title" class="hero-cover__img" />
          </div>
        </header>

        <div class="divider reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '300ms' }" aria-hidden="true"></div>

        <div class="actions reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '360ms' }">
          <button class="share-btn" type="button" @click="onShare" :aria-label="shareAria">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M10 13a5 5 0 0 0 7.07 0l1.41-1.41a5 5 0 0 0-7.07-7.07L10.5 4.4"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path
                d="M14 11a5 5 0 0 0-7.07 0L5.5 12.4a5 5 0 0 0 7.07 7.07L13.5 18.6"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            <span class="share-text">{{ shareLabel }}</span>
          </button>
        </div>

        <div class="content">
          <template v-for="(item, idx) in contentItems" :key="idx">
            <!-- 文字段落 -->
            <p
              v-if="item.type === 'text'"
              class="para reveal"
              :class="{ 'is-in': pageEnter }"
              :style="{ '--d': `${Math.min(900, 420 + idx * 70)}ms` }"
            >
              {{ item.content }}
            </p>
            <!-- 图片 -->
            <figure
              v-else-if="item.type === 'image'"
              class="content-figure reveal"
              :class="{ 'is-in': pageEnter }"
              :style="{ '--d': `${Math.min(900, 420 + idx * 70)}ms` }"
            >
              <img :src="item.url" :alt="item.caption || 'Article image'" class="content-img" />
              <figcaption v-if="item.caption" class="content-caption">{{ item.caption }}</figcaption>
            </figure>
          </template>
        </div>
      </div>

      <div v-else class="not-found">
        <h1 class="nf-title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '120ms' }">Not found</h1>
        <p class="nf-text reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '180ms' }">
          This article does not exist or has been removed.
        </p>
        <button class="nf-back reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '240ms' }" type="button" @click="router.push('/news')">
          Back to News
        </button>
      </div>
    </div>
  </section>
  
  <!-- 添加Third和End组件 -->
  <Third />
  <End />
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'
import { formatDateLong, getNewsBySlug } from '@/services/newsService'
import { useErrorStore } from '@/stores/error'
import Third from '@/page_components/Third.vue'
import End from '@/page_components/End.vue'


const route = useRoute()
const router = useRouter()
const i18n = useI18nStore()
const t = (key, vars) => i18n.t(key, vars)
const errorStore = useErrorStore()

const pageEnter = ref(false)
const article = ref(null)
const isLoading = ref(false)

const isBackOpen = ref(false)
let backCloseTimerId = null
const isBackPressed = ref(false)
const isBackDragging = ref(false)
const suppressBackClickOnce = ref(false)
const backDragX = ref(0)
const backDragY = ref(0)
let backPointerId = null
let backStartClientX = 0
let backStartClientY = 0
let backStartDragX = 0
let backStartDragY = 0
let backMoved = false

const backText = computed(() => (i18n.locale === 'zh' ? '返回' : 'BACK'))
const backAriaLabel = computed(() => (i18n.locale === 'zh' ? '返回' : 'Back'))
const backBtnStyle = computed(() => ({
  '--drag-x': `${backDragX.value}px`,
  '--drag-y': `${backDragY.value}px`,
}))

function openBack(fromPointerDown = false) {
  isBackOpen.value = true
  if (backCloseTimerId) {
    window.clearTimeout(backCloseTimerId)
    backCloseTimerId = null
  }
}

function scheduleCloseBack() {
  if (backCloseTimerId) window.clearTimeout(backCloseTimerId)
  backCloseTimerId = window.setTimeout(() => {
    isBackOpen.value = false
    backCloseTimerId = null
  }, 900)
}

function closeBackNow() {
  if (backCloseTimerId) {
    window.clearTimeout(backCloseTimerId)
    backCloseTimerId = null
  }
  isBackOpen.value = false
}

function onBack() {
  if (suppressBackClickOnce.value) {
    suppressBackClickOnce.value = false
    return
  }
  // "Back" semantics: prefer real history back; fallback to News list.
  if (window.history.length > 1) router.back()
  else router.push({ name: 'news' })
}

function onBackPointerDown(e) {
  // Left-click / touch / pen only
  if (e.button != null && e.button !== 0) return

  openBack(true)
  isBackPressed.value = true
  isBackDragging.value = true
  suppressBackClickOnce.value = false

  backPointerId = e.pointerId
  backStartClientX = e.clientX
  backStartClientY = e.clientY
  backStartDragX = backDragX.value
  backStartDragY = backDragY.value
  backMoved = false

  try {
    e.currentTarget?.setPointerCapture?.(e.pointerId)
  } catch {
    // no-op
  }
}

function onBackPointerLeave(e) {
  // While pressed/dragging (especially on touch), do not collapse.
  if (isBackDragging.value || isBackPressed.value) return
  closeBackNow()
}

function onBackPointerMove(e) {
  if (!isBackDragging.value) return
  if (backPointerId == null || e.pointerId !== backPointerId) return

  const dx = e.clientX - backStartClientX
  const dy = e.clientY - backStartClientY

  if (!backMoved && Math.hypot(dx, dy) >= 6) backMoved = true

  backDragX.value = backStartDragX + dx
  backDragY.value = backStartDragY + dy
}

function endBackDrag(e, { cancelled } = { cancelled: false }) {
  if (backPointerId != null) {
    try {
      e?.currentTarget?.releasePointerCapture?.(backPointerId)
    } catch {
      // no-op
    }
  }

  backPointerId = null
  isBackDragging.value = false
  isBackPressed.value = false

  // If user actually dragged, prevent the "click" from firing navigation.
  if (backMoved) suppressBackClickOnce.value = true

  // Force snap-back to the left edge only (keep vertical position)
  backDragX.value = 0
  backMoved = false

  if (!cancelled) scheduleCloseBack()
  else closeBackNow()
}

function onBackPointerUp(e) {
  endBackDrag(e, { cancelled: false })
}

function onBackPointerCancel(e) {
  endBackDrag(e, { cancelled: true })
}

onBeforeUnmount(() => {
  if (backCloseTimerId) window.clearTimeout(backCloseTimerId)
})

async function triggerEnterAnimation() {
  pageEnter.value = false
  await nextTick()
  requestAnimationFrame(() => {
    pageEnter.value = true
  })
}

async function loadArticle() {
  const slug = String(route.params.slug || '')
  if (!slug) {
    article.value = null
    return
  }

  // Ensure we don't start animations until content is ready
  pageEnter.value = false
  isLoading.value = true
  try {
    article.value = await getNewsBySlug(slug)
    if (!article.value) {
      // Silent not-found; UI will show the not-found block
    }
  } catch (e) {
    errorStore.showError(e?.message || 'Failed to load article')
    article.value = null
  } finally {
    isLoading.value = false
  }

  // Start reveal only after DOM has rendered new content
  await triggerEnterAnimation()
}

onMounted(() => {
  loadArticle()
})

watch(
  () => route.params.slug,
  () => {
    loadArticle()
  }
)

const dekConfig = computed(() => {
  const a = article.value
  if (!a) return { text: '', stripFromBody: false }

  // Allow future extension: if your backend adds subtitle/summary, it will render here automatically.
  const fromField = a.subtitle || a.summary || a.dek
  if (typeof fromField === 'string' && fromField.trim()) {
    return { text: fromField.trim(), stripFromBody: false }
  }

  // Fallback: use the first content paragraph as the "dek" (and remove it from body to avoid duplication)
  const first = Array.isArray(a.content) ? a.content[0] : ''
  return { text: typeof first === 'string' ? first.trim() : '', stripFromBody: true }
})

const dekText = computed(() => dekConfig.value.text)

const bodyParagraphs = computed(() => {
  const a = article.value
  if (!a || !Array.isArray(a.content)) return []
  if (dekConfig.value.stripFromBody) return a.content.slice(1)
  return a.content
})

// 封面图URL
const coverImageUrl = computed(() => {
  const a = article.value
  if (!a) return null
  // 支持多种字段名
  return a.cover_image || a.coverImage || a.cover || null
})

// 内容图片数组
const articleImages = computed(() => {
  const a = article.value
  if (!a) return []
  // 支持多种字段名
  const images = a.images || a.contentImages || a.content_images || []
  if (!Array.isArray(images)) return []
  return images
})

// 将段落和图片合并为统一的内容项数组
const contentItems = computed(() => {
  const paragraphs = bodyParagraphs.value
  const images = articleImages.value
  const items = []

  // 创建图片位置映射
  const imageByPosition = {}
  images.forEach((img) => {
    const pos = img.position ?? img.index ?? -1
    if (pos >= 0) {
      imageByPosition[pos] = img
    }
  })

  // 遍历段落，检查是否有 [IMAGE:n] 标记或按位置插入图片
  paragraphs.forEach((p, idx) => {
    const text = String(p || '').trim()
    
    // 检查是否是图片标记 [IMAGE:n]
    const imageTagMatch = text.match(/^\[IMAGE:(\d+)\]$/)
    if (imageTagMatch) {
      const imgIndex = parseInt(imageTagMatch[1], 10)
      const img = images[imgIndex]
      if (img) {
        items.push({
          type: 'image',
          url: img.url,
          caption: img.caption || '',
        })
      }
      return
    }

    // 普通文字段落
    if (text) {
      items.push({
        type: 'text',
        content: text,
      })
    }

    // 检查是否有图片应该插入在这个段落后面
    if (imageByPosition[idx]) {
      const img = imageByPosition[idx]
      items.push({
        type: 'image',
        url: img.url,
        caption: img.caption || '',
      })
    }
  })

  // 如果没有使用位置标记，且有图片，将剩余图片添加到末尾
  const usedPositions = new Set(Object.keys(imageByPosition).map(Number))
  const hasPositionedImages = usedPositions.size > 0
  
  if (!hasPositionedImages && images.length > 0) {
    // 检查是否已经通过 [IMAGE:n] 标记添加了图片
    const addedImageUrls = new Set(
      items.filter((i) => i.type === 'image').map((i) => i.url)
    )
    
    images.forEach((img) => {
      if (!addedImageUrls.has(img.url)) {
        items.push({
          type: 'image',
          url: img.url,
          caption: img.caption || '',
        })
      }
    })
  }

  return items
})

const shareLabel = ref('Share')
const shareAria = computed(() =>
  shareLabel.value === 'Copied' ? 'Link copied' : 'Share this article'
)

async function copyToClipboard(text) {
  if (navigator?.clipboard?.writeText) {
    await navigator.clipboard.writeText(text)
    return
  }
  // Legacy fallback
  const ta = document.createElement('textarea')
  ta.value = text
  ta.setAttribute('readonly', '')
  ta.style.position = 'fixed'
  ta.style.top = '-9999px'
  document.body.appendChild(ta)
  ta.select()
  document.execCommand('copy')
  document.body.removeChild(ta)
}

async function onShare() {
  const a = article.value
  if (!a) return

  const url = window.location.href

  try {
    if (navigator?.share) {
      await navigator.share({ title: a.title, url })
      return
    }
    await copyToClipboard(url)
    shareLabel.value = 'Copied'
    window.setTimeout(() => {
      shareLabel.value = 'Share'
    }, 1600)
  } catch {
    // no-op: keep UI silent
  }
}
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

.detail-page {
  background: #fbfbfb;
  padding: 120px 24px 80px;
}



.detail-container {
  max-width: 1100px;
  margin: 0 auto;
}

.back-btn {
  position: fixed;
  top: 96px; /* below fixed NavBar */
  left: 0;
  z-index: 30;
  height: 38px;
  width: 44px;
  padding: 0 12px;
  border-radius: 0 999px 999px 0;
  border: 2px solid #000000;
  background: #ffffff;
  color: #000000;
  cursor: grab;
  font-weight: 800;
  letter-spacing: 0.08em;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  overflow: hidden;
  user-select: none;
  touch-action: none;
  transition:
    width 240ms cubic-bezier(0.16, 1, 0.3, 1),
    background-color 0.15s ease,
    color 0.15s ease,
    transform 0.18s ease,
    box-shadow 0.15s ease;
  will-change: width;
  transform: translate3d(var(--drag-x, 0px), var(--drag-y, 0px), 0) scale(1);
}

.back-btn.is-open {
  width: 142px;
  justify-content: flex-start;
  padding: 0 16px 0 12px;
}

.back-btn:hover {
  background: #000000;
  color: #ffffff;
}

.back-btn.is-pressed,
.back-btn:active {
  background: #000000;
  color: #ffffff;
  transform: translate3d(var(--drag-x, 0px), var(--drag-y, 0px), 0) scale(0.98);
}

.back-btn:focus-visible {
  outline: 2px solid rgba(0, 0, 0, 0.6);
  outline-offset: 3px;
}

.back-btn.is-dragging {
  cursor: grabbing;
  transition:
    width 240ms cubic-bezier(0.16, 1, 0.3, 1),
    background-color 0.15s ease,
    color 0.15s ease,
    box-shadow 0.15s ease;
}

.back-btn__icon {
  width: 16px;
  height: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.back-btn__chev {
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 18px;
  transition:
    opacity 160ms ease,
    transform 240ms cubic-bezier(0.16, 1, 0.3, 1);
}

.back-btn__chev--right {
  opacity: 1;
  transform: translate3d(0, 0, 0);
}

.back-btn__chev--left {
  opacity: 0;
  transform: translate3d(-8px, 0, 0);
}

.back-btn.is-open .back-btn__chev--right {
  opacity: 0;
  transform: translate3d(10px, 0, 0);
}

.back-btn.is-open .back-btn__chev--left {
  opacity: 1;
  transform: translate3d(0, 0, 0);
}

.back-btn__text {
  white-space: nowrap;
  font-size: 12px;
  line-height: 1;
  opacity: 0;
  transform: translate3d(-10px, 0, 0);
  transition:
    opacity 160ms ease,
    transform 240ms cubic-bezier(0.16, 1, 0.3, 1);
}

.back-btn.is-open .back-btn__text {
  opacity: 1;
  transform: translate3d(0, 0, 0);
}

.loading {
  padding: 28px 0;
  color: rgba(17, 24, 39, 0.62);
  font-size: 14px;
}

.detail {
  padding-top: 6px;
}

.hero {
  text-align: center;
  padding: 8px 0 0;
}

.hero-meta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  font-size: 16px;
  line-height: 1.4;
  color: rgba(17, 24, 39, 0.58);
  margin-bottom: 28px;
}

.hero-meta__item {
  white-space: nowrap;
}

.hero-meta__dot {
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.36);
}

.hero-title {
  margin: 0 auto;
  max-width: min(1100px, 100%);
  font-size: 64px;
  line-height: 1.12;
  letter-spacing: 0.01em;
  font-weight: 650;
  color: #0b0f19;
}

.hero-dek {
  margin: 28px auto 0;
  max-width: 860px;
  font-size: 20px;
  line-height: 1.7;
  color: rgba(17, 24, 39, 0.72);
}

.divider {
  height: 1px;
  background: rgba(17, 24, 39, 0.12);
  margin: 52px 0 18px;
}

.actions {
  max-width: 860px;
  margin: 0 auto 46px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.share-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  border: 0;
  background: transparent;
  padding: 8px 6px;
  color: rgba(17, 24, 39, 0.78);
  cursor: pointer;
  border-radius: 10px;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.share-btn:hover,
.share-btn:focus-visible {
  background: rgba(17, 24, 39, 0.06);
  color: rgba(17, 24, 39, 0.92);
  outline: none;
}

.share-text {
  font-size: 16px;
  line-height: 1.2;
  font-weight: 600;
}

.content {
  max-width: 860px;
  margin: 0 auto;
}

.para {
  margin: 0 0 18px;
  font-size: 18px;
  line-height: 1.8;
  color: rgba(17, 24, 39, 0.78);
}

.not-found {
  padding: 36px 0;
}

.nf-title {
  margin: 0 0 10px;
  font-size: 40px;
}

.nf-text {
  margin: 0 0 18px;
  color: rgba(17, 24, 39, 0.7);
}

.nf-back {
  height: 40px;
  padding: 0 14px;
  border-radius: 10px;
  border: 1px solid rgba(17, 24, 39, 0.12);
  background: #fff;
  cursor: pointer;
}

/* 封面图样式 */
.hero-cover {
  margin: 36px auto 0;
  max-width: 960px;
  border-radius: 16px;
  overflow: hidden;
  background: #f0f0f0;
}

.hero-cover__img {
  width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
  max-height: 540px;
}

/* 内容图片样式 */
.content-figure {
  margin: 28px 0;
  padding: 0;
}

.content-img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 12px;
  background: #f0f0f0;
}

.content-caption {
  margin-top: 12px;
  font-size: 14px;
  line-height: 1.5;
  color: rgba(17, 24, 39, 0.55);
  text-align: center;
}
</style>


