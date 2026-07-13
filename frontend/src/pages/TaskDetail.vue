<template>
  <section class="task-detail-page">
    <div class="page-container">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <span>{{ isZh ? '加载中...' : 'Loading...' }}</span>
      </div>

      <!-- Error State -->
      <div v-else-if="loadError" class="error-state">
        <div class="error-icon">
          <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="currentColor" stroke-width="1.2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 8v4M12 16h.01"/>
          </svg>
        </div>
        <div class="error-title">{{ isZh ? '加载失败' : 'Load Failed' }}</div>
        <div class="error-desc">{{ loadError }}</div>
        <button class="btn ghost" @click="loadTask">{{ isZh ? '重试' : 'Retry' }}</button>
      </div>

      <!-- Task Content -->
      <template v-else-if="task">
        <header class="page-header">
          <div class="task-meta reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }">
            <span class="task-id">#{{ task.id }}</span>
            <span class="task-time">{{ formatTime(task.published_at || task.created_at) }}</span>
          </div>
          <h1 class="page-title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '120ms' }">
            {{ task.title || (isZh ? '未命名任务' : 'Untitled Task') }}
          </h1>
        </header>

        <!-- Task Content Section -->
        <div class="task-content-section reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '180ms' }">
          <div class="section-label">{{ isZh ? '任务内容' : 'Task Content' }}</div>
          <div class="task-content-body">{{ task.content || (isZh ? '无内容' : 'No content') }}</div>
        </div>

        <!-- Submission Status -->
        <div class="submission-status reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '240ms' }">
          <div class="status-card" :class="statusClass">
            <div class="status-icon">
              <svg v-if="!task.my_submission" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <svg v-else-if="task.my_submission.score === null" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <div class="status-info">
              <div class="status-title">{{ statusTitle }}</div>
              <div class="status-desc">{{ statusDesc }}</div>
            </div>
            <div v-if="task.my_submission && task.my_submission.score !== null" class="status-score">
              {{ task.my_submission.score }}<span class="score-unit">{{ isZh ? '分' : 'pts' }}</span>
            </div>
          </div>
        </div>

        <!-- Submission Form -->
        <div class="submission-form reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '300ms' }">
          <div class="section-label">
            {{ isZh ? '我的提交' : 'My Submission' }}
            <span class="label-hint" v-if="task.my_submission">
              {{ isZh ? '上次提交：' : 'Last submitted: ' }}{{ formatTime(task.my_submission.updated_at || task.my_submission.created_at) }}
            </span>
          </div>

          <!-- Text Content -->
          <div class="form-field">
            <label class="form-label">
              {{ isZh ? '完成情况' : 'Progress Report' }}
              <span class="char-count">{{ form.text_content.length }}/5000</span>
            </label>
            <textarea
              v-model="form.text_content"
              class="form-textarea"
              maxlength="5000"
              :placeholder="isZh ? '描述你的完成情况...' : 'Describe your progress...'"
              rows="5"
            ></textarea>
          </div>

          <!-- Suggestion -->
          <div class="form-field">
            <label class="form-label">
              {{ isZh ? '建议反馈' : 'Suggestions' }}
              <span class="char-count">{{ form.suggestion.length }}/2000</span>
            </label>
            <textarea
              v-model="form.suggestion"
              class="form-textarea"
              maxlength="2000"
              :placeholder="isZh ? '对任务的建议或反馈（可选）...' : 'Your suggestions or feedback (optional)...'"
              rows="3"
            ></textarea>
          </div>

          <!-- Images Section -->
          <div class="form-field">
            <label class="form-label">
              {{ isZh ? '附件图片' : 'Attachments' }}
              <span class="label-hint">({{ images.length }} {{ isZh ? '张' : 'images' }})</span>
            </label>
            
            <!-- Existing Images -->
            <div class="images-grid" v-if="images.length > 0">
              <div v-for="img in images" :key="img.id" class="image-item">
                <img :src="img.url || img.image_url" :alt="img.original_filename || img.filename" @click="previewImage(img)" />
                <button class="image-remove" @click="removeImage(img)" :disabled="isDeletingImage === img.id">
                  <svg v-if="isDeletingImage !== img.id" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"/>
                  </svg>
                  <span v-else class="mini-spinner"></span>
                </button>
              </div>
            </div>

            <!-- Upload Button -->
            <label class="upload-card" :class="{ uploading: isUploading }">
              <input
                type="file"
                accept="image/*"
                class="sr-only"
                :disabled="isUploading"
                @change="handleImageUpload"
              />
              <div class="upload-icon">
                <svg v-if="!isUploading" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <div v-else class="upload-spinner"></div>
              </div>
              <div class="upload-text">
                {{ isUploading ? (isZh ? '上传中...' : 'Uploading...') : (isZh ? '点击上传图片' : 'Click to upload image') }}
              </div>
              <div class="upload-hint">{{ isZh ? '支持 JPG、PNG、GIF，单张最大 10MB' : 'JPG, PNG, GIF supported, max 10MB each' }}</div>
            </label>
          </div>
        </div>
      </template>
    </div>

    <!-- Bottom bar -->
    <div class="bottom-bar" v-if="task">
      <div class="bottom-inner">
        <div class="bottom-left">
          <div class="bottom-title">{{ isZh ? '任务提交' : 'Task Submission' }}</div>
          <div class="bottom-sub">{{ statusTitle }}</div>
        </div>
        <div class="bottom-right">
          <button class="btn ghost" type="button" @click="router.push({ name: 'my-tasks' })">
            {{ isZh ? '返回' : 'Back' }}
          </button>
          <button class="btn primary" type="button" :disabled="isSubmitting" @click="handleSubmit">
            {{ isSubmitting ? (isZh ? '提交中...' : 'Submitting...') : (isZh ? '保存提交' : 'Save Submission') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Image Preview Modal -->
    <div v-if="previewingImage" class="preview-overlay" @click="previewingImage = null">
      <div class="preview-container" @click.stop>
        <img :src="previewingImage.url || previewingImage.image_url" :alt="previewingImage.original_filename || previewingImage.filename" />
        <button class="preview-close" @click="previewingImage = null">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'
import { useUserStore } from '@/stores/user'
import { useErrorStore } from '@/stores/error'
import { useSuccessStore } from '@/stores/success'
import { getTaskDetail, upsertSubmission, uploadSubmissionImage, deleteSubmissionImage } from '@/services/taskService'

const router = useRouter()
const route = useRoute()
const i18n = useI18nStore()
const userStore = useUserStore()
const errorStore = useErrorStore()
const successStore = useSuccessStore()

const isZh = computed(() => i18n.locale === 'zh')
const pageEnter = ref(false)

// Task state
const task = ref(null)
const isLoading = ref(true)
const loadError = ref('')

// Form state
const form = reactive({
  text_content: '',
  suggestion: ''
})

// Images
const images = ref([])
const isUploading = ref(false)
const isDeletingImage = ref(null)
const previewingImage = ref(null)

// Submit state
const isSubmitting = ref(false)

// Computed status
const statusClass = computed(() => {
  if (!task.value?.my_submission) return 'status--pending'
  if (task.value.my_submission.score === null) return 'status--submitted'
  return 'status--scored'
})

const statusTitle = computed(() => {
  if (!task.value?.my_submission) return isZh.value ? '待完成' : 'Pending'
  if (task.value.my_submission.score === null) return isZh.value ? '已提交，待评分' : 'Submitted, awaiting score'
  return isZh.value ? '已评分' : 'Scored'
})

const statusDesc = computed(() => {
  if (!task.value?.my_submission) return isZh.value ? '请填写完成情况并提交' : 'Please fill in your progress and submit'
  if (task.value.my_submission.score === null) return isZh.value ? '管理员正在审核你的提交' : 'Admin is reviewing your submission'
  return isZh.value ? '你的提交已被评分' : 'Your submission has been scored'
})

// Format time
function formatTime(dateStr) {
  if (!dateStr) return '—'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString(isZh.value ? 'zh-CN' : 'en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateStr
  }
}

// Load task
async function loadTask() {
  const taskId = route.params.taskId
  if (!taskId) {
    loadError.value = isZh.value ? '任务ID无效' : 'Invalid task ID'
    isLoading.value = false
    return
  }

  isLoading.value = true
  loadError.value = ''
  try {
    const data = await getTaskDetail(taskId)
    task.value = data
    
    // Populate form with existing submission
    if (data.my_submission) {
      form.text_content = data.my_submission.text_content || ''
      form.suggestion = data.my_submission.suggestion || ''
      images.value = data.my_submission.images || []
    }
  } catch (err) {
    loadError.value = err?.message || (isZh.value ? '加载任务失败' : 'Failed to load task')
  } finally {
    isLoading.value = false
  }
}

// Submit form
async function handleSubmit() {
  if (isSubmitting.value) return
  
  isSubmitting.value = true
  try {
    const taskId = route.params.taskId
    const result = await upsertSubmission(taskId, {
      text_content: form.text_content.trim() || undefined,
      suggestion: form.suggestion.trim() || undefined
    })
    
    // Update local state
    if (task.value) {
      task.value.my_submission = result
      images.value = result.images || []
    }
    
    successStore.showSuccess(isZh.value ? '提交成功' : 'Submitted successfully')
  } catch (err) {
    errorStore.showError(err?.message || (isZh.value ? '提交失败' : 'Submit failed'))
  } finally {
    isSubmitting.value = false
  }
}

// Upload image
async function handleImageUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  
  // Reset input
  e.target.value = ''
  
  // Validate file size (10MB)
  if (file.size > 10 * 1024 * 1024) {
    errorStore.showError(isZh.value ? '图片大小不能超过10MB' : 'Image size cannot exceed 10MB')
    return
  }
  
  isUploading.value = true
  try {
    const taskId = route.params.taskId
    const result = await uploadSubmissionImage(taskId, file, file.name)
    
    // Add new image to list
    if (result.image) {
      images.value.push(result.image)
    } else if (result.id) {
      images.value.push(result)
    }
    
    // Update submission state if needed
    if (task.value && !task.value.my_submission) {
      await loadTask()
    }
    
    successStore.showSuccess(isZh.value ? '图片上传成功' : 'Image uploaded')
  } catch (err) {
    errorStore.showError(err?.message || (isZh.value ? '上传失败' : 'Upload failed'))
  } finally {
    isUploading.value = false
  }
}

// Remove image
async function removeImage(img) {
  if (isDeletingImage.value) return
  
  isDeletingImage.value = img.id
  try {
    const taskId = route.params.taskId
    await deleteSubmissionImage(taskId, img.id)
    
    // Remove from local list
    const idx = images.value.findIndex(i => i.id === img.id)
    if (idx !== -1) images.value.splice(idx, 1)
    
    successStore.showSuccess(isZh.value ? '图片已删除' : 'Image deleted')
  } catch (err) {
    errorStore.showError(err?.message || (isZh.value ? '删除失败' : 'Delete failed'))
  } finally {
    isDeletingImage.value = null
  }
}

// Preview image
function previewImage(img) {
  previewingImage.value = img
}

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  
  loadTask()
  
  requestAnimationFrame(() => {
    pageEnter.value = true
  })
})
</script>


