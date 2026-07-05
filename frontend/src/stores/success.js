import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSuccessStore = defineStore('success', () => {
  const message = ref('')
  const timeoutId = ref(null)

  function showSuccess(successMessage, duration = 2500) {
    if (timeoutId.value) {
      clearTimeout(timeoutId.value)
    }

    message.value = successMessage

    if (duration > 0) {
      timeoutId.value = setTimeout(() => {
        clearSuccess()
      }, duration)
    }
  }

  function clearSuccess() {
    if (timeoutId.value) {
      clearTimeout(timeoutId.value)
      timeoutId.value = null
    }
    message.value = ''
  }

  return {
    message,
    showSuccess,
    clearSuccess,
  }
})


