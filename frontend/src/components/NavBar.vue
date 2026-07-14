<!-- src/components/NavBar.vue -->
<template>
  <header :class="['nav', { scrolled: isScrolled }]">
    <!-- 左侧 Logo：放大一点 -->
    <div class="logo-wrapper">
      <img 
        src="/src/assets/images/logo.png" 
        :alt="t('nav.logoAlt')" 
        class="logo" 
        @click="handleLogoClick"
      />
    </div>

    <!-- 中间导航菜单（整体居中） -->
    <nav
      id="primary-navigation"
      :class="['menu', { 'menu--open': isMobileMenuOpen }]"
      :aria-label="t('nav.primaryNavigation')"
    >
      <!-- SOLUTIONS 下拉 -->
      <div class="menu-item menu-item--dropdown">
        <button
          class="menu-link"
          type="button"
          :aria-expanded="activeMobileDropdown === 'solutions'"
          @click="toggleMobileDropdown('solutions')"
        >
          {{ t('nav.solutions') }} <span class="plus">+</span>
        </button>
        <div :class="['dropdown', 'dropdown--solutions', { 'dropdown--open': activeMobileDropdown === 'solutions' }]">
          <a href="/coming-soon" class="dropdown-item" @click.prevent="navigateTo('/coming-soon')">{{ t('nav.solutionsByIndustry') }}</a>
          <a href="/coming-soon" class="dropdown-item" @click.prevent="navigateTo('/coming-soon')">{{ t('nav.solutionsByScenario') }}</a>
          <a href="/coming-soon" class="dropdown-item" @click.prevent="navigateTo('/coming-soon')">{{ t('nav.solutionsCustom') }}</a>
        </div>
      </div>

      <!-- TECHNOLOGY 下拉 -->
      <div class="menu-item menu-item--dropdown">
        <button
          class="menu-link"
          type="button"
          :aria-expanded="activeMobileDropdown === 'technology'"
          @click="toggleMobileDropdown('technology')"
        >
          {{ t('nav.technology') }} <span class="plus">+</span>
        </button>
        <div :class="['dropdown', 'dropdown--technology', { 'dropdown--open': activeMobileDropdown === 'technology' }]">
          <a href="/technology?topic=platform-build" class="dropdown-item" @click.prevent="navigateTo('/technology?topic=platform-build')">{{ t('nav.technologyPlatform') }}</a>
          <a href="/technology?topic=agent-development" class="dropdown-item" @click.prevent="navigateTo('/technology?topic=agent-development')">{{ t('nav.technologyAgents') }}</a>
          <a href="/technology?topic=data-governance" class="dropdown-item" @click.prevent="navigateTo('/technology?topic=data-governance')">{{ t('nav.technologyRag') }}</a>
        </div>
      </div>

      <!-- LANGUAGES：hover 弹出可选项 -->
      <div class="menu-item menu-item--dropdown menu-item--lang">
        <button
          class="menu-link"
          type="button"
          :aria-expanded="activeMobileDropdown === 'languages'"
          @click="toggleMobileDropdown('languages')"
        >
          {{ t('nav.languages') }} <span class="plus">+</span>
        </button>
        <div :class="['dropdown', 'dropdown--lang', { 'dropdown--open': activeMobileDropdown === 'languages' }]" role="menu" aria-label="Languages">
          <button
            class="dropdown-item dropdown-item--btn"
            type="button"
            role="menuitem"
            :aria-current="i18n.locale === 'zh' ? 'true' : 'false'"
            @click="selectLocale('zh')"
          >
            {{ t('nav.languageChinese') }}
          </button>
          <button
            class="dropdown-item dropdown-item--btn"
            type="button"
            role="menuitem"
            :aria-current="i18n.locale === 'en' ? 'true' : 'false'"
            @click="selectLocale('en')"
          >
            {{ t('nav.languageEnglish') }}
          </button>
        </div>
      </div>

      <!-- COMPANY 下拉 -->
      <div class="menu-item menu-item--dropdown">
        <button
          class="menu-link"
          type="button"
          :aria-expanded="activeMobileDropdown === 'company'"
          @click="toggleMobileDropdown('company')"
        >
          {{ t('nav.company') }} <span class="plus">+</span>
        </button>
        <div :class="['dropdown', 'dropdown--company', { 'dropdown--open': activeMobileDropdown === 'company' }]">
          <a href="/about" class="dropdown-item" @click.prevent="navigateTo('/about')">{{ t('nav.companyAbout') }}</a>
          <a href="/team" class="dropdown-item" @click.prevent="navigateTo('/team')">{{ t('nav.companyTeam') }}</a>
          <a href="/career" class="dropdown-item" @click.prevent="navigateTo('/career')">{{ t('nav.companyCareers') }}</a>
          <a href="/news" class="dropdown-item" @click.prevent="navigateTo('/news')">{{ t('nav.companyNews') }}</a>
        </div>
      </div>

      <!-- DOCS 普通项 -->
      <div class="menu-item">
        <button class="menu-link" type="button" @click="navigateTo('/coming-soon')">{{ t('nav.docs') }}</button>
      </div>

      <button class="mobile-contact" type="button" @click="navigateTo('/career/join')">
        {{ t('nav.contactUs') }}
      </button>
    </nav>

    <!-- 右侧：Contact Us + Search + Login -->
    <div class="nav-actions">
      <!-- Contact Us 按钮 -->
      <button class="btn-12" @click="navigateTo('/career/join')">
        <span>{{ t('nav.contactUs') }}</span>
      </button>

      <!-- Search 输入框 -->
      <div class="wave-group">
        <input required type="text" class="input" />
        <span class="bar"></span>
        <label class="label">
          <span
            v-for="(ch, idx) in searchLabelChars"
            :key="`${idx}-${ch}`"
            class="label-char"
            :style="{ '--index': idx }"
          >
            {{ ch }}
          </span>
        </label>
      </div>

      <!-- 手机端语言快捷切换：显示目标语言，点击后直接切换 -->
      <button
        class="mobile-language-toggle"
        type="button"
        :aria-label="i18n.locale === 'zh' ? t('nav.languageEnglish') : t('nav.languageChinese')"
        :title="i18n.locale === 'zh' ? t('nav.languageEnglish') : t('nav.languageChinese')"
        @click="selectLocale(i18n.locale === 'zh' ? 'en' : 'zh')"
      >
        {{ i18n.locale === 'zh' ? 'EN' : '中' }}
      </button>

      <!-- Login/User 图标 -->
      <button
        class="login-icon"
        :class="{ 'login-icon--has-photo': isLoggedIn && userPhoto }"
        :aria-label="isLoggedIn ? t('nav.userProfile') : t('nav.login')"
        type="button"
        @click="handleUserClick"
      >
        <img v-if="!isLoggedIn" src="/src/assets/images/login.png" :alt="t('nav.login')" />
        <template v-else>
          <img v-if="userPhoto" :src="userPhoto" alt="avatar" class="user-avatar-img" />
          <div v-else class="user-avatar">
            {{ userInitial }}
          </div>
        </template>
      </button>

      <button
        class="menu-toggle"
        type="button"
        :aria-expanded="isMobileMenuOpen"
        aria-controls="primary-navigation"
        :aria-label="isMobileMenuOpen ? t('nav.closeMenu') : t('nav.openMenu')"
        @click="toggleMobileMenu"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>

    <button
      v-if="isMobileMenuOpen"
      class="menu-backdrop"
      type="button"
      :aria-label="t('nav.closeMenu')"
      @click="closeMobileMenu"
    ></button>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, inject, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useI18nStore } from '@/stores/i18n'

