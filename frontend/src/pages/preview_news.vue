<template>
  <section class="preview-page">
    <div class="preview-container">
      <div v-if="!canManage" class="no-access" role="status">
        {{ i18n.locale === 'zh' ? '当前账号没有发布新闻权限，或未登录。' : 'No permission to publish news (or not logged in).' }}
      </div>

      <div class="meta-bar reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }" aria-label="Meta editor">
        <label class="meta-field">
          <span class="meta-label">{{ t('user.newsFieldSlug') }}</span>
          <input
            class="meta-control meta-control--slug"
            v-model.trim="draft.slug"
            placeholder="News"
            :disabled="isPublishing"
          />
        </label>

        <div class="meta-field" ref="categoryDropdownEl">
          <span class="meta-label">{{ i18n.locale === 'zh' ? '分类' : 'Category' }}</span>
          <button
            class="meta-control meta-select"
            type="button"
            :disabled="isPublishing"
            :aria-expanded="isCategoryOpen ? 'true' : 'false'"
            aria-haspopup="listbox"
            @click="toggleCategory"
          >
            <span class="meta-select__value">{{ categoryLabel }}</span>
            <span class="meta-select__chev" aria-hidden="true">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path
                  d="M6 9l6 6 6-6"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
          </button>

          <div
            v-if="isCategoryOpen"
            class="meta-options"
            role="listbox"
            :aria-label="i18n.locale === 'zh' ? '选择分类' : 'Choose category'"
          >
            <button
              v-for="c in categoryOptions"
              :key="c.value"
              class="meta-option"
              type="button"
              role="option"
              :aria-selected="draft.category === c.value ? 'true' : 'false'"
              @click="selectCategory(c.value)"
            >
              <span class="meta-option__label">{{ c.label }}</span>
              <span v-if="draft.category === c.value" class="meta-option__tick" aria-hidden="true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M20 6L9 17l-5-5"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>
            </button>
          </div>
        </div>

        <label class="meta-field">
          <span class="meta-label">{{ i18n.locale === 'zh' ? '作者' : 'Author' }}</span>
          <input class="meta-control" v-model.trim="draft.author" placeholder="DAIL Tech" :disabled="isPublishing" />
        </label>
      </div>

      <main class="preview reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '160ms' }" aria-label="Preview">
        <!-- Match published news layout (same as NewsDetail.vue) -->
        <div class="detail">
          <header class="hero" aria-label="Article header">
            <div class="hero-meta" role="group" aria-label="Article meta">
              <time class="hero-meta__item hero-meta__item--date" :datetime="draft.publishedAt">
                {{ formatDateLong(draft.publishedAt, i18n.locale) }}
              </time>
              <span class="hero-meta__dot" aria-hidden="true"></span>
              <span class="hero-meta__item">{{ categoryLabel }}</span>
            </div>

            <!-- Inline editing (no side form) -->
            <textarea
              class="hero-title hero-title-input"
              v-model="draft.title"
              :disabled="isPublishing"
              rows="2"
              :placeholder="i18n.locale === 'zh' ? '请输入标题…' : 'Write the headline…'"
            ></textarea>

            <textarea
              class="hero-dek hero-dek-input"
              v-model="draft.subtitle"
              :disabled="isPublishing"
              rows="2"
              :placeholder="i18n.locale === 'zh' ? '副标题（可选）…' : 'Optional short dek…'"
            ></textarea>

            <!-- 封面图上传 - 放在标题下方，横线上方 -->
            <div class="cover-section reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '200ms' }">
              <div v-if="coverImage" class="cover-preview">
                <img :src="coverImage.url" alt="Cover preview" class="cover-img" />
                <button
                  class="cover-remove"
                  type="button"
                  @click="removeCoverImage"
                  :disabled="isPublishing"
                  :aria-label="i18n.locale === 'zh' ? '移除封面' : 'Remove cover'"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
              <label v-else class="cover-dropzone" :class="{ uploading: isUploadingCover }">
                <input
                  ref="coverInputRef"
                  type="file"
                  accept="image/jpeg,image/png,image/gif,image/webp"
                  class="sr-only"
                  :disabled="isPublishing || isUploadingCover"
                  @change="handleCoverUpload"
                />
                <div class="dropzone-content">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" class="dropzone-icon">
                    <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="1.5"/>
                    <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
                    <path d="M21 15l-5-5L5 21" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span class="dropzone-text">
                    {{ isUploadingCover 
                      ? (i18n.locale === 'zh' ? '上传中...' : 'Uploading...') 
                      : (i18n.locale === 'zh' ? '添加封面图' : 'Add cover image') 
                    }}
                  </span>
                </div>
              </label>
            </div>
          </header>

          <div class="divider" aria-hidden="true"></div>

          <!-- 图文混排编辑区域 - Word风格 -->
          <div class="content">
            <div class="section-label">{{ i18n.locale === 'zh' ? '正文内容' : 'Content' }}</div>
            
            <!-- 工具栏 -->
            <div class="editor-toolbar">
              <label class="toolbar-btn" :class="{ uploading: isUploadingContent }">
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/gif,image/webp"
                  class="sr-only"
                  :disabled="isPublishing || isUploadingContent"
                  @change="handleInsertImageAtCursor($event)"
                />
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="1.5"/>
                  <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
                  <path d="M21 15l-5-5L5 21" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>{{ isUploadingContent ? (i18n.locale === 'zh' ? '上传中...' : 'Uploading...') : (i18n.locale === 'zh' ? '插入图片' : 'Insert Image') }}</span>
              </label>
            </div>
            
            <!-- Word风格编辑区 -->
            <div class="word-editor" ref="wordEditorRef">
              <div 
                v-for="(block, idx) in contentBlocks" 
                :key="block.id" 
                class="editor-block"
                :class="{ 
                  'editor-block--image': block.type === 'image',
                  'editor-block--focused': focusedBlockIndex === idx
                }"
              >
                <!-- 文本块 - 自动扩展的编辑区 -->
                <div v-if="block.type === 'text'" class="block-text">
                  <div
                    class="block-editable"
                    contenteditable="true"
                    :data-placeholder="i18n.locale === 'zh' ? '输入内容...' : 'Start typing...'"
                    :data-index="idx"
                    @focus="focusedBlockIndex = idx"
                    @blur="handleTextBlur($event, idx)"
                    @keydown="handleKeyDown($event, idx)"
                    @paste="handlePaste($event, idx)"
                  ></div>
                </div>

                <!-- 图片块 -->
                <div v-else-if="block.type === 'image'" class="block-image" @click="focusedBlockIndex = idx">
                  <img :src="block.url" alt="Image" class="block-image-preview" />
                  <button
                    class="block-remove block-remove--image"
                    type="button"
                    @click.stop="removeBlock(idx)"
                    :disabled="isPublishing"
                    :title="i18n.locale === 'zh' ? '删除图片' : 'Remove image'"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- 空状态 -->
              <div v-if="contentBlocks.length === 0" class="editor-empty" @click="addFirstTextBlock">
                <div class="empty-hint">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                  <span>{{ i18n.locale === 'zh' ? '点击此处开始编写...' : 'Click here to start writing...' }}</span>
                </div>
              </div>
            </div>

            <div class="content-footer">
              <div class="content-hint">
                {{ i18n.locale === 'zh' ? '段落：' : 'Paragraphs: ' }}{{ textBlockCount }}
                <span v-if="imageBlockCount > 0"> · {{ i18n.locale === 'zh' ? '图片：' : 'Images: ' }}{{ imageBlockCount }}</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Bottom action bar (replaces top header) -->
    <div class="bottom-bar" role="region" aria-label="Publisher actions">
      <div class="bottom-inner">
        <div class="bottom-left">
          <div class="bottom-title">{{ i18n.locale === 'zh' ? '新闻预览' : 'News preview' }}</div>
          <div class="bottom-sub">
            {{ i18n.locale === 'zh' ? '编辑标题/内容，并以正式发布格式预览。' : 'Edit fields and preview with the published layout.' }}
          </div>
        </div>
        <div class="bottom-right">
          <button class="btn ghost" type="button" @click="router.back()">
            {{ i18n.locale === 'zh' ? '返回' : 'Back' }}
          </button>
          <button class="btn ghost" type="button" @click="resetDraft" :disabled="isPublishing">
            {{ i18n.locale === 'zh' ? '重置' : 'Reset' }}
          </button>
          <button class="btn primary" type="button" @click="publish" :disabled="isPublishing || !canManage">
            {{ isPublishing ? (i18n.locale === 'zh' ? '发布中…' : 'Publishing…') : (i18n.locale === 'zh' ? '发布' : 'Publish') }}
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'
import { useErrorStore } from '@/stores/error'
import { useSuccessStore } from '@/stores/success'
import { useWarningStore } from '@/stores/warning'
import { useUserStore } from '@/stores/user'
import { createNews, formatDateLong } from '@/services/newsService'
import { uploadImage, linkImageToNews } from '@/services/imageService'

