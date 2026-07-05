<template>
  <Transition name="warning-alert">
    <div
      v-if="message"
      class="warning-alert"
      :class="{ 'warning-alert--visible': message }"
    >
      <button
        type="button"
        :aria-label="$t('common.close')"
        class="warning-alert__close"
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

      <p class="warning-alert__message">
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
          <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"></path>
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
import { useWarningStore } from '@/stores/warning'

const warningStore = useWarningStore()
const message = computed(() => warningStore.message)

const close = () => {
  warningStore.clearWarning()
}
</script>

<style scoped>
.warning-alert {
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

  border: 1px solid #f59e0b;
  color: #92400e;
  background: #fef3c7; /* opaque */
}

.warning-alert__close {
  position: absolute;
  right: 16px;
  padding: 4px;
  border-radius: 6px;
  transition: background-color 0.2s ease;
  color: #b45309;
  border: 1px solid #f59e0b;
  background: transparent;
  cursor: pointer;
  opacity: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.warning-alert__close:hover {
  background: rgba(245, 158, 11, 0.16);
}

.warning-alert__message {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-right: auto;
  gap: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.warning-alert__message svg {
  width: 28px;
  height: 28px;
  color: #92400e;
  flex-shrink: 0;
}

.warning-alert-enter-active,
.warning-alert-leave-active {
  transition: all 0.5s ease;
}

.warning-alert-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.warning-alert-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}
</style>

