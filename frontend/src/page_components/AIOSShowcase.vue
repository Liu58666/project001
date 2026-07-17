<template>
  <section
    id="aios-showcase"
    ref="sectionRef"
    class="aios-showcase"
    :class="{ 'aios-showcase--visible': isVisible }"
    :lang="i18n.locale"
    aria-labelledby="aios-showcase-title"
  >
    <div class="aios-inner">
      <div class="aios-copy">
        <p class="aios-eyebrow">{{ t('aiosShowcase.eyebrow') }}</p>
        <h2 id="aios-showcase-title" class="aios-title">
          <span>{{ t('aiosShowcase.titleLine1') }}</span>
          <span>{{ t('aiosShowcase.titleLine2') }}</span>
        </h2>
        <p class="aios-description">
          <span>{{ t('aiosShowcase.descriptionLine1') }}</span>
          <span>{{ t('aiosShowcase.descriptionLine2') }}</span>
        </p>
      </div>

      <div class="aios-visual" aria-hidden="true">
        <div class="aios-floor-light"></div>
        <div class="aios-contact-shadow"></div>
        <img
          :src="aiosImage"
          alt=""
          width="1024"
          height="614"
          loading="lazy"
          decoding="async"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import aiosImage from '@/assets/images/prod/AIOS.png'

const i18n = useI18nStore()
const t = (key) => i18n.t(key)

const sectionRef = ref(null)
const isVisible = ref(false)

let observer = null
let updateFrame = null

const updateTheme = () => {
  updateFrame = null
  const section = sectionRef.value
  if (!section) return

  const bounds = section.getBoundingClientRect()
  const navHeight = document.querySelector('.nav')?.getBoundingClientRect().height
    || (window.innerWidth <= 900 ? 68 : 80)
  document.body.classList.toggle(
    'aios-showcase-active',
    bounds.top <= navHeight && bounds.bottom > navHeight,
  )
}

const requestThemeUpdate = () => {
  if (updateFrame !== null) return
  updateFrame = window.requestAnimationFrame(updateTheme)
}

onMounted(() => {
  const section = sectionRef.value
  if (!section) return

  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting && entry.intersectionRatio >= 0.18) {
        isVisible.value = true
      }
    },
    { threshold: [0, 0.18, 0.5] },
  )
  observer.observe(section)

  updateTheme()
  window.addEventListener('scroll', requestThemeUpdate, { passive: true })
  window.addEventListener('resize', requestThemeUpdate, { passive: true })
})

onBeforeUnmount(() => {
  observer?.disconnect()
  window.removeEventListener('scroll', requestThemeUpdate)
  window.removeEventListener('resize', requestThemeUpdate)
  if (updateFrame !== null) window.cancelAnimationFrame(updateFrame)
  document.body.classList.remove('aios-showcase-active')
})
</script>

<style scoped>
.aios-showcase {
  position: relative;
  z-index: 2;
  min-height: 100vh;
  min-height: 100svh;
  overflow: hidden;
  background: #000000;
  color: #ffffff;
}

.aios-inner {
  display: grid;
  width: min(100%, 1720px);
  min-height: 100vh;
  min-height: 100svh;
  margin: 0 auto;
  padding: clamp(110px, 14vh, 152px) clamp(34px, 5.5vw, 104px) clamp(64px, 8vh, 92px);
  grid-template-columns: minmax(520px, 1.08fr) minmax(360px, 0.92fr);
  align-items: center;
  gap: clamp(28px, 3vw, 58px);
  box-sizing: border-box;
}

.aios-copy {
  position: relative;
  right: clamp(-72px, -3.5vw, -30px);
  z-index: 3;
  order: 2;
  width: min(42vw, 680px);
  justify-self: end;
  opacity: 0;
  transform: translate3d(0, 54px, 0);
  transition:
    opacity 0.8s ease 0.08s,
    transform 1s cubic-bezier(0.16, 1, 0.3, 1) 0.08s;
}