const router = useRouter()
const i18n = useI18nStore()
const errorStore = useErrorStore()
const successStore = useSuccessStore()
const warningStore = useWarningStore()
const userStore = useUserStore()
const t = (key, vars) => i18n.t(key, vars)

function todayYmd() {
  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

function computeCanManageFromToken(token) {
  try {
    const [, payload] = String(token || '').split('.')
    if (!payload) return false
    const json = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    const role = json?.role
    // role >= 3 can publish/delete news
    if (typeof role === 'number' && role >= 3) return true
    if (!('role' in json)) return true
    return false
  } catch {
    return !!token
  }
}

const canManage = computed(() => computeCanManageFromToken(userStore.accessToken))

const categoryOptions = computed(() => [
  { value: 'Alliance', label: t('news.categories.Alliance') },
  { value: 'Milestone', label: t('news.categories.Milestone') },
  { value: 'Partnership', label: t('news.categories.Partnership') },
  { value: 'News', label: t('news.categories.News') },
])

const draft = ref({
  slug: '',
  category: 'News',
  publishedAt: todayYmd(),
  title: '',
  subtitle: '',
  author: '',
})

const isPublishing = ref(false)

// 图片上传相关
const coverImage = ref(null) // { id, url, file }
const isUploadingCover = ref(false)
const isUploadingContent = ref(false)
const coverInputRef = ref(null)
const insertAfterIndex = ref(-1) // 记录图片插入位置

// 块编辑器：每个块是 { id, type: 'text'|'image', content?, url?, imageId?, caption? }
let blockIdCounter = 0
const contentBlocks = ref([
  { id: blockIdCounter++, type: 'text', content: '' }
])

// Word编辑器相关
const wordEditorRef = ref(null)
const textBlockRefs = ref([])
const focusedBlockIndex = ref(0)

// 允许的图片类型
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
const MAX_IMAGE_SIZE = 10 * 1024 * 1024 // 10MB

function validateImageFile(file) {
  if (!file) return { valid: false, error: '请选择图片文件' }
  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    return { valid: false, error: '仅支持 JPG、PNG、GIF、WebP 格式' }
  }
  if (file.size > MAX_IMAGE_SIZE) {
    return { valid: false, error: '图片大小不能超过 10MB' }
  }
  return { valid: true, error: null }
}

