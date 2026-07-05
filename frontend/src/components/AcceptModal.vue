<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-overlay" @click.self="handleClose">
      <div class="modal-box">
        <div class="modal-icon modal-icon--success">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <h3 class="modal-title">{{ title }}</h3>
        <p class="modal-desc">{{ description }}</p>
        
        <div class="modal-input-group">
          <label class="modal-label">{{ inputLabel }}</label>
          <textarea
            v-model="inputMessage"
            class="modal-textarea"
            :placeholder="placeholder"
            rows="3"
          ></textarea>
        </div>

        <div class="modal-actions">
          <button class="modal-btn modal-btn--ghost" @click="handleCancel">
            {{ cancelText }}
          </button>
          <button class="modal-btn modal-btn--primary" @click="handleConfirm">
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18nStore } from '@/stores/i18n'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  inputLabel: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  defaultMessage: { type: String, default: '' },
  confirmText: { type: String, default: '' },
  cancelText: { type: String, default: '' },
  closeOnOverlay: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const i18n = useI18nStore()
const isZh = computed(() => i18n.locale === 'zh')

const inputMessage = ref('')

// 当弹窗打开时重置消息
watch(() => props.modelValue, (val) => {
  if (val) {
    inputMessage.value = props.defaultMessage
  }
})

const confirmText = computed(() => props.confirmText || (isZh.value ? '确认通过' : 'Confirm'))
const cancelText = computed(() => props.cancelText || (isZh.value ? '取消' : 'Cancel'))

function handleClose() {
  if (props.closeOnOverlay) {
    emit('update:modelValue', false)
  }
}

function handleConfirm() {
  emit('confirm', inputMessage.value)
  emit('update:modelValue', false)
}

function handleCancel() {
  emit('cancel')
  emit('update:modelValue', false)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 32px;
}

.modal-box {
  background: #fff;
  border-radius: 28px;
  padding: 56px 52px;
  max-width: 560px;
  width: 100%;
  text-align: center;
  box-shadow: 0 32px 80px rgba(0, 0, 0, 0.18);
  animation: modal-in 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modal-in {
  from { opacity: 0; transform: scale(0.92) translateY(24px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.modal-icon {
  margin-bottom: 24px;
}

.modal-icon--success {
  color: #10b981;
}

.modal-icon svg {
  width: 64px;
  height: 64px;
}

.modal-title {
  font-size: 28px;
  font-weight: 700;
  color: #0b0f19;
  margin: 0 0 12px;
  letter-spacing: -0.02em;
}

.modal-desc {
  font-size: 17px;
  color: #6b7280;
  margin: 0 0 36px;
  line-height: 1.6;
}

.modal-input-group {
  text-align: left;
  margin-bottom: 36px;
}

.modal-label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 12px;
}

.modal-textarea {
  width: 100%;
  padding: 16px 18px;
  border: 2px solid #e5e7eb;
  border-radius: 14px;
  font-size: 16px;
  line-height: 1.6;
  resize: vertical;
  min-height: 120px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  font-family: inherit;
}

.modal-textarea:focus {
  outline: none;
  border-color: #0b0f19;
  box-shadow: 0 0 0 4px rgba(11, 15, 25, 0.08);
}

.modal-textarea::placeholder {
  color: #9ca3af;
}

.modal-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding-top: 8px;
}

.modal-btn {
  padding: 16px 40px;
  border: none;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-btn--primary {
  background: #10b981;
  color: #fff;
}

.modal-btn--primary:hover {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(16, 185, 129, 0.35);
}

.modal-btn--ghost {
  background: transparent;
  color: #6b7280;
  border: 2px solid #e5e7eb;
}

.modal-btn--ghost:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}
</style>