<style scoped>
/* Reveal animation */
.reveal {
  opacity: 0;
  transform: translate3d(0, 22px, 0);
  filter: blur(10px);
  transition: opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1), transform 0.9s cubic-bezier(0.16, 1, 0.3, 1), filter 0.9s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--d, 0ms);
}
.reveal.is-in { opacity: 1; transform: translate3d(0, 0, 0); filter: blur(0); }

/* Page layout */
.task-detail-page {
  min-height: 100vh;
  background: #fbfbfb;
  padding: 120px 24px 148px;
}

.page-container {
  max-width: 720px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 13px;
  color: rgba(0, 0, 0, 0.5);
}

.task-id {
  font-family: monospace;
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  color: #0b0f19;
  margin: 0;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

/* Loading & Error States */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  text-align: center;
  gap: 16px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: #0b0f19;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  color: rgba(0, 0, 0, 0.2);
}

.error-title {
  font-size: 18px;
  font-weight: 600;
  color: #0b0f19;
}

.error-desc {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.5);
}

/* Task Content Section */
.task-content-section {
  margin-bottom: 24px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #000000;
  margin-bottom: 12px;
}

.label-hint {
  font-weight: 500;
  color: rgba(0, 0, 0, 0.4);
  text-transform: none;
  letter-spacing: 0;
}

