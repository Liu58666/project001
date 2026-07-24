<template>
  <section class="resume-page">
    <div class="resume-container">
      <!-- Meta bar -->
      <div class="meta-bar reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }">
        <label class="meta-field">
          <span class="meta-label">{{ isZh ? '姓名' : 'Name' }}</span>
          <input class="meta-control" v-model.trim="form.real_name" :placeholder="isZh ? '请输入姓名' : 'Enter name'" />
        </label>
        <label class="meta-field">
          <span class="meta-label">{{ isZh ? '职位' : 'Title' }}</span>
          <input class="meta-control" v-model.trim="extras.job_title" :placeholder="isZh ? '产品经理 / AI 工程师' : 'PM / AI Engineer'" />
        </label>
        <label class="meta-field">
          <span class="meta-label">{{ isZh ? '部门' : 'Department' }}</span>
          <input class="meta-control" v-model.trim="extras.department" :placeholder="isZh ? '研发/产品' : 'R&D / Product'" />
        </label>
      </div>

      <!-- Main preview area -->
      <main class="preview reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '160ms' }">
        <div class="detail">
          <header class="hero">
            <div class="avatar-section">
              <label class="avatar-uploader" :class="{ uploading: isUploadingAvatar, 'has-avatar': !!avatarUrl }">
                <input ref="avatarInputRef" type="file" accept="image/jpeg,image/png,image/gif,image/webp" class="sr-only" :disabled="isUploadingAvatar" @change="handleAvatarUpload" />
                <div class="avatar-circle" :class="{ 'avatar-loading': avatarUrl && !avatarLoaded }">
                  <img v-if="avatarUrl" :src="avatarUrl" alt="avatar" @load="onAvatarLoad" />
                  <div v-else class="avatar-letter">{{ avatarLetter }}</div>
                  <div class="avatar-skeleton"></div>
                  <div class="avatar-overlay">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                      <path d="M12 20h9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                      <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </div>
                </div>
              </label>
            </div>
            <textarea class="hero-title hero-title-input" v-model="form.real_name" rows="1" :placeholder="isZh ? '请输入姓名…' : 'Enter your name…'"></textarea>
            <textarea class="hero-dek hero-dek-input" v-model="extras.job_title" rows="1" :placeholder="isZh ? '职位/标签（可选）…' : 'Title / Tagline (optional)…'"></textarea>
          </header>

          <div class="divider"></div>

          <!-- Basic info -->
          <div class="content">
            <div class="section-label">{{ isZh ? '基本信息' : 'Basic Information' }}</div>
            <div class="info-row">
              <label class="info-field">
                <span class="info-label">{{ isZh ? '年龄' : 'Age' }}</span>
                <input class="info-control" type="number" min="0" v-model.number="form.age" />
              </label>
              <label class="info-field">
                <span class="info-label">{{ isZh ? '学历' : 'Education' }}</span>
                <input class="info-control" v-model.trim="extras.education" :placeholder="isZh ? '本科/硕士' : 'Bachelor/Master'" />
              </label>
              <label class="info-field">
                <span class="info-label">{{ isZh ? '邮箱' : 'Email' }}</span>
                <input class="info-control" v-model.trim="form.email" :placeholder="isZh ? '邮箱' : 'Email'" />
              </label>
            </div>
            <div class="info-row">
              <label class="info-field">
                <span class="info-label">{{ isZh ? '电话' : 'Phone' }}</span>
                <input class="info-control" :value="form.phone" readonly :placeholder="isZh ? '电话' : 'Phone'" />
                <small class="field-note">{{ isZh ? '手机号来自注册账号，暂不支持在此修改。' : 'Phone comes from your registered account and cannot be changed here.' }}</small>
              </label>
              <label class="info-field">
                <span class="info-label">{{ isZh ? '所在地' : 'Location' }}</span>
                <input class="info-control" v-model.trim="form.address" :placeholder="isZh ? '上海' : 'Shanghai'" />
              </label>
              <div class="info-field"></div>
            </div>
          </div>

          <div class="divider"></div>

          <!-- Resume visual editor - Word风格 -->
          <div class="content">
            <div class="section-label">{{ isZh ? '个人简历' : 'Resume' }}</div>
            
            <!-- 工具栏 -->
            <div class="editor-toolbar">
              <label class="toolbar-btn" :class="{ uploading: isUploadingContent }">
                <input type="file" accept="image/jpeg,image/png,image/gif,image/webp" class="sr-only" :disabled="isUploadingContent" @change="handleInsertImageAtCursor($event)" />
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="1.5"/>
                  <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
                  <path d="M21 15l-5-5L5 21" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>{{ isUploadingContent ? (isZh ? '上传中...' : 'Uploading...') : (isZh ? '插入图片' : 'Insert Image') }}</span>
              </label>
            </div>
            
            <!-- Word风格编辑区 -->
            <div class="word-editor" ref="wordEditorRef">
              <div v-for="(block, idx) in contentBlocks" :key="block.id" class="editor-block" :class="{ 'editor-block--image': block.type === 'image', 'editor-block--focused': focusedBlockIndex === idx }">
                <!-- Text block - contenteditable -->
                <div v-if="block.type === 'text'" class="block-text">
                  <div
                    class="block-editable"
                    contenteditable="true"
                    :data-placeholder="isZh ? '输入内容...' : 'Start typing...'"
                    :data-index="idx"
                    @focus="focusedBlockIndex = idx"
                    @blur="handleTextBlur($event, idx)"
                    @keydown="handleKeyDown($event, idx)"
                    @paste="handlePaste($event, idx)"
                  ></div>
                </div>
                <!-- Image block -->
                <div v-else-if="block.type === 'image'" class="block-image" @click="focusedBlockIndex = idx">
                  <img :src="block.url" alt="Image" class="block-image-preview" />
                  <button class="block-remove block-remove--image" type="button" @click.stop="removeBlock(idx)" :title="isZh ? '删除图片' : 'Remove image'">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                  </button>
                </div>
              </div>
              <!-- Empty state -->
              <div v-if="contentBlocks.length === 0" class="editor-empty" @click="addFirstTextBlock">
                <div class="empty-hint">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                  <span>{{ isZh ? '点击此处开始编写...' : 'Click here to start writing...' }}</span>
                </div>
              </div>
            </div>

            <div class="content-footer">
              <div class="content-hint">
                {{ isZh ? '段落：' : 'Paragraphs: ' }}{{ textBlockCount }}
                <span v-if="imageBlockCount > 0"> · {{ isZh ? '图片：' : 'Images: ' }}{{ imageBlockCount }}</span>
              </div>
            </div>
          </div>

          <div v-if="isLoadingResume" class="loading-hint">{{ isZh ? '加载中…' : 'Loading…' }}</div>
        </div>
      </main>
    </div>

    <!-- Bottom bar -->
    <div class="bottom-bar">
      <div class="bottom-inner">
        <div class="bottom-left">
          <div class="bottom-title">{{ isZh ? '简历编辑' : 'Resume Editor' }}</div>
          <div class="bottom-sub">{{ isZh ? '编辑个人信息，预览简历效果。' : 'Edit your profile and preview resume.' }}</div>
        </div>
        <div class="bottom-right">
          <div class="toggle-group">
            <span class="toggle-label">{{ form.is_public ? (isZh ? '公开' : 'Public') : (isZh ? '私密' : 'Privacy') }}</span>
            <input type="checkbox" class="theme-checkbox" v-model="form.is_public" />
          </div>
          <button class="btn ghost" type="button" @click="router.push('/user')">{{ isZh ? '返回' : 'Back' }}</button>
          <button class="btn ghost" type="button" :disabled="isLoadingResume" @click="loadAll">{{ isZh ? '刷新' : 'Refresh' }}</button>
          <button class="btn primary" type="button" :disabled="isSavingResume" @click="saveAll">
            {{ isSavingResume ? (isZh ? '保存中…' : 'Saving…') : (isZh ? '保存' : 'Save') }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useI18nStore } from '@/stores/i18n'
