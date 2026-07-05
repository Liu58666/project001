import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWarningStore = defineStore('warning', () => {
  const message = ref('')
  const timeoutId = ref(null)

  function showWarning(warnMessage, duration = 3500) {
    if (timeoutId.value) {
      clearTimeout(timeoutId.value)
    }

    message.value = warnMessage

    if (duration > 0) {
      timeoutId.value = setTimeout(() => {
        clearWarning()
      }, duration)
    }
  }

  function clearWarning() {
    if (timeoutId.value) {
      clearTimeout(timeoutId.value)
      timeoutId.value = null
    }
    message.value = ''
  }

  return {
    message,
    showWarning,
    clearWarning,
  }
})