const router = useRouter()
const userStore = useUserStore()
const i18n = useI18nStore()
const emit = defineEmits(['navigate-home'])
const showLoaderFor = inject('showLoaderFor', null)

const isScrolled = ref(false)
const isMobileMenuOpen = ref(false)
const activeMobileDropdown = ref(null)

const t = (key, vars) => i18n.t(key, vars)

const searchLabelChars = computed(() => String(t('nav.search') || '').split(''))

// 检查登录状态
const isLoggedIn = computed(() => userStore.isLoggedIn)

// 用户头像首字母
const userInitial = computed(() => {
  const name = userStore.displayName || userStore.username || 'U'
  return name.charAt(0).toUpperCase()
})

// 用户头像 URL
const userPhoto = computed(() => userStore.photo || '')

const handleUserClick = () => {
  closeMobileMenu()
  if (isLoggedIn.value) {
    // 已登录，跳转到用户页面
    router.push('/user')
  } else {
    // 未登录，跳转到登录页面
    router.push('/login')
  }
}

const handleScroll = () => {
  isScrolled.value = window.scrollY > 10
}

const handleLogoClick = () => {
  closeMobileMenu()
  emit('navigate-home')
}

const navigateTo = (path) => {
  closeMobileMenu()
  router.push(path)
}

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
  if (!isMobileMenuOpen.value) activeMobileDropdown.value = null
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
  activeMobileDropdown.value = null
}