import { useErrorStore } from '@/stores/error'
import { useSuccessStore } from '@/stores/success'
import { useWarningStore } from '@/stores/warning'

import { createOrUpdateResume, getMyResume } from '@/services/resumeService'
import { uploadUserImage } from '@/services/userImageService'
import { patchMyProfile } from '@/services/profileService'

const router = useRouter()
const userStore = useUserStore()
const i18n = useI18nStore()
const errorStore = useErrorStore()
const successStore = useSuccessStore()
const warningStore = useWarningStore()

const isZh = computed(() => i18n.locale === 'zh')
const pageEnter = ref(false)
const resume = ref(null)

const form = reactive({
  real_name: '',
  gender: '',
  age: null,
  address: '',
  is_public: false,
  email: '',
  phone: '',
})

const extras = reactive({
  job_title: '',
  education: '',
  department: '',
})

const avatarUrl = computed(() => {
  const r = resume.value
  return r?.avatar_url || r?.avatarUrl || r?.avatar || r?.avatarImageUrl || ''
})

const avatarLetter = computed(() => {
  const s = String(form.real_name || '').trim() || String(userStore.displayNameText || userStore.displayName || userStore.username || 'U').trim() || 'U'
  return (s[0] || 'U').toUpperCase()
})

const isLoadingResume = ref(false)
const isSavingResume = ref(false)

