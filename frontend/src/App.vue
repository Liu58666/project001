<!-- src/App.vue -->
<template>
  <div class="app-root">
    <!-- 加载页面 -->
    <LoaderOverlay :show="showLoader" />

    <!-- 全局错误提示 -->
    <ErrorAlert />
    <!-- 全局警示提示（黄色） -->
    <WarningAlert />
    <!-- 全局成功提示（绿色） -->
    <SuccessAlert />

    <!-- 顶部极简导航 -->
    <NavBar @navigate-home="handleNavigateHome" />

    <!-- 主体内容 -->
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, provide } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NavBar from './components/NavBar.vue'
import LoaderOverlay from './components/LoaderOverlay.vue'
import ErrorAlert from './components/ErrorAlert.vue'
import WarningAlert from './components/WarningAlert.vue'
import SuccessAlert from './components/SuccessAlert.vue'

const router = useRouter()
const userStore = useUserStore()
const showLoader = ref(true)
const loaderFinished = ref(false)

// 初始化用户状态（从存储中恢复）
userStore.init()

// 提供给子组件，通知过场动画已结束
provide('loaderFinished', loaderFinished)

// 提供给子组件：显示 LoaderOverlay 一段时间后执行回调
// 用法：showLoaderFor(1000, () => { ... })
const showLoaderFor = (ms = 1000, cb) => {
  showLoader.value = true
  loaderFinished.value = false
  setTimeout(() => {
    try {
      cb?.()
    } finally {
      showLoader.value = false
      // 通知过场动画已结束，可以开始页面动画
      setTimeout(() => {
        loaderFinished.value = true
      }, 50)
    }
  }, Number(ms) || 0)
}
provide('showLoaderFor', showLoaderFor)

const handleNavigateHome = () => {
  // 显示过场动画
  showLoader.value = true
  loaderFinished.value = false
  // 1秒后跳转到首页并隐藏动画
  setTimeout(() => {
    router.push('/')
    showLoader.value = false
    // 通知过场动画已结束，可以开始页面动画
    setTimeout(() => {
      loaderFinished.value = true
    }, 50)
  }, 1000)
}

onMounted(() => {
  // 2秒后隐藏加载页面，并通知可以开始页面动画
  setTimeout(() => {
    showLoader.value = false
    loaderFinished.value = true
  }, 2000)
})
</script>

<style scoped>
.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Main 组件自己处理 padding，这里不需要额外 padding */
.app-main {
  flex: 1;
}

</style>