const toggleMobileDropdown = (name) => {
  if (window.innerWidth > 900) return
  activeMobileDropdown.value = activeMobileDropdown.value === name ? null : name
}

const handleResize = () => {
  if (window.innerWidth > 900) closeMobileMenu()
}

const handleKeydown = (event) => {
  if (event.key === 'Escape') closeMobileMenu()
}

const selectLocale = (nextLocale) => {
  closeMobileMenu()
  const run = () => i18n.setLocale(nextLocale)
  if (typeof showLoaderFor === 'function') {
    showLoaderFor(1000, run)
    return
  }
  // fallback (shouldn't happen if App.vue provides it)
  setTimeout(run, 1000)
}

onMounted(() => {
  handleScroll()
  window.addEventListener('scroll', handleScroll, { passive: true })
  window.addEventListener('resize', handleResize, { passive: true })
  window.addEventListener('keydown', handleKeydown)
})

watch(isMobileMenuOpen, (isOpen) => {
  document.body.style.overflow = isOpen ? 'hidden' : ''
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* 整体布局：三列，左 logo / 中导航 / 右按钮+搜索  */
/* 整体布局：三列，左 logo / 中导航 / 右按钮+搜索  */
.nav {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 80px;
  padding: 0 30px;
  background: transparent;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  box-sizing: border-box;
  z-index: 1000; /* keep dropdown above all pages */
  transition: background 0.25s ease, box-shadow 0.25s ease;
}

.nav.scrolled {
  background: #ffffff;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}

/* 左侧 logo */
.logo-wrapper {
  display: flex;
  align-items: center;
  margin-left: 30px; /* 调整这个值可以让 logo 右移，数值越大右移越多 */
}

/* 这里的 height 就是你真正控制 logo 大小的地方 */
.logo {
  display: block;
  height: 84px;
  width: auto;
  object-fit: contain;
  transform: translateY(2px);
  cursor: pointer;
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: translateY(2px) scale(1.1);
}

/* 文字占位版本 */
.logo-placeholder {
  font-weight: 700;
  font-size: 20px;
  letter-spacing: 0.16em;
}

/* 中间菜单：真正居中 */
.menu {
  justify-self: center;
  display: flex;
  align-items: center;
  gap: 36px;
}

/* 每一项容器（用于承载下拉） */
.menu-item {
  position: relative;
}

/* 在下拉菜单和按钮之间添加一个不可见的桥接区域，防止鼠标移动时菜单消失 */
.menu-item--dropdown::before {
  content: '';
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  height: 20px; /* 桥接区域高度，确保鼠标移动路径连续 */
  z-index: 1001;
  pointer-events: auto;
}

/* 导航文字按钮 */
.menu-link {
  background: none;
  border: none;
  cursor: pointer;

  font-family: 'IBM Plex Mono', 'JetBrains Mono', ui-monospace, SFMono-Regular,
    Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 16px; /* 调大中间导航字体 */
  letter-spacing: 0.16em;

  color: #1f2933;
  padding: 4px 2px;
  transition: color 0.2s ease, transform 0.2s ease;
}

.menu-link:hover {
  color: #000;
  transform: translateY(-1px);
}

.plus {
  margin-left: 4px;
  opacity: 0.6;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

/* 极简下拉菜单 */
.dropdown {
  position: absolute;
  top: calc(100% + 20px); /* 紧接桥接区域下方 */
  left: 50%;
  transform: translate(-50%, 0);
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  min-width: 200px;
  max-width: 260px; /* 默认最大宽度，防止被长文本撑宽 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);

  display: flex;
  flex-direction: column;
  gap: 8px;

  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease, visibility 0.2s;
  z-index: 1002;
}

/* 不同分组单独控制最大宽度 */
.dropdown--solutions {
  min-width: 220px;
}

.dropdown--technology {
  max-width: 300px;
}

.dropdown--company {
  max-width: 280px;
}

.dropdown--lang {
  min-width: 180px;
  max-width: 220px;
}

.dropdown-item--btn {
  width: 100%;
  text-align: left;
  background: transparent;
  border: none;
  cursor: pointer;
  font-family: inherit;
}

.dropdown-item--btn[aria-current='true'] {
  font-weight: 700;
  color: #9333ea;
}

.dropdown-item {
  font-size: 15px;
  letter-spacing: 0.08em;
  color: #000000;
  text-decoration: none;
  padding: 8px 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-radius: 4px;
  transition: all 0.2s ease;
  position: relative;
  max-width: 100%;
}

.dropdown-item:hover {
  color: #9333ea;
  text-decoration: underline;
  text-decoration-color: #9333ea;
  text-decoration-thickness: 2px;
  text-underline-offset: 4px;
  background: rgba(147, 51, 234, 0.05);
  font-weight: 600;
  transform: translateX(2px);
}

/* hover 触发 */
.menu-item--dropdown:hover .dropdown {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  transform: translate(-50%, 0);
}

.menu-item--dropdown:focus-within .dropdown {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  transform: translate(-50%, 0);
}

/* 确保桥接区域在 hover 时也保持可见 */
.menu-item--dropdown:hover::before {
  pointer-events: auto;
}

.menu-item--dropdown:hover .plus {
  opacity: 1;
  transform: rotate(90deg);
}

/* 右侧 Contact + Search */
.nav-actions {
  justify-self: end;
  display: flex;
  align-items: center;
  gap: 24px;
}

.menu-toggle,
.mobile-language-toggle,
.mobile-contact,
.menu-backdrop {
  display: none;
}

.login-icon {
  width: 38px;
  height: 38px;
  border: 1.9px solid #000;
  border-radius: 50%;
  background: transparent;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
}

.login-icon--has-photo {
  padding: 0;
  overflow: hidden;
  border: none;
}

.login-icon:hover {
  background: #000;
  border-color: #000;
  transform: scale(1.12);
}

.login-icon img {
  width: 28px;
  height: 28px;
  object-fit: contain;
  filter: invert(0);
  transition: filter 0.2s ease;
}

.login-icon--has-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.login-icon:hover img {
  filter: invert(1);
}

.login-icon--has-photo:hover img {
  filter: none;
}

.user-avatar {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: #000;
  transition: color 0.2s ease;
}

.login-icon:hover .user-avatar {
  color: #fff;
}

/* ============ Contact Us 按钮样式（btn-12） ============ */
.btn-12,
.btn-12 *,
.btn-12 :after,
.btn-12 :before,
.btn-12:after,
.btn-12:before {
  border: 0 solid;
  box-sizing: border-box;
}

.btn-12 {
  -webkit-tap-highlight-color: transparent;
  -webkit-appearance: button;
  appearance: button;
  background-color: #000;
  background-image: none;
  color: #fff;
  cursor: pointer;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif,
    'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
    'Noto Color Emoji';
  font-size: 11px;
  font-weight: 800;
  line-height: 1.45;
  margin: 0;
  padding: 0;
  text-transform: uppercase;

  border-radius: 99rem;
  border: none; /* 移除默认白色边框 */
  outline: none;
  overflow: hidden;
  padding: 0.6rem 1.4rem;
  position: relative;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.btn-12 span {
  position: relative;
  z-index: 1;
  mix-blend-mode: normal;
}

.btn-12:before,
.btn-12:after {
  content: none;
  display: none;
}

.btn-12:hover {
  border: 0;
  background-color: #ffffff;
  color: #000000;
  box-shadow: none;
}

/* ============ Search 输入框（改成 Search） ============ */
.wave-group {
  position: relative;
}

.wave-group .input {
  font-size: 14px;
  padding: 8px 10px 8px 5px;
  display: block;
  width: 200px;
  border: none;
  border-bottom: 1px solid #515151;
  background: transparent;
}

.wave-group .input:focus {
  outline: none;
}

.wave-group .label {
  color: #999;
  font-size: 16px;
  font-weight: normal;
  position: absolute;
  pointer-events: none;
  left: 5px;
  top: 10px;
  display: flex;
}

.wave-group .label-char {
  transition: 0.2s ease all;
  transition-delay: calc(var(--index) * 0.05s);
}

.wave-group .input:focus ~ label .label-char,
.wave-group .input:valid ~ label .label-char {
  transform: translateY(-20px);
  font-size: 12px;
  color: #000000;
}

.wave-group .bar {
  position: relative;
  display: block;
  width: 200px;
}

.wave-group .bar:before,
.wave-group .bar:after {
  content: '';
  height: 2px;
  width: 0;
  bottom: 1px;
  position: absolute;
  background: #000000;
  transition: 0.2s ease all;
}

.wave-group .bar:before {
  left: 50%;
}

.wave-group .bar:after {
  right: 50%;
}

.wave-group .input:focus ~ .bar:before,
.wave-group .input:focus ~ .bar:after {
  width: 50%;
}

@media (max-width: 900px) {
  .nav {
    height: 68px;
    padding: 0 16px;
    grid-template-columns: 1fr auto;
    background: rgba(255, 255, 255, 0.96);
    box-shadow: 0 1px 0 rgba(15, 23, 42, 0.08);
    backdrop-filter: blur(14px);
  }

  .logo-wrapper {
    margin-left: 0;
  }

  .logo {
    height: 62px;
  }

  .logo:hover {
    transform: translateY(2px);
  }

  .menu {
    position: fixed;
    top: 68px;
    left: 0;
    right: 0;
    width: 100%;
    z-index: 1002;
    display: flex;
    max-height: calc(100dvh - 68px);
    padding: 12px 20px 28px;
    flex-direction: column;
    align-items: stretch;
    justify-self: stretch;
    gap: 0;
    overflow-y: auto;
    background: #ffffff;
    border-top: 1px solid #e5e7eb;
    box-shadow: 0 20px 40px rgba(15, 23, 42, 0.14);
    opacity: 0;
    visibility: hidden;
    transform: translateY(-12px);
    transition: opacity 0.2s ease, transform 0.2s ease, visibility 0.2s;
  }

  .menu--open {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
  }

  .menu-item {
    width: 100%;
    border-bottom: 1px solid #e5e7eb;
  }

  .menu-item--lang {
    display: none;
  }

  .menu-item--dropdown::before {
    display: none;
  }

  .menu-link {
    display: flex;
    width: 100%;
    min-height: 52px;
    padding: 14px 4px;
    align-items: center;
    justify-content: space-between;
    font-size: 15px;
    text-align: left;
  }

  .menu-link:hover {
    transform: none;
  }

  .menu-link[aria-expanded='true'] .plus {
    opacity: 1;
    transform: rotate(45deg);
  }

  .dropdown {
    position: static;
    min-width: 0;
    max-width: none;
    max-height: 0;
    padding: 0 8px;
    gap: 2px;
    overflow: hidden;
    border: 0;
    border-radius: 0;
    box-shadow: none;
    opacity: 1;
    visibility: hidden;
    pointer-events: none;
    transform: none;
    transition: max-height 0.25s ease, padding 0.25s ease;
  }

  .dropdown--open {
    max-height: 360px;
    padding: 0 8px 12px;
    visibility: visible;
    pointer-events: auto;
  }

  .menu-item--dropdown:hover .dropdown {
    transform: none;
  }

  .menu-item--dropdown:focus-within .dropdown:not(.dropdown--open) {
    max-height: 0;
    padding: 0 8px;
    visibility: hidden;
    pointer-events: none;
  }

  .dropdown-item {
    min-height: 44px;
    padding: 11px 12px;
    white-space: normal;
  }

  .mobile-contact {
    display: block;
    width: 100%;
    min-height: 48px;
    margin-top: 20px;
    border: 0;
    border-radius: 999px;
    background: #111827;
    color: #ffffff;
    font-weight: 700;
    cursor: pointer;
  }

  .nav-actions {
    gap: 10px;
  }

  .nav-actions .btn-12,
  .wave-group {
    display: none;
  }

  .login-icon {
    width: 42px;
    height: 42px;
  }

  .mobile-language-toggle {
    display: inline-flex;
    width: 42px;
    height: 42px;
    flex: 0 0 42px;
    align-items: center;
    justify-content: center;
    border: 0;
    border-radius: 0;
    background: transparent;
    color: rgba(17, 24, 39, 0.68);
    font-family: inherit;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.04em;
    cursor: pointer;
  }

  .mobile-language-toggle:active {
    transform: scale(0.94);
  }

  .menu-toggle {
    display: flex;
    width: 44px;
    height: 44px;
    padding: 10px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 5px;
    border: 0;
    border-radius: 8px;
    background: transparent;
    cursor: pointer;
  }

  .menu-toggle span {
    display: block;
    width: 22px;
    height: 2px;
    border-radius: 999px;
    background: #111827;
    transition: transform 0.2s ease, opacity 0.2s ease;
  }

  .menu-toggle[aria-expanded='true'] span:first-child {
    transform: translateY(7px) rotate(45deg);
  }

  .menu-toggle[aria-expanded='true'] span:nth-child(2) {
    opacity: 0;
  }

  .menu-toggle[aria-expanded='true'] span:last-child {
    transform: translateY(-7px) rotate(-45deg);
  }

  .menu-backdrop {
    position: fixed;
    inset: 68px 0 0;
    z-index: 1001;
    display: block;
    width: 100%;
    border: 0;
    background: rgba(15, 23, 42, 0.38);
  }
}

@media (prefers-reduced-motion: reduce) {
  .menu,
  .dropdown,
  .menu-toggle span {
    transition: none;
  }
}
</style>
