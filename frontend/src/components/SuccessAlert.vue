<template>
  <Transition name="success-alert">
    <div
      v-if="message"
      class="success-alert"
      :class="{ 'success-alert--visible': message }"
    >
      <button
        type="button"
        :aria-label="$t('common.close')"
        class="success-alert__close"
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

      <p class="success-alert__message">
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
          <path d="M20 6 9 17l-5-5"></path>
        </svg>
        {{ message }}
      </p>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'
import { useSuccessStore } from '@/stores/success'

const successStore = useSuccessStore()
const message = computed(() => successStore.message)

const close = () => {
  successStore.clearSuccess()
}
</script>

<style scoped>
.success-alert {
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

  border: 1px solid #22c55e;
  color: #15803d;
  background: #dcfce7; /* opaque */
}

.success-alert__close {
  position: absolute;
  right: 16px;
  padding: 4px;
  border-radius: 6px;
  transition: opacity 0.2s ease;
  color: #22c55e;
  border: 1px solid #22c55e;
  background: transparent;
  cursor: pointer;
  opacity: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-alert__close:hover {
  background: rgba(34, 197, 94, 0.14);
}

.success-alert__close svg {
  width: 16px;
  height: 16px;
}

.success-alert__message {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-right: auto;
  gap: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.success-alert__message svg {
  width: 28px;
  height: 28px;
  color: #15803d;
  flex-shrink: 0;
}

.success-alert-enter-active,
.success-alert-leave-active {
  transition: all 0.5s ease;
}

.success-alert-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.success-alert-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}
</style>


