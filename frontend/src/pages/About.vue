<template>
  <div class="about-wrapper" ref="wrapperRef">
    <div class="about-container" :style="{ transform: `translateY(-${currentPage * 100}vh)` }">
      <div class="about-section">
        <AboutOne />
      </div>
      <div class="about-section">
        <AboutTwo ref="aboutTwoRef" />
      </div>
      <div class="about-section">
        <AboutThree ref="aboutThreeRef" />
      </div>
      <div class="about-section">
        <AboutFour ref="aboutFourRef" />
      </div>
    </div>
    
    <!-- 页面指示器 -->
    <div class="page-indicators">
      <button 
        v-for="(_, idx) in totalPages" 
        :key="idx"
        class="indicator"
        :class="{ active: currentPage === idx }"
        @click="goToPage(idx)"
        :aria-label="`Go to page ${idx + 1}`"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import AboutOne from '@/page_components/About_one.vue'
import AboutTwo from '@/page_components/About_two.vue'
import AboutThree from '@/page_components/About_three.vue'
import AboutFour from '@/page_components/About_four.vue'

const wrapperRef = ref(null)
const aboutTwoRef = ref(null)
const aboutThreeRef = ref(null)
const aboutFourRef = ref(null)
const currentPage = ref(0)
const totalPages = 4
const isAnimating = ref(false)

let lastWheelTime = 0
const wheelThrottle = 800 // 翻页动画节流时间
let mobileMediaQuery = null

// ====== About 2/3/4 远程图片预加载（提前缓存，避免首次进入时闪动/布局跳变）======
const ABOUT_IMG_BASE = 'https://pages-1327732770.cos.ap-guangzhou.myqcloud.com/about'
const IMG_VERSION = 'v2' // 更新图片后修改此版本号以刷新缓存
const ABOUT_IMG_URLS = [
  // `${ABOUT_IMG_BASE}/1.jpg`,
  // `${ABOUT_IMG_BASE}/2.jpg`,
  // `${ABOUT_IMG_BASE}/3.jpg`,
  `${ABOUT_IMG_BASE}/5.jpg?${IMG_VERSION}`,
  `${ABOUT_IMG_BASE}/6.jpg?${IMG_VERSION}`
]

const _preloaded = new Set()
const preloadImage = (url) => {
  if (!url || _preloaded.has(url)) return
  _preloaded.add(url)
  const img = new Image()
  img.decoding = 'async'
  img.src = url
}

const schedulePreload = (urls) => {
  const run = () => urls.forEach(preloadImage)
  if (typeof window !== 'undefined' && typeof window.requestIdleCallback === 'function') {
    window.requestIdleCallback(run, { timeout: 2000 })
  } else {
    setTimeout(run, 400)
  }
}

const preconnectAboutHost = () => {
  if (typeof document === 'undefined') return
  const href = ABOUT_IMG_BASE.replace(/\/about$/, '')
  const ensureLink = (rel) => {
    if (document.head.querySelector(`link[rel="${rel}"][href="${href}"]`)) return
    const link = document.createElement('link')
    link.rel = rel
    link.href = href
    document.head.appendChild(link)
  }
  ensureLink('dns-prefetch')
  ensureLink('preconnect')
}

const handleWheel = (e) => {
  if (mobileMediaQuery?.matches) return
  e.preventDefault()
  
  const now = Date.now()
  if (now - lastWheelTime < wheelThrottle || isAnimating.value) return
  
  const delta = e.deltaY
  
  if (delta > 30 && currentPage.value < totalPages - 1) {
    // 向下滚动
    lastWheelTime = now
    goToPage(currentPage.value + 1)
  } else if (delta < -30 && currentPage.value > 0) {
    // 向上滚动
    lastWheelTime = now
    goToPage(currentPage.value - 1)
  }
}

const goToPage = (page) => {
  if (page < 0 || page >= totalPages || isAnimating.value) return
  
  isAnimating.value = true
  currentPage.value = page
  
  // 触发对应页面的动画
  if (page === 1 && aboutTwoRef.value) {
    setTimeout(() => {
      aboutTwoRef.value.show()
    }, 300)
  }
  if (page === 2 && aboutThreeRef.value) {
    setTimeout(() => {
      aboutThreeRef.value.show()
    }, 300)
  }
  if (page === 3 && aboutFourRef.value) {
    setTimeout(() => {
      aboutFourRef.value.show()
    }, 300)
  }
  
  setTimeout(() => {
    isAnimating.value = false
  }, wheelThrottle)
}

// 键盘支持
const handleKeydown = (e) => {
  if (mobileMediaQuery?.matches) return
  if (e.key === 'ArrowDown' || e.key === 'PageDown') {
    e.preventDefault()
    if (currentPage.value < totalPages - 1) {
      goToPage(currentPage.value + 1)
    }
  } else if (e.key === 'ArrowUp' || e.key === 'PageUp') {
    e.preventDefault()
    if (currentPage.value > 0) {
      goToPage(currentPage.value - 1)
    }
  }
}

const syncSectionVisibility = () => {
  const sectionRefs = [aboutTwoRef.value, aboutThreeRef.value, aboutFourRef.value]

  if (mobileMediaQuery?.matches) {
    sectionRefs.forEach((sectionRef) => sectionRef?.show?.())
    return
  }

  sectionRefs.forEach((sectionRef, index) => {
    if (currentPage.value === index + 1) sectionRef?.show?.()
    else sectionRef?.hide?.()
  })
}

onMounted(() => {
  mobileMediaQuery = window.matchMedia('(max-width: 900px)')
  mobileMediaQuery.addEventListener('change', syncSectionVisibility)
  requestAnimationFrame(syncSectionVisibility)

  const wrapper = wrapperRef.value
  if (wrapper) {
    wrapper.addEventListener('wheel', handleWheel, { passive: false })
  }
  window.addEventListener('keydown', handleKeydown)

  // 页面挂载后就开始“空闲预加载”，用户滚到第2/3/4屏时基本都是缓存命中
  preconnectAboutHost()
  schedulePreload(ABOUT_IMG_URLS)
})

onBeforeUnmount(() => {
  mobileMediaQuery?.removeEventListener('change', syncSectionVisibility)
  mobileMediaQuery = null

  const wrapper = wrapperRef.value
  if (wrapper) {
    wrapper.removeEventListener('wheel', handleWheel)
  }
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.about-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: #ffffff;
}

.about-container {
  width: 100%;
  transition: transform 0.8s cubic-bezier(0.65, 0, 0.35, 1);
  will-change: transform;
}

.about-section {
  width: 100%;
  height: 100vh;
  background: #ffffff;
}

/* 页面指示器 */
.page-indicators {
  position: fixed;
  right: 30px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 100;
}

.indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid rgba(0, 0, 0, 0.3);
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
}

.indicator:hover {
  border-color: rgba(0, 0, 0, 0.6);
  transform: scale(1.2);
}

.indicator.active {
  background: #000;
  border-color: #000;
}

@media (max-width: 900px) {
  .about-wrapper {
    position: relative;
    height: auto;
    min-height: 100svh;
    overflow: visible;
  }

  .about-container {
    transform: none !important;
    transition: none;
  }

  .about-section {
    height: auto;
    min-height: 100svh;
  }

  .page-indicators {
    display: none;
  }
}
</style>
