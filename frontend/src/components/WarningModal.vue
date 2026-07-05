<template>
  <Teleport to="body">
    <div v-if="modelValue" class="modal-overlay" @click.self="handleClose">
      <div class="modal-box">
        <div class="modal-icon" :class="`modal-icon--${type}`">
          <!-- Warning icon -->
          <svg v-if="type === 'warning'" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <!-- Info icon -->
          <svg v-else-if="type === 'info'" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <!-- Error icon -->
          <svg v-else-if="type === 'error'" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          <!-- Success icon -->
          <svg v-else-if="type === 'success'" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <h3 class="modal-title">{{ title }}</h3>
        <p class="modal-text">{{ message }}</p>
        <div class="modal-actions">
          <button v-if="showCancel" class="modal-btn modal-btn--ghost" @click="handleCancel">
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
import { computed } from 'vue'
import { useI18nStore } from '@/stores/i18n'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'warning', // 'warning' | 'info' | 'error' | 'success'
    validator: (v) => ['warning', 'info', 'error', 'success'].includes(v)
  },
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    default: ''
  },
  confirmText: {
    type: String,
    default: ''
  },
  cancelText: {
    type: String,
    default: ''
  },
  showCancel: {
    type: Boolean,
    default: false
  },
  closeOnOverlay: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const i18n = useI18nStore()
const isZh = computed(() => i18n.locale === 'zh')

// 默认文案
const confirmText = computed(() => props.confirmText || (isZh.value ? '我知道了' : 'Got it'))
const cancelText = computed(() => props.cancelText || (isZh.value ? '取消' : 'Cancel'))

function handleClose() {
  if (props.closeOnOverlay) {
    emit('update:modelValue', false)
  }
}

function handleConfirm() {
  emit('confirm')
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
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 24px;
}

.modal-box {
  background: #fff;
  border-radius: 20px;
  padding: 40px;
  max-width: 400px;
  width: 100%;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  animation: modal-in 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-icon {
  margin-bottom: 16px;
}

.modal-icon--warning {
  color: #f59e0b;
}

.modal-icon--info {
  color: #3b82f6;
}

.modal-icon--error {
  color: #ef4444;
}

.modal-icon--success {
  color: #10b981;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #0b0f19;
  margin: 0 0 12px;
}

.modal-text {
  font-size: 15px;
  color: #6b7280;
  margin: 0 0 28px;
  line-height: 1.6;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.modal-btn {
  padding: 12px 32px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-btn--primary {
  background: #0b0f19;
  color: #fff;
}

.modal-btn--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(11, 15, 25, 0.25);
}

.modal-btn--ghost {
  background: transparent;
  color: #6b7280;
  border: 1px solid #e5e7eb;
}

.modal-btn--ghost:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}
</style>