async function handleCoverUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return

  const validation = validateImageFile(file)
  if (!validation.valid) {
    warningStore.showWarning(validation.error)
    return
  }

  isUploadingCover.value = true
  try {
    const result = await uploadImage(file, 'cover')
    coverImage.value = {
      id: result.id,
      url: result.url,
      file: file,
    }
    successStore.showSuccess(i18n.locale === 'zh' ? '封面上传成功' : 'Cover uploaded')
  } catch (e) {
    errorStore.showError(e?.message || (i18n.locale === 'zh' ? '封面上传失败' : 'Cover upload failed'))
  } finally {
    isUploadingCover.value = false
    // 清空input以便重复选择同一文件
    if (coverInputRef.value) coverInputRef.value.value = ''
  }
}

function removeCoverImage() {
  coverImage.value = null
}

// Word风格编辑器操作
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
  // 聚焦到前一个块或后一个块
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
  contentBlocks.value.forEach((block, idx) => {
    if (block.type === 'text') {
      if (editables[editableIndex]) {
        block.content = editables[editableIndex].innerHTML
      }
      editableIndex++
    }
  })
}

// 处理失焦 - 保存内容
function handleTextBlur(event, index) {
  const el = event.target
  contentBlocks.value[index].content = el.innerHTML
}

// 处理键盘事件
function handleKeyDown(event, index) {
  const el = event.target
  
  // Enter 创建新段落（不是 Shift+Enter）
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    
    // 保存当前内容
    syncAllContent()
    
    // 获取光标位置后的内容
    const selection = window.getSelection()
    if (!selection.rangeCount) return
    const range = selection.getRangeAt(0)
    
    // 创建一个临时范围来获取光标后的内容
    const afterRange = range.cloneRange()
    afterRange.selectNodeContents(el)
    afterRange.setStart(range.endContainer, range.endOffset)
    const afterContent = afterRange.cloneContents()
    
    // 创建临时div来获取HTML
    const tempDiv = document.createElement('div')
    tempDiv.appendChild(afterContent)
    const afterHtml = tempDiv.innerHTML
    
    // 删除光标后的内容
    afterRange.deleteContents()
    
    // 更新当前块内容
    contentBlocks.value[index].content = el.innerHTML
    
    // 创建新块并插入光标后的内容
    const newBlock = { id: blockIdCounter++, type: 'text', content: afterHtml }
    contentBlocks.value.splice(index + 1, 0, newBlock)
    
    // 聚焦新块并设置内容
    nextTick(() => {
      const editables = document.querySelectorAll('.block-editable')
      const newEl = editables[index + 1]
      if (newEl) {
        newEl.innerHTML = afterHtml
        newEl.focus()
        // 将光标移到开头
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
  
  // Backspace 在块开头时合并到上一块
  if (event.key === 'Backspace') {
    const selection = window.getSelection()
    if (!selection.rangeCount) return
    const range = selection.getRangeAt(0)
    
    // 只有当光标在最开头且没有选中内容时才处理
    if (!range.collapsed) return
    
    // 检查是否真的在块的最开头
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
      
      // 保存当前内容
      syncAllContent()
      
      // 找到上一个文本块
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
        
        // 合并内容
        prevBlock.content = prevContent + currentContent
        
        // 删除当前块
        contentBlocks.value.splice(index, 1)
        
        // 聚焦到上一块并将光标放在原内容末尾
        nextTick(() => {
          const editables = document.querySelectorAll('.block-editable')
          const targetEl = editables[prevEditableIndex]
          if (targetEl) {
            targetEl.innerHTML = prevBlock.content
            targetEl.focus()
            
            // 将光标放在合并点
            const newSelection = window.getSelection()
            const newRange = document.createRange()
            
            try {
              // 找到合适的位置
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

// 处理粘贴
function handlePaste(event, index) {
  event.preventDefault()
  
  // 获取纯文本
  const text = event.clipboardData.getData('text/plain')
  
  // 插入纯文本
  document.execCommand('insertText', false, text)
}

// 在当前光标位置插入图片
async function handleInsertImageAtCursor(event) {
  const file = event.target.files?.[0]
  if (!file) return

  const validation = validateImageFile(file)
  if (!validation.valid) {
    warningStore.showWarning(validation.error)
    event.target.value = ''
    return
  }

  // 先同步内容
  syncAllContent()

  isUploadingContent.value = true
  
  // 确定插入位置（当前聚焦的块之后）
  const insertIndex = focusedBlockIndex.value >= 0 ? focusedBlockIndex.value : contentBlocks.value.length - 1
  
  try {
    const result = await uploadImage(file, 'content')
    const newBlock = {
      id: blockIdCounter++,
      type: 'image',
      url: result.url,
      imageId: result.id,
      caption: '',
    }
    contentBlocks.value.splice(insertIndex + 1, 0, newBlock)
    
    // 在图片后添加一个空文本块（如果下一个不是文本块）
    if (insertIndex + 2 >= contentBlocks.value.length || contentBlocks.value[insertIndex + 2]?.type !== 'text') {
      contentBlocks.value.splice(insertIndex + 2, 0, { id: blockIdCounter++, type: 'text', content: '' })
    }
    
    successStore.showSuccess(i18n.locale === 'zh' ? '图片已插入' : 'Image inserted')
    
    // 聚焦到图片后的文本块
    nextTick(() => {
      const editables = document.querySelectorAll('.block-editable')
      // 计算新文本块对应的 editable 索引
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
    errorStore.showError(e?.message || (i18n.locale === 'zh' ? '图片上传失败' : 'Image upload failed'))
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

const pageEnter = ref(false)

const isCategoryOpen = ref(false)
const categoryDropdownEl = ref(null)

function toggleCategory() {
  if (isPublishing.value) return
  isCategoryOpen.value = !isCategoryOpen.value
}

function selectCategory(value) {
  draft.value.category = String(value || '').trim() || 'News'
  isCategoryOpen.value = false
}

function resetDraft() {
  draft.value = {
    slug: '',
    category: 'News',
    publishedAt: todayYmd(),
    title: '',
    subtitle: '',
    author: '',
  }
  coverImage.value = null
  contentBlocks.value = [{ id: blockIdCounter++, type: 'text', content: '' }]
  // 清空 contenteditable 元素
  nextTick(() => {
    const editables = document.querySelectorAll('.block-editable')
    editables.forEach(el => {
      el.innerHTML = ''
    })
    if (editables[0]) {
      editables[0].focus()
    }
  })
}

onMounted(() => {
  if (!draft.value.publishedAt) draft.value.publishedAt = todayYmd()
})

onMounted(() => {
  requestAnimationFrame(() => {
    pageEnter.value = true
  })
})

function onDocPointerDown(e) {
  const el = categoryDropdownEl.value
  if (!el) return
  if (!isCategoryOpen.value) return
  if (el === e.target || el.contains(e.target)) return
  isCategoryOpen.value = false
}

function onDocKeyDown(e) {
  if (!isCategoryOpen.value) return
  if (e.key === 'Escape') {
    isCategoryOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('pointerdown', onDocPointerDown, true)
  document.addEventListener('keydown', onDocKeyDown, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', onDocPointerDown, true)
  document.removeEventListener('keydown', onDocKeyDown, true)
})

watch(
  () => userStore.accessToken,
  () => {
    if (!userStore.accessToken) {
      // keep the page visible, but disable publish
    }
  }
)

// 从块生成内容数组（用于发布）
// 将 HTML 转换为纯文本
function htmlToText(html) {
  if (!html) return ''
  // 创建临时元素来解析 HTML
  const temp = document.createElement('div')
  temp.innerHTML = html
  // 将 <br> 转换为换行
  temp.querySelectorAll('br').forEach(br => br.replaceWith('\n'))
  // 将 <div> 和 <p> 转换为换行
  temp.querySelectorAll('div, p').forEach(el => {
    el.prepend(document.createTextNode('\n'))
  })
  return temp.textContent?.trim() || ''
}

// 获取当前编辑器内容（实时从 DOM 读取）
function getCurrentContent() {
  const editables = document.querySelectorAll('.block-editable')
  const result = []
  let imageIndex = 0
  let editableIndex = 0
  
  for (const block of contentBlocks.value) {
    if (block.type === 'text') {
      const el = editables[editableIndex]
      const html = el ? el.innerHTML : block.content
      const text = htmlToText(html)
      if (text) result.push(text)
      editableIndex++
    } else if (block.type === 'image') {
      result.push(`[IMAGE:${imageIndex}]`)
      imageIndex++
    }
  }
  return result
}

const contentParagraphs = computed(() => {
  // 注意：这个计算属性可能不会实时更新，发布时使用 getCurrentContent()
  const result = []
  let imageIndex = 0
  for (const block of contentBlocks.value) {
    if (block.type === 'text') {
      const text = htmlToText(block.content)
      if (text) result.push(text)
    } else if (block.type === 'image') {
      result.push(`[IMAGE:${imageIndex}]`)
      imageIndex++
    }
  }
  return result
})

// 提取所有图片块（用于发布时关联）
const contentImages = computed(() => {
  return contentBlocks.value
    .filter(b => b.type === 'image')
    .map((b, idx) => ({
      id: b.imageId,
      url: b.url,
      position: idx,
      caption: b.caption || '',
    }))
})

const textBlockCount = computed(() => contentBlocks.value.filter(b => b.type === 'text' && htmlToText(b.content)).length)
const imageBlockCount = computed(() => contentBlocks.value.filter(b => b.type === 'image').length)
const paragraphCount = computed(() => textBlockCount.value)

const article = computed(() => ({
  slug: String(draft.value.slug || '').trim(),
  category: String(draft.value.category || '').trim() || 'News',
  publishedAt: String(draft.value.publishedAt || '').trim() || todayYmd(),
  title: String(draft.value.title || '').trim(),
  subtitle: String(draft.value.subtitle || '').trim(),
  author: String(draft.value.author || '').trim(),
  content: contentParagraphs.value,
}))

const categoryLabel = computed(() => {
  const v = article.value.category
  const hit = categoryOptions.value.find((x) => x.value === v)
  return hit?.label || v
})

const dekText = computed(() => {
  const a = article.value
  const fromField = a.subtitle || a.summary || a.dek
  if (typeof fromField === 'string' && fromField.trim()) return fromField.trim()
  const first = Array.isArray(a.content) ? a.content[0] : ''
  return typeof first === 'string' ? first.trim() : ''
})

const stripFromBody = computed(() => {
  const a = article.value
  const fromField = a.subtitle || a.summary || a.dek
  return !(typeof fromField === 'string' && fromField.trim())
})

const bodyParagraphs = computed(() => {
  const a = article.value
  if (!Array.isArray(a.content)) return []
  if (stripFromBody.value) return a.content.slice(1)
  return a.content
})

async function publish() {
  if (isPublishing.value) return
  if (!canManage.value) {
    errorStore.showError(t('user.newsNoAccessText') || (i18n.locale === 'zh' ? '没有权限' : 'No access'))
    return
  }

  // 先同步内容
  syncAllContent()

  const payload = {
    slug: article.value.slug,
    category: article.value.category,
    publishedAt: article.value.publishedAt,
    title: article.value.title,
    subtitle: article.value.subtitle,
    author: article.value.author,
    content: getCurrentContent(),
    // 添加图片信息
    cover_image: coverImage.value?.url || null,
    images: contentImages.value,
  }

  // Basic validation (backend still validates)
  if (!payload.slug || !payload.title || !payload.category || !payload.publishedAt) {
    warningStore.showWarning(i18n.locale === 'zh' ? '请填写 slug / 标题 / 分类 / 日期' : 'Please fill slug / title / category / date')
    return
  }
  if (!Array.isArray(payload.content) || payload.content.length === 0) {
    warningStore.showWarning(i18n.locale === 'zh' ? '请填写正文' : 'Please fill content')
    return
  }

  isPublishing.value = true
  try {
    const data = await createNews(payload)
    const newsId = data?.id

    // 如果有图片且返回了新闻ID，关联图片到新闻
    if (newsId) {
      const imageIds = []
      if (coverImage.value?.id) imageIds.push(coverImage.value.id)
      contentImages.value.forEach((img) => {
        if (img.id) imageIds.push(img.id)
      })

      // 并行关联所有图片
      await Promise.all(
        imageIds.map((imgId) => linkImageToNews(imgId, newsId).catch(() => null))
      )
    }

    successStore.showSuccess(t('user.newsSuccess') || (i18n.locale === 'zh' ? '发布成功' : 'Published'))
    const slug = data?.slug || payload.slug
    if (slug) router.push({ name: 'news-detail', params: { slug } })
  } catch (e) {
    errorStore.showError(e?.message || (i18n.locale === 'zh' ? '发布失败' : 'Failed to publish'))
  } finally {
    isPublishing.value = false
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

.preview-page {
  background: #fbfbfb;
  padding: 120px 24px 148px; /* leave room for bottom bar */
}

.preview-container {
  max-width: 1400px;
  margin: 0 auto;
}

.btn {
  height: 32px;
  padding: 0 10px;
  border-radius: 999px;
  font-weight: 500;
  font-size: 12px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  cursor: pointer;
  border: 1px solid #000000;
  background: transparent;
  color: #000000;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn:active:not(:disabled) {
  background: #000000;
  color: #ffffff;
  transform: scale(0.97);
}

.btn.primary {
  background: #000000;
  border-color: #000000;
  color: #ffffff;
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

.no-access {
  padding: 12px 0 18px;
  color: #000000;
  font-size: 14px;
}

.meta-bar {
  margin: 0 auto 24px;
  max-width: 860px;
  display: flex;
  align-items: flex-end;
  gap: 24px;
  padding: 0;
  background: transparent;
  position: relative;
  z-index: 20;
}

.meta-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  flex: 1;
  position: relative;
}

.meta-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(0, 0, 0, 0.45);
}

.meta-control {
  height: 40px;
  width: 100%;
  border-radius: 0;
  border: none;
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
  background: transparent;
  padding: 0;
  font-size: 15px;
  color: #000000;
  outline: none;
  transition: border-color 0.2s ease;
}

.meta-control--slug {
  color: rgba(0, 0, 0, 0.7);
}

.meta-control--slug::placeholder {
  color: rgba(0, 0, 0, 0.3);
  opacity: 1;
}

.meta-control:hover {
  border-bottom-color: rgba(0, 0, 0, 0.4);
}

.meta-control:focus {
  border-bottom-color: #000000;
  box-shadow: none;
}

.meta-control::placeholder {
  color: rgba(0, 0, 0, 0.3);
  opacity: 1;
}

.meta-select {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  text-align: left;
  cursor: pointer;
}

.meta-select__value {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta-select__chev {
  width: 16px;
  height: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 0, 0, 0.4);
  flex-shrink: 0;
  transition: color 0.2s ease;
}

.meta-select:hover .meta-select__chev {
  color: #000000;
}

.meta-options {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 100%;
  min-width: 180px;
  z-index: 80;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

.meta-option {
  width: 100%;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  color: #000000;
}

.meta-option:hover,
.meta-option:focus-visible {
  outline: none;
  background: rgba(0, 0, 0, 0.06);
}

.meta-option__label {
  font-size: 13px;
  font-weight: 600;
}

.meta-option__tick {
  color: #000000;
}

.preview {
  min-width: 0;
  position: relative;
  z-index: 1;
}

/* --- Published layout (copied from NewsDetail.vue) --- */
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
  color: #000000;
  margin-bottom: 28px;
}

.hero-meta__item--date {
  color: rgba(0, 0, 0, 0.55);
}

.hero-meta__dot {
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.35);
}

.hero-meta__item {
  white-space: nowrap;
}

.hero-title {
  margin: 0 auto;
  max-width: min(1100px, 100%);
  font-size: 64px;
  line-height: 1.12;
  letter-spacing: 0.01em;
  font-weight: 650;
  color: #000000;
}

.hero-dek {
  margin: 28px auto 0;
  max-width: 860px;
  font-size: 20px;
  line-height: 1.7;
  color: #000000;
}

.hero-title-input,
.hero-dek-input {
  display: block;
  width: 100%;
  border: 0;
  outline: none;
  resize: none;
  background: transparent;
  text-align: center;
}

.hero-title-input::placeholder,
.hero-dek-input::placeholder {
  color: rgba(0, 0, 0, 0.45);
  opacity: 1;
}

.hero-title-input {
  padding: 0;
}

.hero-dek-input {
  padding: 0;
}

.hero-title-input:disabled,
.hero-dek-input:disabled {
  opacity: 0.75;
}

.divider {
  height: 1px;
  background: rgba(0, 0, 0, 0.18);
  margin: 52px 0 18px;
}

.content {
  max-width: 860px;
  margin: 0 auto;
}

.content-textarea {
  width: 100%;
  border: 1px solid #000000;
  outline: none;
  background: transparent;
  resize: vertical;
  font-size: 18px;
  line-height: 1.8;
  color: #000000;
  padding: 14px 16px;
  border-radius: 14px;
  min-height: 260px;
  margin-top: 6px;
}

.content-textarea:focus {
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.10);
}

.content-textarea::placeholder {
  color: rgba(0, 0, 0, 0.45);
  opacity: 1;
}

.content-footer {
  margin-top: 10px;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.content-hint {
  font-size: 12px;
  color: #000000;
}

.content-preview-hint {
  font-size: 12px;
  color: #000000;
}

/* Bottom action bar */
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
  max-width: 720px;
}

.bottom-right {
  display: inline-flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

/* Bigger controls inside wider bottom bar */
.bottom-bar .btn {
  height: 36px;
  padding: 0 16px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.03em;
}

/* 图片上传样式 */
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

.section-label {
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #000000;
  margin-bottom: 12px;
}

/* 封面图上传 */
.cover-section {
  max-width: 860px;
  margin: 32px auto 0;
}

.cover-dropzone {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 999px;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cover-dropzone:hover {
  border-color: #000000;
  background: rgba(0, 0, 0, 0.03);
}

.cover-dropzone.uploading {
  opacity: 0.6;
  cursor: wait;
}

.dropzone-content {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(0, 0, 0, 0.5);
}

.dropzone-icon {
  color: rgba(0, 0, 0, 0.4);
}

.dropzone-text {
  font-size: 13px;
  font-weight: 500;
}

.cover-preview {
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  background: #f5f5f5;
}

.cover-img {
  width: 100%;
  height: auto;
  max-height: 360px;
  object-fit: cover;
  display: block;
}

.cover-remove {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.6);
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.2s ease;
}

.cover-preview:hover .cover-remove {
  opacity: 1;
}

.cover-remove:hover {
  background: #000000;
  transform: scale(1.1);
}

/* 内容图片上传 */
.images-section {
  max-width: 860px;
  margin: 24px auto 0;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 10px;
  overflow: hidden;
  background: #f0f0f0;
}

.image-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-actions {
  position: absolute;
  top: 6px;
  right: 6px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.image-item:hover .image-actions {
  opacity: 1;
}

.image-action-btn {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.7);
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.image-action-btn:hover {
  background: #000000;
  transform: scale(1.1);
}

.image-action-btn--danger:hover {
  background: #dc2626;
}

.image-index {
  position: absolute;
  bottom: 6px;
  left: 6px;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.7);
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
}

.image-add {
  aspect-ratio: 1;
  border: 2px dashed rgba(0, 0, 0, 0.25);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.image-add:hover {
  border-color: #000000;
  background: rgba(255, 255, 255, 0.9);
}

.image-add.uploading {
  opacity: 0.7;
  cursor: wait;
}

.image-add-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: rgba(0, 0, 0, 0.55);
}

.image-add-content span {
  font-size: 11px;
  font-weight: 600;
}

/* 可视化块编辑器 - Word风格 */
.word-editor {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 16px;
  padding: 32px;
  min-height: 400px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

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

.editor-block {
  position: relative;
  margin-bottom: 4px;
}

.editor-block--focused .block-editable {
  background: rgba(0, 0, 0, 0.01);
}

/* 文本块 - contenteditable */
.block-text {
  position: relative;
}

.block-editable {
  width: 100%;
  min-height: 1.8em;
  outline: none;
  font-size: 18px;
  line-height: 1.2;
  color: #000000;
  padding: 8px 0;
  border: none;
  background: transparent;
  word-wrap: break-word;
  overflow-wrap: break-word;
  border-radius: 8px;
  transition: background 0.2s ease, box-shadow 0.2s ease;
}

.block-editable:empty::before {
  content: attr(data-placeholder);
  color: rgba(0, 0, 0, 0.3);
  pointer-events: none;
}

.block-editable:hover {
  background: rgba(0, 0, 0, 0.02);
}

.block-editable:focus {
  outline: none;
  background: rgba(0, 0, 0, 0.03);
}

/* 图片块 */
.block-image {
  position: relative;
  margin: 16px 0;
  border-radius: 12px;
  overflow: hidden;
  background: #f5f5f5;
}

.block-image-preview {
  width: 100%;
  max-height: 500px;
  object-fit: contain;
  display: block;
}

.block-remove {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.6);
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.2s ease;
}

.block-image:hover .block-remove {
  opacity: 1;
}

.block-remove:hover {
  background: #dc2626;
  transform: scale(1.1);
}

/* 空状态 */
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
</style>

