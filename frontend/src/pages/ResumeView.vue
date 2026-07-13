<template>
  <section class="resume-page">
    <div class="resume-container">
      <!-- Loading -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <span>{{ isZh ? '加载中...' : 'Loading...' }}</span>
      </div>

      <!-- Error / Not found -->
      <div v-else-if="errorMsg" class="error-state">
        <p>{{ errorMsg }}</p>
        <button class="btn ghost" @click="router.push('/team')">{{ isZh ? '返回团队' : 'Back to Team' }}</button>
      </div>

      <!-- Resume content -->
      <template v-else-if="resume">
        <main class="preview reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }">
          <div class="detail">
            <header class="hero">
              <div class="avatar-section">
                <div class="avatar-circle" :class="{ 'avatar-loading': avatarUrl && !avatarLoaded }">
                  <img 
                    v-if="avatarUrl" 
                    :src="avatarUrl" 
                    alt="avatar"
                    loading="eager"
                    @load="onAvatarLoad"
                  />
                  <div v-else class="avatar-letter">{{ avatarLetter }}</div>
                  <div class="avatar-skeleton"></div>
                </div>
              </div>
              <h1 class="hero-title">{{ resume.real_name || (isZh ? '未设置' : 'Not set') }}</h1>
              <p v-if="resume.job_title" class="hero-dek">{{ resume.job_title }}</p>
              <p v-if="resume.department" class="hero-dept">{{ resume.department }}</p>
            </header>

            <div class="divider"></div>

            <!-- Basic info -->
            <div class="content">
              <div class="section-label">{{ isZh ? '基本信息' : 'Basic Information' }}</div>
              <div class="info-grid">
                <div v-if="resume.age" class="info-item">
                  <span class="info-label">{{ isZh ? '年龄' : 'Age' }}</span>
                  <span class="info-value">{{ resume.age }}</span>
                </div>
                <div v-if="resume.education" class="info-item">
                  <span class="info-label">{{ isZh ? '学历' : 'Education' }}</span>
                  <span class="info-value">{{ resume.education }}</span>
                </div>
                <div v-if="resume.address" class="info-item">
                  <span class="info-label">{{ isZh ? '所在地' : 'Location' }}</span>
                  <span class="info-value">{{ resume.address }}</span>
                </div>
                <div v-if="resume.email" class="info-item">
                  <span class="info-label">{{ isZh ? '邮箱' : 'Email' }}</span>
                  <span class="info-value">{{ resume.email }}</span>
                </div>
                <div v-if="resume.phone" class="info-item">
                  <span class="info-label">{{ isZh ? '电话' : 'Phone' }}</span>
                  <span class="info-value">{{ resume.phone }}</span>
                </div>
              </div>
            </div>

            <!-- Bio content -->
            <template v-if="bioContent.length">
              <div class="divider"></div>
              <div class="content">
                <div class="section-label">{{ isZh ? '个人简历' : 'Resume' }}</div>
                <div class="bio-blocks">
                  <template v-for="(block, idx) in bioContent" :key="idx">
                    <p v-if="block.type === 'text'" class="bio-text">{{ block.content }}</p>
                    <div v-else-if="block.type === 'image'" class="bio-image-wrapper" :class="{ 'image-loading': !isBioImageLoaded(block.url) }">
                      <img 
                        :src="block.url" 
                        alt="Bio image" 
                        class="bio-image"
                        loading="lazy"
                        @load="onBioImageLoad(block.url)"
                      />
                      <div class="image-skeleton"></div>
                    </div>
                  </template>
                </div>
              </div>
            </template>
          </div>
        </main>
      </template>
    </div>

    <!-- Bottom bar -->
    <div class="bottom-bar">
      <div class="bottom-inner">
        <div class="bottom-left">
          <div class="bottom-title">{{ resume?.real_name || (isZh ? '简历' : 'Resume') }}</div>
          <div class="bottom-sub">{{ resume?.job_title || '' }}</div>
        </div>
        <div class="bottom-right">
          <button class="btn ghost" @click="router.push('/team')">{{ isZh ? '返回团队' : 'Back to Team' }}</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'
import { getPublicResume } from '@/services/resumeService'
import { preloadImagesInBackground } from '@/utils/imagePreloader'