// Avatar upload
const avatarInputRef = ref(null)
const isUploadingAvatar = ref(false)
const avatarLoaded = ref(false)

// 头像加载完成
function onAvatarLoad() {
  avatarLoaded.value = true
}

// Content blocks editor
let blockIdCounter = 0
const contentBlocks = ref([{ id: blockIdCounter++, type: 'text', content: '' }])
const isUploadingContent = ref(false)
const insertAfterIndex = ref(-1)

// Word editor related
const wordEditorRef = ref(null)
const textBlockRefs = ref([])
const focusedBlockIndex = ref(0)

// Track the next available position from database (max position + 1)
const nextBioImagePosition = ref(0)

// 将 HTML 转换为纯文本
function htmlToText(html) {
  if (!html) return ''
  const temp = document.createElement('div')
  temp.innerHTML = html
  temp.querySelectorAll('br').forEach(br => br.replaceWith('\n'))
  temp.querySelectorAll('div, p').forEach(el => {
    el.prepend(document.createTextNode('\n'))
  })
  return temp.textContent?.trim() || ''
}

const textBlockCount = computed(() => contentBlocks.value.filter(b => b.type === 'text' && htmlToText(b.content)).length)
const imageBlockCount = computed(() => contentBlocks.value.filter(b => b.type === 'image').length)

const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
const MAX_IMAGE_SIZE = 10 * 1024 * 1024

function validateImageFile(file) {
  if (!file) return { valid: false, error: isZh.value ? '请选择图片文件' : 'Please choose an image file' }
  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    return { valid: false, error: isZh.value ? '仅支持 JPG、PNG、GIF、WebP 格式' : 'Only JPG/PNG/GIF/WebP are supported' }
  }
  if (file.size > MAX_IMAGE_SIZE) {
    return { valid: false, error: isZh.value ? '图片大小不能超过 10MB' : 'Image must be <= 10MB' }
  }
  return { valid: true, error: null }
}

async function handleAvatarUpload(event) {
  const file = event?.target?.files?.[0]
  if (!file) return
  const validation = validateImageFile(file)
  if (!validation.valid) {
    warningStore.showWarning(validation.error)
    if (avatarInputRef.value) avatarInputRef.value.value = ''
    return
  }
  isUploadingAvatar.value = true
  avatarLoaded.value = false // 重置加载状态
  try {
    await uploadUserImage({ file, imageType: 'avatar', caption: '', displayOrder: 0 })
    successStore.showSuccess(isZh.value ? '头像上传成功' : 'Avatar uploaded')
    await loadResume()
  } catch (e) {
    errorStore.showError(isZh.value ? `头像上传失败：${e?.message || e}` : `Avatar upload failed: ${e?.message || e}`)
  } finally {
    isUploadingAvatar.value = false
    if (avatarInputRef.value) avatarInputRef.value.value = ''
  }
}

// Word style editor operations
function addFirstTextBlock() {
  contentBlocks.value.push({ id: blockIdCounter++, type: 'text', content: '' })
  nextTick(() => {
    const editables = document.querySelectorAll('.block-editable')
    if (editables.length > 0) {
      editables[editables.length - 1].focus()
    }
  })
}

function insertTextBlockAfter(index) {
  const newBlock = { id: blockIdCounter++, type: 'text', content: '' }
  contentBlocks.value.splice(index + 1, 0, newBlock)
  nextTick(() => {
    const editables = document.querySelectorAll('.block-editable')
    if (editables[index + 1]) {
      editables[index + 1].focus()
    }
  })
}

function removeBlock(index) {
  if (contentBlocks.value.length <= 1 && contentBlocks.value[0].type === 'text') {
    contentBlocks.value[0].content = ''
    nextTick(() => {
      const editables = document.querySelectorAll('.block-editable')
      if (editables[0]) {
        editables[0].innerHTML = ''
        editables[0].focus()
      }
    })
    return
  }
  contentBlocks.value.splice(index, 1)
  nextTick(() => {
    const editables = document.querySelectorAll('.block-editable')
    const targetIdx = Math.min(index, editables.length - 1)
    if (editables[targetIdx]) {
      editables[targetIdx].focus()
    }
  })
}

// 同步所有编辑器内容到数据
function syncAllContent() {
  const editables = document.querySelectorAll('.block-editable')
  let editableIndex = 0
  contentBlocks.value.forEach((block) => {
    if (block.type === 'text') {
      if (editables[editableIndex]) {
        block.content = editables[editableIndex].innerHTML
      }
      editableIndex++
    }
  })
}