.aios-showcase--visible .aios-copy {
  opacity: 1;
  transform: translate3d(0, 0, 0);
}

.aios-eyebrow {
  margin: 0 0 clamp(24px, 3.5vh, 38px);
  color: rgba(226, 233, 243, 0.62);
  font-family: 'IBM Plex Mono', 'JetBrains Mono', ui-monospace, monospace;
  font-size: clamp(10px, 0.72vw, 12px);
  font-weight: 500;
  letter-spacing: 0.18em;
  line-height: 1.5;
  text-transform: uppercase;
}

.aios-title {
  margin: 0;
  font-size: clamp(48px, 4.7vw, 82px);
  font-weight: 430;
  letter-spacing: -0.06em;
  line-height: 1.02;
  text-wrap: balance;
}

.aios-title span,
.aios-description span {
  display: block;
}

.aios-description {
  max-width: 35rem;
  margin: clamp(28px, 4.5vh, 46px) 0 0;
  color: rgba(225, 234, 246, 0.7);
  font-size: clamp(15px, 1.12vw, 19px);
  line-height: 1.72;
}

.aios-visual {
  position: relative;
  left: clamp(-90px, -3vw, -40px);
  z-index: 2;
  order: 1;
  width: min(54vw, 980px);
  justify-self: start;
  opacity: 0;
  transform: translate3d(-70px, 38px, 0) scale(0.94);
  transform-origin: center;
  isolation: isolate;
  transition:
    opacity 0.9s ease 0.16s,
    transform 1.15s cubic-bezier(0.16, 1, 0.3, 1) 0.12s;
  will-change: transform, opacity;
}

.aios-showcase--visible .aios-visual {
  opacity: 1;
  transform: translate3d(0, 0, 0) scale(1);
}

.aios-visual::after {
  content: '';
  position: absolute;
  z-index: 0;
  top: 5%;
  right: 8%;
  bottom: 12%;
  left: 8%;
  background: radial-gradient(
    ellipse at 48% 68%,
    rgba(221, 235, 255, 0.17) 0%,
    rgba(93, 132, 188, 0.1) 34%,
    transparent 72%
  );
  filter: blur(42px);
  pointer-events: none;
}

.aios-floor-light {
  position: absolute;
  z-index: 1;
  left: 50%;
  bottom: -8%;
  width: 126%;
  height: 34%;
  border-radius: 50%;
  background: radial-gradient(
    ellipse at center,
    rgba(240, 247, 255, 0.62) 0%,
    rgba(187, 207, 235, 0.34) 24%,
    rgba(95, 128, 172, 0.17) 48%,
    rgba(27, 47, 75, 0.08) 64%,
    transparent 78%
  );
  filter: blur(18px);
  opacity: 0;
  transform: translateX(-50%) scaleX(0.78) scaleY(0.28);
  transform-origin: center;
  transition:
    opacity 1s ease 0.28s,
    transform 1.15s cubic-bezier(0.16, 1, 0.3, 1) 0.2s;
  pointer-events: none;
}

.aios-contact-shadow {
  position: absolute;
  z-index: 2;
  left: 50%;
  bottom: 1.5%;
  width: 48%;
  height: 9%;
  border-radius: 50%;
  background: radial-gradient(
    ellipse at center,
    rgba(0, 0, 0, 0.84) 0%,
    rgba(0, 0, 0, 0.52) 38%,
    rgba(0, 0, 0, 0.16) 66%,
    transparent 82%
  );
  filter: blur(10px);
  opacity: 0;
  transform: translateX(-50%) scaleX(0.72);
  transition:
    opacity 0.85s ease 0.34s,
    transform 1s cubic-bezier(0.16, 1, 0.3, 1) 0.26s;
  pointer-events: none;
}

.aios-showcase--visible .aios-floor-light {
  opacity: 0.72;
  transform: translateX(-50%) scaleX(1) scaleY(0.36);
}

