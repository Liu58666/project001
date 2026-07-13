<template>
  <section class="coming-soon-page">
    <div class="content-wrapper">
      <div class="icon-wrapper reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '0ms' }">
        <svg viewBox="0 0 24 24" width="80" height="80" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 6v6l4 2"/>
        </svg>
      </div>
      
      <h1 class="title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '100ms' }">
        {{ isZh ? '正在开发中' : 'Coming Soon' }}
      </h1>
      
      <p class="subtitle reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '200ms' }">
        {{ isZh ? '该功能正在紧锣密鼓地开发中，敬请期待！' : 'This feature is under active development. Stay tuned!' }}
      </p>
      
      <button 
        class="back-btn reveal" 
        :class="{ 'is-in': pageEnter }" 
        :style="{ '--d': '300ms' }"
        @click="goBack"
      >
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        {{ isZh ? '返回' : 'Go Back' }}
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'

const router = useRouter()
const i18n = useI18nStore()
const isZh = computed(() => i18n.locale === 'zh')
const pageEnter = ref(false)

function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

onMounted(() => {
  requestAnimationFrame(() => {
    pageEnter.value = true
  })
})
</script>

<style scoped>
.coming-soon-page {
  min-height: 100vh;
  background: #fbfbfb;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.content-wrapper {
  text-align: center;
  max-width: 480px;
}

.icon-wrapper {
  margin-bottom: 32px;
  color: #9ca3af;
}

.icon-wrapper svg {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
}

.title {
  font-size: 48px;
  font-weight: 600;
  color: #0b0f19;
  margin: 0 0 16px;
  letter-spacing: -0.02em;
}

.subtitle {
  font-size: 16px;
  color: rgba(0, 0, 0, 0.55);
  margin: 0 0 40px;
  line-height: 1.6;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: #0b0f19;
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(11, 15, 25, 0.2);
}

.back-btn:active {
  transform: scale(0.98);
}

/* 动画 */
.reveal {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), 
              transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--d, 0ms);
}

.reveal.is-in {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 900px) {
  .coming-soon-page { min-height: 100svh; padding: 104px 20px 56px; }
  .title { font-size: clamp(38px, 11vw, 48px); }
  .back-btn { width: 100%; justify-content: center; min-height: 48px; }
}
</style>