// Handle blur - save content
function handleTextBlur(event, index) {
  const el = event.target
  contentBlocks.value[index].content = el.innerHTML
}

// Handle keyboard events
function handleKeyDown(event, index) {
  const el = event.target
  
  // Enter creates new paragraph (not Shift+Enter)
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    
    // Save current content
    syncAllContent()
    
    const selection = window.getSelection()
    if (!selection.rangeCount) return
    const range = selection.getRangeAt(0)
    
    // Get content after cursor
    const afterRange = range.cloneRange()
    afterRange.selectNodeContents(el)
    afterRange.setStart(range.endContainer, range.endOffset)
    const afterContent = afterRange.cloneContents()
    
    const tempDiv = document.createElement('div')
    tempDiv.appendChild(afterContent)
    const afterHtml = tempDiv.innerHTML
    
    // Delete content after cursor
    afterRange.deleteContents()
    
    // Update current block
    contentBlocks.value[index].content = el.innerHTML
    
    // Create new block with content after cursor
    const newBlock = { id: blockIdCounter++, type: 'text', content: afterHtml }
    contentBlocks.value.splice(index + 1, 0, newBlock)
    
    // Focus new block and set content
    nextTick(() => {
      const editables = document.querySelectorAll('.block-editable')
      const newEl = editables[index + 1]
      if (newEl) {
        newEl.innerHTML = afterHtml
        newEl.focus()
        const newSelection = window.getSelection()
        const newRange = document.createRange()
        newRange.selectNodeContents(newEl)
        newRange.collapse(true)
        newSelection.removeAllRanges()
        newSelection.addRange(newRange)
      }
    })
    return
  }
  
  // Backspace at block start merges with previous
  if (event.key === 'Backspace') {
    const selection = window.getSelection()
    if (!selection.rangeCount) return
    const range = selection.getRangeAt(0)
    
    if (!range.collapsed) return
    
    const isAtVeryStart = (function() {
      if (range.startOffset !== 0) return false
      
      let node = range.startContainer
      while (node && node !== el) {
        if (node.previousSibling) return false
        node = node.parentNode
      }
      return true
    })()
    
    if (isAtVeryStart && index > 0) {
      event.preventDefault()
      
      syncAllContent()
      
      let prevTextIndex = -1
      let prevEditableIndex = -1
      let editableCount = 0
      for (let i = 0; i < index; i++) {
        if (contentBlocks.value[i].type === 'text') {
          prevTextIndex = i
          prevEditableIndex = editableCount
          editableCount++
        }
      }
      
      if (prevTextIndex >= 0) {
        const currentContent = el.innerHTML
        const prevBlock = contentBlocks.value[prevTextIndex]
        const prevContent = prevBlock.content || ''
        
        prevBlock.content = prevContent + currentContent
        contentBlocks.value.splice(index, 1)
        
        nextTick(() => {
          const editables = document.querySelectorAll('.block-editable')
          const targetEl = editables[prevEditableIndex]
          if (targetEl) {
            targetEl.innerHTML = prevBlock.content
            targetEl.focus()
            
            const newSelection = window.getSelection()
            const newRange = document.createRange()
            
            try {
              let charCount = 0
              let targetNode = null
              let targetOffset = 0
              const mergePoint = prevContent.replace(/<[^>]*>/g, '').length
              
              const walker = document.createTreeWalker(targetEl, NodeFilter.SHOW_TEXT, null, false)
              while (walker.nextNode()) {
                const textNode = walker.currentNode
                if (charCount + textNode.length >= mergePoint) {
                  targetNode = textNode
                  targetOffset = mergePoint - charCount
                  break
                }
                charCount += textNode.length
              }
              
              if (targetNode) {
                newRange.setStart(targetNode, Math.min(targetOffset, targetNode.length))
              } else {
                newRange.selectNodeContents(targetEl)
                newRange.collapse(false)
              }
              newRange.collapse(true)
              newSelection.removeAllRanges()
              newSelection.addRange(newRange)
            } catch (e) {
              newRange.selectNodeContents(targetEl)
              newRange.collapse(false)
              newSelection.removeAllRanges()
              newSelection.addRange(newRange)
            }
          }
        })
      }
    }
  }
}

// Handle paste
function handlePaste(event, index) {
  event.preventDefault()
  const text = event.clipboardData.getData('text/plain')
  document.execCommand('insertText', false, text)
}

