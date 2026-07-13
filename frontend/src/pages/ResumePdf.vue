<template>
  <section class="resume-pdf-page">
    <div class="container">
      <!-- Header -->
      <header class="page-header reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }">
        <h1 class="page-title">{{ isZh ? 'PDF 简历' : 'PDF Resume' }}</h1>
        <p class="page-desc">{{ isZh ? '上传您的 PDF 格式简历，方便管理员查阅。' : 'Upload your PDF resume for administrators to review.' }}</p>
      </header>

      <!-- Main content -->
      <main class="main-content reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '160ms' }">
        <!-- Upload area -->
        <div class="upload-section">
          <label 
            class="upload-zone" 
            :class="{ 'is-dragging': isDragging, 'is-uploading': isUploading, 'has-file': !!pdfInfo }"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
          >
            <input
              ref="fileInputRef"
              type="file"
              accept=".pdf,application/pdf"
              class="sr-only"
              :disabled="isUploading"
              @change="handleFileSelect"
            />
            
            <div class="upload-content">
              <div class="upload-icon">
                <svg v-if="isUploading" class="spin" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <path d="M12 18v-6"/>
                  <path d="M9 15l3-3 3 3"/>
                </svg>
              </div>
              
              <div class="upload-text">
                <span v-if="isUploading">{{ isZh ? '上传中...' : 'Uploading...' }}</span>
                <span v-else-if="pdfInfo">{{ isZh ? '点击或拖拽以更换文件' : 'Click or drag to replace' }}</span>
                <span v-else>{{ isZh ? '点击或拖拽 PDF 文件到此处' : 'Click or drag PDF file here' }}</span>
              </div>
              
              <div class="upload-hint">
                {{ isZh ? '仅支持 PDF 格式，最大 20MB' : 'PDF only, max 20MB' }}
              </div>
            </div>
          </label>
        </div>

        <!-- Current PDF info -->
        <div v-if="pdfInfo" class="pdf-card reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '240ms' }">
          <div class="pdf-icon">
            <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <path d="M9 15h6"/>
              <path d="M9 11h6"/>
            </svg>
          </div>
          
          <div class="pdf-info">
            <div class="pdf-name">{{ pdfInfo.original_filename }}</div>
            <div class="pdf-meta">
              <span>{{ formatFileSize(pdfInfo.file_size) }}</span>
              <span class="meta-sep">·</span>
              <span>{{ formatDate(pdfInfo.updated_at) }}</span>
            </div>
          </div>
          
          <div class="pdf-actions">
            <a :href="pdfInfo.url" target="_blank" class="btn-action" :title="isZh ? '预览' : 'Preview'">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
            </a>
            <a :href="pdfInfo.url" download class="btn-action" :title="isZh ? '下载' : 'Download'">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </a>
          </div>
        </div>

        <!-- Empty state -->
        <div v-else-if="!isLoading" class="empty-state reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '240ms' }">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <div class="empty-text">{{ isZh ? '暂未上传 PDF 简历' : 'No PDF resume uploaded yet' }}</div>
        </div>

        <!-- Loading state -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <span>{{ isZh ? '加载中...' : 'Loading...' }}</span>
        </div>
      </main>

      <!-- Bottom bar -->
      <div class="bottom-bar">
        <button class="btn ghost" type="button" @click="router.push('/user')">
          {{ isZh ? '返回' : 'Back' }}
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useI18nStore } from '@/stores/i18n'
import { useErrorStore } from '@/stores/error'
import { useSuccessStore } from '@/stores/success'
import { useWarningStore } from '@/stores/warning'
import { uploadMyPdfResume, getMyPdfResume } from '@/services/resumeService'

const router = useRouter()
const userStore = useUserStore()
const i18n = useI18nStore()
const errorStore = useErrorStore()
const successStore = useSuccessStore()
const warningStore = useWarningStore()

const isZh = computed(() => i18n.locale === 'zh')
const pageEnter = ref(false)

const fileInputRef = ref(null)
const pdfInfo = ref(null)
const isLoading = ref(false)
const isUploading = ref(false)
const isDragging = ref(false)

const MAX_FILE_SIZE = 20 * 1024 * 1024 // 20MB

function validatePdfFile(file) {
  if (!file) {
    return { valid: false, error: isZh.value ? '请选择文件' : 'Please select a file' }
  }
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    return { valid: false, error: isZh.value ? '仅支持 PDF 格式' : 'Only PDF format is supported' }
  }
  if (file.size > MAX_FILE_SIZE) {
    return { valid: false, error: isZh.value ? '文件大小不能超过 20MB' : 'File size must be <= 20MB' }
  }
  return { valid: true, error: null }
}

