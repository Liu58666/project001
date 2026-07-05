// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useI18nStore } from '@/stores/i18n'

// 全局基础样式（重置、字体、背景）
import './assets/styles/base.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Global $t() for templates (lightweight i18n)
const i18n = useI18nStore(pinia)
app.config.globalProperties.$t = (key, vars) => i18n.t(key, vars)

app.mount('#app')