// Insert image at cursor position
async function handleInsertImageAtCursor(event) {
  const file = event?.target?.files?.[0]
  if (!file) return
  const validation = validateImageFile(file)
  if (!validation.valid) {
    warningStore.showWarning(validation.error)
    event.target.value = ''
    return
  }
  
  // Sync content first
  syncAllContent()
  
  isUploadingContent.value = true
  
  const insertIndex = focusedBlockIndex.value >= 0 ? focusedBlockIndex.value : contentBlocks.value.length - 1
  
  try {
    const displayOrder = nextBioImagePosition.value
    const result = await uploadUserImage({ file, imageType: 'bio', caption: '', displayOrder })
    const imageUrl = result.url || ''
    if (!imageUrl) {
      console.warn('Upload result:', result)
      throw new Error('No image URL in response')
    }
    const actualPosition = result.display_order ?? result.position ?? displayOrder
    const newBlock = { id: blockIdCounter++, type: 'image', url: imageUrl, position: actualPosition }
    contentBlocks.value.splice(insertIndex + 1, 0, newBlock)
    nextBioImagePosition.value = actualPosition + 1
    
    // Add empty text block after image if needed
    if (insertIndex + 2 >= contentBlocks.value.length || contentBlocks.value[insertIndex + 2]?.type !== 'text') {
      contentBlocks.value.splice(insertIndex + 2, 0, { id: blockIdCounter++, type: 'text', content: '' })
    }
    
    successStore.showSuccess(isZh.value ? '图片已插入' : 'Image inserted')
    
    // Focus text block after image
    nextTick(() => {
      const editables = document.querySelectorAll('.block-editable')
      let editableIdx = 0
      for (let i = 0; i <= insertIndex + 2 && i < contentBlocks.value.length; i++) {
        if (contentBlocks.value[i].type === 'text') {
          if (i === insertIndex + 2) break
          editableIdx++
        }
      }
      if (editables[editableIdx]) {
        editables[editableIdx].focus()
      }
    })
  } catch (e) {
    errorStore.showError(isZh.value ? `图片上传失败：${e?.message || e}` : `Image upload failed: ${e?.message || e}`)
  } finally {
    isUploadingContent.value = false
    event.target.value = ''
  }
}

// 初始化编辑器内容
function initEditorContent() {
  nextTick(() => {
    const editables = document.querySelectorAll('.block-editable')
    let editableIndex = 0
    contentBlocks.value.forEach((block) => {
      if (block.type === 'text' && editables[editableIndex]) {
        editables[editableIndex].innerHTML = block.content || ''
        editableIndex++
      }
    })
  })
}

function applyResumeToForm(r) {
  form.real_name = String(r?.real_name ?? r?.realName ?? '')
  form.gender = String(r?.gender ?? '')
  const age = r?.age
  form.age = age === null || age === undefined || age === '' ? null : Number(age)
  form.address = String(r?.address ?? '')
  form.is_public = Boolean(r?.is_public ?? r?.isPublic ?? false)
  form.email = String(r?.email ?? userStore.email ?? '')
  form.phone = String(r?.phone ?? userStore.phone ?? '')
  extras.job_title = String(r?.job_title ?? r?.title ?? r?.position ?? r?.tagline ?? '')
  extras.education = String(r?.education ?? '')
  extras.department = String(r?.department ?? '')

  // Build bio_images map: position -> url, and find max position
  const bioImages = Array.isArray(r?.bio_images) ? r.bio_images : []
  const imageMap = {}
  let maxPosition = -1
  bioImages.forEach((img) => {
    const pos = img.position ?? img.display_order ?? 0
    imageMap[pos] = img.url || img.image_url || ''
    if (pos > maxPosition) maxPosition = pos
  })
  // Set next available position for new uploads
  nextBioImagePosition.value = maxPosition + 1

  // Load bio into blocks - parse [IMAGE:n] format and replace with actual URLs
  const bioArr = Array.isArray(r?.bio) ? r.bio.map((x) => String(x ?? '')).filter(Boolean) : []
  if (bioArr.length) {
    const imagePattern = /^\[IMAGE:(\d+)\]$/
    contentBlocks.value = bioArr.map((text) => {
      const match = text.match(imagePattern)
      if (match) {
        // It's an image block - get URL from bio_images by position
        const position = parseInt(match[1], 10)
        const imageUrl = imageMap[position] || ''
        return { id: blockIdCounter++, type: 'image', url: imageUrl, position: position }
      }
      // It's a text block
      return { id: blockIdCounter++, type: 'text', content: text }
    })
  } else {
    // No bio content, reset to empty text block
    contentBlocks.value = [{ id: blockIdCounter++, type: 'text', content: '' }]
  }
  
  // 初始化编辑器内容
  initEditorContent()
}