async function uploadFile(file) {
  const validation = validatePdfFile(file)
  if (!validation.valid) {
    warningStore.showWarning(validation.error)
    return
  }

  isUploading.value = true
  try {
    const result = await uploadMyPdfResume(file, file.name)
    pdfInfo.value = result
    successStore.showSuccess(isZh.value ? 'PDF 简历上传成功' : 'PDF resume uploaded successfully')
  } catch (e) {
    const msg = e?.message || e
    if (e?.status === 400) {
      errorStore.showError(isZh.value ? `上传失败：${msg}` : `Upload failed: ${msg}`)
    } else {
      errorStore.showError(isZh.value ? `上传失败：${msg}` : `Upload failed: ${msg}`)
    }
  } finally {
    isUploading.value = false
    if (fileInputRef.value) fileInputRef.value.value = ''
  }
}

function handleFileSelect(event) {
  const file = event?.target?.files?.[0]
  if (file) uploadFile(file)
}

function handleDrop(event) {
  isDragging.value = false
  const file = event?.dataTransfer?.files?.[0]
  if (file) uploadFile(file)
}

async function loadPdfInfo() {
  isLoading.value = true
  try {
    const data = await getMyPdfResume()
    pdfInfo.value = data
  } catch (e) {
    if (e?.status === 404) {
      pdfInfo.value = null
    } else {
      errorStore.showError(isZh.value ? '加载 PDF 简历信息失败' : 'Failed to load PDF resume info')
    }
  } finally {
    isLoading.value = false
  }
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return `${size.toFixed(i > 0 ? 1 : 0)} ${units[i]}`
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString(isZh.value ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  requestAnimationFrame(() => { pageEnter.value = true })
  await loadPdfInfo()
})
</script>

<style scoped>
.reveal {
  opacity: 0;
  transform: translate3d(0, 22px, 0);
  filter: blur(8px);
  transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), transform 0.7s cubic-bezier(0.16, 1, 0.3, 1), filter 0.7s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--d, 0ms);
}
.reveal.is-in { opacity: 1; transform: translate3d(0, 0, 0); filter: blur(0); }

.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0; }

.resume-pdf-page {
  min-height: 100vh;
  background: #fff;
  padding: 100px 24px 120px;
}

.container {
  max-width: 640px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 48px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #000;
  margin: 0 0 12px;
}

.page-desc {
  font-size: 15px;
  color: rgba(0,0,0,0.5);
  margin: 0;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Upload zone */
.upload-section {
  width: 100%;
}

.upload-zone {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  border: 2px dashed rgba(0,0,0,0.15);
  border-radius: 16px;
  background: rgba(0,0,0,0.02);
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-zone:hover,
.upload-zone.is-dragging {
  border-color: rgba(0,0,0,0.4);
  background: rgba(0,0,0,0.04);
}

.upload-zone.is-uploading {
  pointer-events: none;
  opacity: 0.7;
}

.upload-zone.has-file {
  min-height: 140px;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
}

.upload-icon {
  color: rgba(0,0,0,0.3);
}

.upload-icon .spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.upload-text {
  font-size: 16px;
  font-weight: 500;
  color: rgba(0,0,0,0.7);
}

.upload-hint {
  font-size: 13px;
  color: rgba(0,0,0,0.4);
}

/* PDF card */
.pdf-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: #fafafa;
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,0.06);
}

.pdf-icon {
  flex-shrink: 0;
  color: #e74c3c;
}

.pdf-info {
  flex: 1;
  min-width: 0;
}

.pdf-name {
  font-size: 15px;
  font-weight: 600;
  color: #000;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pdf-meta {
  font-size: 13px;
  color: rgba(0,0,0,0.5);
  margin-top: 4px;
}

.meta-sep {
  margin: 0 6px;
}

.pdf-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(0,0,0,0.05);
  color: rgba(0,0,0,0.6);
  transition: all 0.15s ease;
}

.btn-action:hover {
  background: rgba(0,0,0,0.1);
  color: #000;
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 24px;
  color: rgba(0,0,0,0.3);
}

.empty-text {
  font-size: 15px;
}

/* Loading state */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: rgba(0,0,0,0.5);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(0,0,0,0.1);
  border-top-color: rgba(0,0,0,0.5);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Bottom bar */
.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 16px 24px;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(12px);
  border-top: 1px solid rgba(0,0,0,0.06);
  display: flex;
  justify-content: center;
}

.btn {
  padding: 12px 28px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  border: none;
}

.btn.ghost {
  background: rgba(0,0,0,0.05);
  color: #000;
}

.btn.ghost:hover {
  background: rgba(0,0,0,0.1);
}

@media (max-width: 640px) {
  .resume-pdf-page {
    padding: 104px 16px 130px;
  }
  
  .page-title {
    font-size: 26px;
  }
  
  .pdf-card {
    flex-wrap: wrap;
  }
  
  .pdf-info {
    flex-basis: calc(100% - 72px);
  }
  
  .pdf-actions {
    flex-basis: 100%;
    justify-content: flex-end;
    margin-top: 8px;
  }

  .upload-zone { padding: 28px 18px; }
  .bottom-bar { padding: 14px 16px; }
  .bottom-bar .btn { width: 100%; min-height: 44px; }
}
</style>
