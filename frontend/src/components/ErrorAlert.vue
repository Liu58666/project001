<template>
  <Transition name="error-alert">
    <div
      v-if="message"
      class="error-alert"
      :class="{ 'error-alert--visible': message }"
    >
      <button
        type="button"
        :aria-label="$t('common.close')"
        class="error-alert__close"
        @click="close"
      >
        <svg
          stroke="currentColor"
          fill="none"
          stroke-width="2"
          viewBox="0 0 24 24"
          stroke-linecap="round"
          stroke-linejoin="round"
          height="16"
          width="16"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M18 6 6 18"></path>
          <path d="m6 6 12 12"></path>
        </svg>
      </button>
      <p class="error-alert__message">
        <svg
          stroke="currentColor"
          fill="none"
          stroke-width="2"
          viewBox="0 0 24 24"
          stroke-linecap="round"
          stroke-linejoin="round"
          height="28"
          width="28"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"
          ></path>
          <path d="M12 9v4"></path>
          <path d="M12 17h.01"></path>
        </svg>
        {{ message }}
      </p>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'
import { useErrorStore } from '@/stores/error'

const errorStore = useErrorStore()

const message = computed(() => errorStore.message)

const close = () => {
  errorStore.clearError()
}
</script>

<style scoped>
.error-alert {
  position: fixed;
  top: 100px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;

  width: auto;
  min-width: 200px;
  max-width: min(92vw, 600px);
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: center;
  padding: 12px 56px 12px 16px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.5s ease;
  white-space: nowrap;

  border: 1px solid #f85149;
  color: #b22b2b;
  background: #fee2e2; /* opaque */
}

.error-alert__close {
  position: absolute;
  right: 16px;
  padding: 4px;
  border-radius: 6px;
  transition: opacity 0.2s ease;
  color: #f85149;
  border: 1px solid #f85149;
  background: transparent;
  cursor: pointer;
  opacity: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-alert__close:hover {
  background: rgba(248, 81, 73, 0.14);
}

.error-alert__close svg {
  width: 16px;
  height: 16px;
}

.error-alert__message {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-right: auto;
  gap: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.error-alert__message svg {
  width: 28px;
  height: 28px;
  color: #b22b2b;
  flex-shrink: 0;
}

/* 过渡动画 */
.error-alert-enter-active,
.error-alert-leave-active {
  transition: all 0.5s ease;
}

.error-alert-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.error-alert-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}
</style>