.task-content-body {
  padding: 20px;
  background: #fff;
  border: 1.5px solid rgba(0, 0, 0, 0.08);
  border-radius: 14px;
  font-size: 15px;
  line-height: 1.7;
  color: #0b0f19;
  white-space: pre-wrap;
}

/* Submission Status */
.submission-status {
  margin-bottom: 32px;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border: 1.5px solid rgba(0, 0, 0, 0.08);
  border-radius: 14px;
}

.status-card.status--pending {
  border-color: rgba(245, 158, 11, 0.3);
  background: rgba(245, 158, 11, 0.05);
}

.status-card.status--submitted {
  border-color: rgba(59, 130, 246, 0.3);
  background: rgba(59, 130, 246, 0.05);
}

.status-card.status--scored {
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.05);
}

.status-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.status--pending .status-icon {
  background: rgba(245, 158, 11, 0.15);
  color: #d97706;
}

.status--submitted .status-icon {
  background: rgba(59, 130, 246, 0.15);
  color: #2563eb;
}

.status--scored .status-icon {
  background: rgba(16, 185, 129, 0.15);
  color: #059669;
}

.status-info {
  flex: 1;
}

.status-title {
  font-size: 16px;
  font-weight: 600;
  color: #0b0f19;
  margin-bottom: 4px;
}