.aios-showcase--visible .aios-contact-shadow {
  opacity: 0.82;
  transform: translateX(-50%) scaleX(1);
}

.aios-visual img {
  position: relative;
  z-index: 3;
  display: block;
  width: 100%;
  height: auto;
  filter: saturate(1.02) contrast(1.015);
  user-select: none;
}

@media (min-width: 901px) {
  .aios-showcase:lang(zh) .aios-title {
    font-size: clamp(44px, 4vw, 68px);
  }

  .aios-showcase:lang(zh) .aios-title span {
    white-space: nowrap;
  }
}

@media (max-width: 900px) {
  .aios-inner {
    min-height: 100svh;
    padding: 102px 20px 54px;
    grid-template-columns: minmax(0, 1fr);
    align-content: center;
    gap: 42px;
  }

  .aios-copy {
    right: auto;
    order: 1;
    width: min(100%, 620px);
    justify-self: start;
  }

  .aios-eyebrow {
    margin-bottom: 18px;
    font-size: 9px;
  }

  .aios-title {
    font-size: clamp(38px, 10.4vw, 54px);
    line-height: 1.04;
  }

  .aios-description {
    margin-top: 22px;
    font-size: clamp(13px, 3.7vw, 16px);
    line-height: 1.6;
  }

  .aios-visual {
    left: 0;
    order: 2;
    width: 118vw;
    max-width: none;
    margin-right: -24vw;
    justify-self: end;
    transform: translate3d(48px, 34px, 0) scale(0.96);
  }
}

@media (prefers-reduced-motion: reduce) {
  .aios-copy,
  .aios-visual,
  .aios-showcase--visible .aios-copy,
  .aios-showcase--visible .aios-visual {
    opacity: 1;
    transform: none;
    transition: none;
  }

  .aios-floor-light,
  .aios-contact-shadow,
  .aios-showcase--visible .aios-floor-light,
  .aios-showcase--visible .aios-contact-shadow {
    opacity: 0.7;
    transition: none;
  }

  .aios-floor-light,
  .aios-showcase--visible .aios-floor-light {
    transform: translateX(-50%) scaleX(1) scaleY(0.36);
  }

  .aios-contact-shadow,
  .aios-showcase--visible .aios-contact-shadow {
    transform: translateX(-50%) scaleX(1);
  }
}
</style>

<style>
body.aios-showcase-active .nav,
body.aios-showcase-active .nav.scrolled {
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
}

body.aios-showcase-active .nav .logo {
  filter: invert(1) grayscale(1) brightness(1.8);
}

body.aios-showcase-active .nav .menu-link,
body.aios-showcase-active .nav .mobile-language-toggle {
  color: rgba(255, 255, 255, 0.82);
}

body.aios-showcase-active .nav .btn-12 {
  background-color: #ffffff;
  color: #050505;
}

body.aios-showcase-active .nav .login-icon {
  border-color: rgba(255, 255, 255, 0.88);
}

body.aios-showcase-active .nav .login-icon:not(.login-icon--has-photo) img {
  filter: invert(1);
}

body.aios-showcase-active .nav .user-avatar {
  color: #ffffff;
}

body.aios-showcase-active .nav .menu-toggle span {
  background: #ffffff;
}

@media (max-width: 900px) {
  body.aios-showcase-active .nav:has(.menu--open),
  body.aios-showcase-active .nav.scrolled:has(.menu--open) {
    background: rgba(255, 255, 255, 0.98);
  }

  body.aios-showcase-active .nav:has(.menu--open) .logo {
    filter: none;
  }

  body.aios-showcase-active .nav:has(.menu--open) .mobile-language-toggle {
    color: rgba(17, 24, 39, 0.68);
  }

  body.aios-showcase-active .nav:has(.menu--open) .login-icon {
    border-color: #111827;
  }

  body.aios-showcase-active .nav:has(.menu--open) .menu-toggle span {
    background: #111827;
  }
}
</style>