const router = useRouter()
const route = useRoute()
const i18n = useI18nStore()

const isZh = computed(() => i18n.locale === 'zh')
const pageEnter = ref(false)
const isLoading = ref(true)
const errorMsg = ref('')
const resume = ref(null)
const avatarLoaded = ref(false)
const loadedImages = ref(new Set())

const avatarUrl = computed(() => {
  const r = resume.value
  return r?.avatar_url || r?.avatarUrl || r?.avatar || ''
})

const avatarLetter = computed(() => {
  const s = String(resume.value?.real_name || 'U').trim()
  return (s[0] || 'U').toUpperCase()
})

// 头像加载完成
function onAvatarLoad() {
  avatarLoaded.value = true
}

// Bio图片加载完成
function onBioImageLoad(url) {
  loadedImages.value.add(url)
}

// 检查Bio图片是否已加载
function isBioImageLoaded(url) {
  return loadedImages.value.has(url)
}

// Parse bio content with images
const bioContent = computed(() => {
  const r = resume.value
  if (!r) return []
  
  const bioArr = Array.isArray(r.bio) ? r.bio : []
  const bioImages = Array.isArray(r.bio_images) ? r.bio_images : []
  
  // Build image map by position
  const imageMap = {}
  bioImages.forEach(img => {
    const pos = img.position ?? img.display_order ?? 0
    imageMap[pos] = img.url || img.image_url || ''
  })
  
  const imagePattern = /^\[IMAGE:(\d+)\]$/
  return bioArr.map(text => {
    const match = String(text).match(imagePattern)
    if (match) {
      const position = parseInt(match[1], 10)
      return { type: 'image', url: imageMap[position] || '' }
    }
    return { type: 'text', content: text }
  }).filter(b => b.type === 'image' ? b.url : b.content)
})

async function loadResume() {
  const userId = route.params.userId
  if (!userId) {
    errorMsg.value = isZh.value ? '缺少用户ID' : 'Missing user ID'
    isLoading.value = false
    return
  }
  
  try {
    const data = await getPublicResume(userId)
    if (!data) {
      errorMsg.value = isZh.value ? '简历不存在或未公开' : 'Resume not found or private'
    } else {
      resume.value = data
      
      // 数据加载完成后，立即预加载所有图片
      const imagesToPreload = []
      const avatar = data.avatar_url || data.avatarUrl || data.avatar
      if (avatar) imagesToPreload.push(avatar)
      
      // 预加载bio中的图片
      const bioImages = Array.isArray(data.bio_images) ? data.bio_images : []
      bioImages.forEach(img => {
        const url = img.url || img.image_url
        if (url) imagesToPreload.push(url)
      })
      
      preloadImagesInBackground(imagesToPreload)
    }
  } catch (e) {
    if (e?.status === 404) {
      errorMsg.value = isZh.value ? '简历不存在或未公开' : 'Resume not found or private'
    } else {
      errorMsg.value = isZh.value ? `加载失败：${e?.message || e}` : `Load failed: ${e?.message || e}`
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  setTimeout(() => { pageEnter.value = true }, 100)
  loadResume()
})
</script>


<style scoped>
.reveal {
  opacity: 0;
  transform: translate3d(0, 22px, 0);
  filter: blur(10px);
  transition: opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1), transform 0.9s cubic-bezier(0.16, 1, 0.3, 1), filter 0.9s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--d, 0ms);
}
.reveal.is-in { opacity: 1; transform: translate3d(0, 0, 0); filter: blur(0); }

.resume-page { min-height: 100vh; background: #ffffff; }
.resume-container { max-width: 1400px; margin: 0 auto; padding: 120px 24px 148px; }

/* Loading & Error */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 100px 0;
  color: #64748b;
}
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #0f172a;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.preview { min-width: 0; }
.detail { padding-top: 16px; }

/* Hero */
.hero { text-align: center; padding: 16px 0 0; }
.avatar-section { display: flex; justify-content: center; margin-bottom: 32px; }
.avatar-circle {
  width: 140px;
  height: 140px;
  border-radius: 999px;
  overflow: hidden;
  border: 4px solid #fff;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.2);
  display: grid;
  place-items: center;
  position: relative;
}
.avatar-circle img { 
  width: 100%; 
  height: 100%; 
  object-fit: cover;
  opacity: 1;
  transition: opacity 0.4s ease;
}
.avatar-circle.avatar-loading img {
  opacity: 0;
}