.status-desc {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.55);
}

.status-score {
  font-size: 32px;
  font-weight: 700;
  color: #059669;
}

.score-unit {
  font-size: 14px;
  font-weight: 600;
  margin-left: 2px;
}

/* Submission Form */
.submission-form {
  margin-bottom: 24px;
}

.form-field {
  margin-bottom: 24px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
  margin-bottom: 10px;
}

.char-count {
  margin-left: auto;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.4);
  font-size: 12px;
}

.form-textarea {
  width: 100%;
  padding: 16px 18px;
  border: 1.5px solid rgba(0, 0, 0, 0.12);
  border-radius: 14px;
  font-size: 15px;
  font-family: inherit;
  background: #fff;
  resize: vertical;
  min-height: 100px;
  line-height: 1.6;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-sizing: border-box;
}

.form-textarea:focus {
  outline: none;
  border-color: #000000;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.06);
}

/* Images Grid */
.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.05);
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.image-item:hover img {
  transform: scale(1.05);
}

.image-remove {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 24px;
  height: 24px;
  border: none;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.image-item:hover .image-remove {
  opacity: 1;
}

.image-remove:hover {
  background: rgba(239, 68, 68, 0.9);
}

.mini-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

/* Upload Card */
.upload-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
  background: #fff;
  border: 2px dashed rgba(0, 0, 0, 0.15);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-card:hover {
  border-color: rgba(0, 0, 0, 0.3);
  background: rgba(0, 0, 0, 0.02);
}

.upload-card.uploading {
  pointer-events: none;
  opacity: 0.7;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.upload-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 0, 0, 0.4);
  margin-bottom: 12px;
}

.upload-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: #0b0f19;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.upload-text {
  font-size: 14px;
  font-weight: 600;
  color: #0b0f19;
  margin-bottom: 4px;
}

.upload-hint {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
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

.bottom-left {
  min-width: 0;
}

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
}

.bottom-right {
  display: inline-flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  padding: 0 20px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  border: 1.5px solid #000000;
  background: transparent;
  color: #000000;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn:active:not(:disabled) {
  background: #000000;
  color: #ffffff;
  transform: scale(0.97);
}

.btn.primary:active:not(:disabled) {
  background: #ffffff;
  color: #000000;
  transform: scale(0.97);
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn.primary {
  background: #000000;
  border-color: #000000;
  color: #ffffff;
}

.btn.primary:hover:not(:disabled) {
  background: #1a1a1a;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.btn.ghost {
  border-color: rgba(0, 0, 0, 0.2);
}

/* Image Preview Modal */
.preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.preview-container {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.preview-container img {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 8px;
}

.preview-close {
  position: absolute;
  top: -48px;
  right: 0;
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s ease;
}

.preview-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

@media (max-width: 900px) {
  .task-detail-page { padding: 104px 16px 230px; }
  .page-title { font-size: clamp(32px, 9vw, 40px); overflow-wrap: anywhere; }
  .task-meta { flex-wrap: wrap; gap: 8px 14px; }
  .status-card { align-items: flex-start; padding: 16px; }
  .submission-textarea { min-height: 180px; }
  .images-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .bottom-inner { flex-direction: column; align-items: stretch; gap: 14px; padding: 16px; }
  .bottom-right { width: 100%; flex-wrap: wrap; }
  .bottom-bar .btn { flex: 1 1 120px; min-height: 44px; }
  .preview-overlay { padding: 12px; }
  .preview-close { top: 10px; right: 10px; background: rgba(0, 0, 0, 0.55); }
}
</style>