async function loadResume() {
  isLoadingResume.value = true
  try {
    const data = await getMyResume()
    resume.value = data || null
    applyResumeToForm(data)
  } catch (e) {
    if (e?.status === 404) {
      resume.value = null
      applyResumeToForm({})
      return
    }
    errorStore.showError(isZh.value ? `加载履历失败：${e?.message || e}` : `Failed to load resume: ${e?.message || e}`)
  } finally {
    isLoadingResume.value = false
  }
}

async function loadAll() {
  await loadResume()
}

function buildBioArray() {
  // 先同步内容
  syncAllContent()
  
  const out = []
  for (const block of contentBlocks.value) {
    if (block.type === 'text') {
      const text = htmlToText(block.content)
      if (text) out.push(text)
    } else if (block.type === 'image') {
      // Use the actual position stored in the block (from database)
      out.push(`[IMAGE:${block.position}]`)
    }
  }
  return out
}

async function saveProfile() {
  const data = await patchMyProfile({ email: String(form.email || '').trim() })
  form.email = String(data?.email ?? form.email ?? '')
  userStore.setProfileFields({ email: form.email, updatedAt: data?.updated_at })
  return data
}

async function saveResume(manageLoading = true) {
  const basePayload = {
    real_name: String(form.real_name || '').trim(),
    gender: form.gender || null,
    age: form.age === null || form.age === undefined || form.age === '' ? null : Number(form.age),
    address: String(form.address || '').trim(),
    bio: buildBioArray(),
    is_public: Boolean(form.is_public),
  }
  if (!basePayload.real_name) {
    throw new Error(isZh.value ? '真实姓名为必填' : 'Real name is required')
  }
  if (manageLoading) isSavingResume.value = true
  try {
    const extended = {
      ...basePayload,
      job_title: String(extras.job_title || '').trim() || undefined,
      education: String(extras.education || '').trim() || undefined,
      department: String(extras.department || '').trim() || undefined,
    }
    let data = null
    try {
      data = await createOrUpdateResume(extended)
    } catch (e) {
      if (e?.status === 422) {
        warningStore.showWarning(isZh.value ? '后端暂不支持部分扩展字段，已仅保存核心字段' : 'Backend rejected extra fields; saved core fields only')
        data = await createOrUpdateResume(basePayload)
      } else { throw e }
    }
    resume.value = data || resume.value
    return data
  } catch (e) {
    throw e
  } finally {
    if (manageLoading) isSavingResume.value = false
  }
}

async function saveAll() {
  if (isSavingResume.value) return
  isSavingResume.value = true
  try {
    // Save the profile first because the backend copies its email to the resume.
    await saveProfile()
    await saveResume(false)
    successStore.showSuccess(isZh.value ? '邮箱和履历已保存' : 'Email and resume saved')
  } catch (e) {
    errorStore.showError(isZh.value ? `保存失败：${e?.message || e}` : `Save failed: ${e?.message || e}`)
  } finally {
    isSavingResume.value = false
  }
}

onMounted(async () => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  requestAnimationFrame(() => { pageEnter.value = true })
  await loadAll()
})
</script>


<style scoped>
.reveal {
  opacity: 0;
  transform: translate3d(0, 22px, 0);
  filter: blur(10px);
  transition: opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1), transform 0.9s cubic-bezier(0.16, 1, 0.3, 1), filter 0.9s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--d, 0ms);
  will-change: opacity, transform, filter;
}
.reveal.is-in { opacity: 1; transform: translate3d(0, 0, 0); filter: blur(0); }
@media (prefers-reduced-motion: reduce) { .reveal { transition: none; opacity: 1; transform: none; filter: none; } }

.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }

.resume-page { min-height: 100vh; position: relative; overflow: hidden; background: #ffffff; }

.resume-container { position: relative; max-width: 1400px; margin: 0 auto; padding: 120px 24px 148px; }

/* Meta bar */
.meta-bar { margin: 0 auto 32px; max-width: 860px; display: flex; align-items: flex-end; gap: 32px; padding: 0; background: transparent; position: relative; z-index: 20; }
.meta-field { display: flex; flex-direction: column; gap: 8px; min-width: 0; flex: 1; position: relative; }
.meta-label { font-size: 13px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(0, 0, 0, 0.5); }
.meta-control { height: 48px; width: 100%; border-radius: 0; border: none; border-bottom: 2px solid rgba(0, 0, 0, 0.15); background: transparent; padding: 0; font-size: 18px; color: #000000; outline: none; transition: border-color 0.2s ease; }
.meta-control:hover { border-bottom-color: rgba(0, 0, 0, 0.4); }
.meta-control:focus { border-bottom-color: #000000; }
.meta-control::placeholder { color: rgba(0, 0, 0, 0.3); }

.preview { min-width: 0; position: relative; z-index: 1; }
.detail { padding-top: 6px; }

/* Hero */
.hero { text-align: center; padding: 16px 0 0; }
.avatar-section { display: flex; justify-content: center; margin-bottom: 32px; }
.avatar-uploader { cursor: pointer; user-select: none; }
.avatar-circle { width: 140px; height: 140px; border-radius: 999px; overflow: hidden; border: 4px solid #fff; background: rgba(255, 255, 255, 0.9); box-shadow: 0 20px 50px rgba(15, 23, 42, 0.2); position: relative; display: grid; place-items: center; transition: transform 0.15s ease, box-shadow 0.15s ease; }
.avatar-uploader:hover .avatar-circle { transform: translateY(-3px); box-shadow: 0 24px 60px rgba(15, 23, 42, 0.25); }
.avatar-circle img { width: 100%; height: 100%; object-fit: cover; opacity: 1; transition: opacity 0.4s ease; }
.avatar-circle.avatar-loading img { opacity: 0; }
.avatar-skeleton { position: absolute; inset: 0; background: linear-gradient(90deg, rgba(0,0,0,0.06) 25%, rgba(0,0,0,0.12) 50%, rgba(0,0,0,0.06) 75%); background-size: 200% 100%; animation: skeleton-shimmer 1.5s infinite; opacity: 0; transition: opacity 0.3s ease; border-radius: 999px; }
.avatar-circle.avatar-loading .avatar-skeleton { opacity: 1; }
@keyframes skeleton-shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
.avatar-letter { width: 100%; height: 100%; display: grid; place-items: center; font-size: 48px; font-weight: 950; color: rgba(15, 23, 42, 0.82); background: radial-gradient(140px 140px at 30% 20%, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.55)); }
.avatar-overlay { position: absolute; inset: 0; display: grid; place-items: center; background: rgba(15, 23, 42, 0.42); color: #fff; opacity: 0; transition: opacity 0.15s ease; }
.avatar-uploader:hover .avatar-overlay { opacity: 1; }
.avatar-uploader.uploading { pointer-events: none; opacity: 0.75; }

.hero-title { margin: 0 auto; max-width: min(1100px, 100%); font-size: 72px; line-height: 1.08; letter-spacing: -0.02em; font-weight: 700; color: #000000; }
.hero-dek { margin: 24px auto 0; max-width: 860px; font-size: 24px; line-height: 1.6; color: rgba(0, 0, 0, 0.7); }
.hero-title-input, .hero-dek-input { display: block; width: 100%; border: 0; outline: none; resize: none; background: transparent; text-align: center; }
.hero-title-input::placeholder, .hero-dek-input::placeholder { color: rgba(0, 0, 0, 0.35); }

.divider { height: 1px; background: rgba(0, 0, 0, 0.12); margin: 60px 0 24px; }

.content { max-width: 860px; margin: 0 auto; }
.section-label { font-size: 20px; font-weight: 700; letter-spacing: 0.02em; text-transform: uppercase; color: #000000; margin-bottom: 24px; }

/* Info row */
.info-row { display: flex; align-items: flex-end; gap: 32px; margin-bottom: 24px; }
.info-field { display: flex; flex-direction: column; gap: 8px; min-width: 0; flex: 1; }
.info-label { font-size: 13px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(0, 0, 0, 0.5); }
.info-control { height: 48px; width: 100%; border-radius: 0; border: none; border-bottom: 2px solid rgba(0, 0, 0, 0.15); background: transparent; padding: 0; font-size: 18px; color: #000000; outline: none; transition: border-color 0.2s ease; }
.info-control:hover { border-bottom-color: rgba(0, 0, 0, 0.4); }
.info-control:focus { border-bottom-color: #000000; }
.info-control::placeholder { color: rgba(0, 0, 0, 0.3); }

/* Visual editor - Word style */
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.toolbar-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  background: #ffffff;
  color: rgba(0, 0, 0, 0.7);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toolbar-btn:hover {
  border-color: #000000;
  color: #000000;
  background: rgba(0, 0, 0, 0.02);
}

.toolbar-btn.uploading {
  opacity: 0.5;
  cursor: wait;
}

.word-editor {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 16px;
  padding: 32px;
  min-height: 400px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.editor-block { position: relative; margin-bottom: 4px; }
.editor-block--image { margin-bottom: 20px; }
.editor-block--focused .block-editable { background: rgba(0, 0, 0, 0.01); }

.block-text { position: relative; }

.block-editable {
  width: 100%;
  min-height: 1.8em;
  outline: none;
  font-size: 20px;
  line-height: 1.2;
  color: #000000;
  padding: 8px 0;
  border: none;
  background: transparent;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.block-editable:empty::before {
  content: attr(data-placeholder);
  color: rgba(0, 0, 0, 0.3);
  pointer-events: none;
}

.block-editable:focus {
  outline: none;
  background: rgba(0, 0, 0, 0.03);
}

.block-image { position: relative; margin: 16px 0; border-radius: 16px; overflow: hidden; }
.block-image-preview { width: 100%; height: auto; display: block; }

.block-remove {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  border-radius: 50%;
  color: #fff;
  cursor: pointer;
  display: grid;
  place-items: center;
  opacity: 0;
  transition: all 0.15s ease;
}

.block-image:hover .block-remove { opacity: 1; }
.block-remove:hover { background: rgba(220, 38, 38, 0.9); }

.editor-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  cursor: text;
}

.empty-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(0, 0, 0, 0.35);
  font-size: 16px;
}

.content-footer { margin-top: 16px; }
.content-hint { font-size: 14px; color: rgba(0, 0, 0, 0.45); }

.loading-hint { font-size: 13px; color: rgba(0, 0, 0, 0.55); padding: 8px 0; text-align: center; margin-top: 24px; }

/* Bottom bar */
.bottom-bar { position: fixed; left: 0; right: 0; bottom: 0; z-index: 40; background: #ffffff; border-top: 1px solid rgba(0, 0, 0, 0.1); box-shadow: 0 -6px 32px rgba(0, 0, 0, 0.08); }
.bottom-inner { max-width: 1400px; margin: 0 auto; padding: 20px 24px; display: flex; align-items: center; justify-content: space-between; gap: 24px; }
.bottom-left { min-width: 0; }
.bottom-title { font-size: 18px; font-weight: 700; color: #000000; letter-spacing: -0.01em; }
.bottom-sub { font-size: 14px; color: rgba(0, 0, 0, 0.7); margin-top: 4px; }
.bottom-right { display: flex; align-items: center; gap: 12px; flex-shrink: 0; }

/* Toggle group */
.toggle-group { display: flex; align-items: center; gap: 10px; margin-right: 8px; }
.toggle-label { font-size: 14px; font-weight: 600; color: #000000; }

/* Theme checkbox toggle */
.theme-checkbox {
  --toggle-size: 10px;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  width: 6.25em;
  height: 3.125em;
  background: linear-gradient(to right, #efefef 50%, #2a2a2a 50%) no-repeat;
  background-size: 205%;
  background-position: 0;
  transition: 0.4s;
  border-radius: 99em;
  position: relative;
  cursor: pointer;
  font-size: var(--toggle-size);
}
.theme-checkbox::before {
  content: "";
  width: 2.25em;
  height: 2.25em;
  position: absolute;
  top: 0.438em;
  left: 0.438em;
  background: linear-gradient(to right, #efefef 50%, #2a2a2a 50%) no-repeat;
  background-size: 205%;
  background-position: 100%;
  border-radius: 50%;
  transition: 0.4s;
}
.theme-checkbox:checked::before {
  left: calc(100% - 2.25em - 0.438em);
  background-position: 0;
}
.theme-checkbox:checked {
  background-position: 100%;
}

/* Buttons */
.btn {
  height: 36px;
  padding: 0 16px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  cursor: pointer;
  border: 1px solid #000000;
  background: transparent;
  color: #000000;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateY(0);
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
  box-shadow: none;
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
.btn.primary:active:not(:disabled) {
  background: #000000;
}
.btn.ghost {
  background: transparent;
  border-color: #000000;
  color: #000000;
}
.btn.ghost:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.06);
  border-color: #000000;
}

@media (max-width: 900px) {
  .resume-container { padding: 104px 20px 260px; }
  .meta-bar, .info-row { align-items: stretch; flex-direction: column; gap: 18px; }
  .hero-title { font-size: clamp(38px, 11vw, 54px); }
  .hero-dek { margin-top: 18px; font-size: 17px; }
  .avatar-circle { width: 112px; height: 112px; }
  .divider { margin: 40px 0 22px; }
  .section-label { font-size: 17px; }
  .editor-toolbar { overflow-x: auto; flex-wrap: nowrap; }
  .toolbar-btn { flex: 0 0 auto; min-height: 42px; }
  .word-editor { padding: 18px 14px; }
  .bottom-inner { align-items: stretch; flex-direction: column; gap: 14px; padding: 16px 20px; }
  .bottom-right { width: 100%; flex-wrap: wrap; }
  .toggle-group { width: 100%; justify-content: space-between; margin-right: 0; }
  .bottom-right .btn { flex: 1 1 130px; min-height: 44px; }
}
</style>