/* 头像骨架屏 */
.avatar-skeleton {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
  border-radius: 999px;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.avatar-circle.avatar-loading .avatar-skeleton {
  opacity: 1;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.avatar-letter {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  font-size: 48px;
  font-weight: 950;
  color: rgba(15, 23, 42, 0.82);
  background: radial-gradient(140px 140px at 30% 20%, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.55));
}

.hero-title {
  margin: 0 auto;
  max-width: min(1100px, 100%);
  font-size: 72px;
  line-height: 1.08;
  letter-spacing: -0.02em;
  font-weight: 700;
  color: #000000;
}
.hero-dek {
  margin: 24px auto 0;
  max-width: 860px;
  font-size: 24px;
  line-height: 1.6;
  color: rgba(0, 0, 0, 0.7);
}
.hero-dept {
  margin: 10px auto 0;
  font-size: 18px;
  color: rgba(0, 0, 0, 0.5);
}

.divider { height: 1px; background: rgba(0, 0, 0, 0.12); margin: 60px 0 24px; }

.content { max-width: 860px; margin: 0 auto; }
.section-label {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: #000000;
  margin-bottom: 24px;
}

/* Info grid */
.info-grid { display: flex; flex-wrap: wrap; gap: 28px 56px; }
.info-item { display: flex; flex-direction: column; gap: 6px; }
.info-label { font-size: 13px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(0, 0, 0, 0.5); }
.info-value { font-size: 18px; color: #000000; }

/* Bio blocks */
.bio-blocks { display: flex; flex-direction: column; gap: 28px; }
.bio-text { font-size: 20px; line-height: 1.9; color: #000000; margin: 0; }

/* Bio图片包装器 */
.bio-image-wrapper {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  background: #f3f4f6;
  min-height: 200px;
}
.bio-image { 
  width: 100%; 
  height: auto; 
  display: block;
  opacity: 1;
  transition: opacity 0.4s ease;
}
.bio-image-wrapper.image-loading .bio-image {
  opacity: 0;
}

/* 图片骨架屏 */
.image-skeleton {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.bio-image-wrapper.image-loading .image-skeleton {
  opacity: 1;
}

/* Bottom bar */
.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 40;
  background: #ffffff;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 -6px 32px rgba(0, 0, 0, 0.08);
  padding: 0 30px;
}
.bottom-inner {
  max-width: 1400px;
  margin: 0 auto;
  min-height: 72px;
  padding: 20px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}
.bottom-left { min-width: 0; }
.bottom-title {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #000000;
}
.bottom-sub {
  margin-top: 4px;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.7);
  max-width: 720px;
}
.bottom-right {
  display: inline-flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.btn {
  height: 36px;
  padding: 0 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #000000;
  background: transparent;
  color: #000000;
  transform: translateY(0);
}
.btn:hover {
  background: rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.btn:active {
  background: #000000;
  color: #ffffff;
  transform: scale(0.97);
}
.btn.ghost {
  background: transparent;
  border: 1px solid #000000;
  color: #000000;
}

@media (max-width: 900px) {
  .resume-container { padding: 104px 20px 220px; }
  .avatar-circle { width: 112px; height: 112px; }
  .hero-title { font-size: clamp(38px, 11vw, 54px); }
  .hero-dek { margin-top: 18px; font-size: 17px; }
  .hero-dept { font-size: 16px; }
  .divider { margin: 40px 0 22px; }
  .info-grid { display: grid; grid-template-columns: minmax(0, 1fr); gap: 20px; }
  .info-value { overflow-wrap: anywhere; }
  .bio-text { font-size: 17px; line-height: 1.75; }
  .bottom-bar { padding: 0; }
  .bottom-inner { align-items: stretch; flex-direction: column; gap: 14px; padding: 16px 20px; }
  .bottom-right { width: 100%; }
  .bottom-right .btn { flex: 1 1 auto; min-height: 44px; }
}
</style>
