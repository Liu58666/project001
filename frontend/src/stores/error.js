import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useErrorStore = defineStore('error', () => {
  const message = ref('')
  const timeoutId = ref(null)

  // 显示错误信息
  function showError(errorMessage, duration = 5000) {
    // 清除之前的定时器
    if (timeoutId.value) {
      clearTimeout(timeoutId.value)
    }

    message.value = errorMessage

    // 自动清除错误信息
    if (duration > 0) {
      timeoutId.value = setTimeout(() => {
        clearError()
      }, duration)
    }
  }

  // 清除错误信息
  function clearError() {
    if (timeoutId.value) {
      clearTimeout(timeoutId.value)
      timeoutId.value = null
    }
    message.value = ''
  }

  return {
    message,
    showError,
    clearError
  }
})
