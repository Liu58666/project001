<template>
  <section
    ref="sectionRef"
    :class="['nemo-one-showcase', { 'nemo-one-showcase--visible': isVisible }]"
    aria-labelledby="nemo-one-title"
  >
    <div
      class="nemo-stage"
      @pointermove="handlePointerMove"
      @pointerleave="resetPointer"
    >
      <div class="nemo-ambient" aria-hidden="true"></div>

      <div class="nemo-copy">
        <p class="nemo-eyebrow">{{ t('nemoOne.eyebrow') }}</p>
        <h2 id="nemo-one-title" class="nemo-title">
          <span>{{ t('nemoOne.titleLine1') }}</span>
          <span>{{ t('nemoOne.titleLine2') }}</span>
        </h2>
        <p class="nemo-description">{{ t('nemoOne.description') }}</p>
      </div>

      <div
        class="nemo-product-shell"
        role="img"
        :aria-label="t('nemoOne.ariaLabel')"
      >
        <div class="nemo-product-motion" aria-hidden="true">
          <div class="nemo-product-frame">
            <img
              :src="nemoFront"
              alt=""
              width="1600"
              height="900"
              loading="eager"
              decoding="async"
              fetchpriority="high"
            />
          </div>
          <div class="nemo-sheen"></div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import nemoFront from '@/assets/images/prod/nemo-cooling.png'

const i18n = useI18nStore()
const t = (key) => i18n.t(key)

const sectionRef = ref(null)
const isVisible = ref(false)

let observer = null
let parallaxFrame = null

const clamp = (value, min = -1, max = 1) => Math.min(max, Math.max(min, value))

const updateParallax = () => {
  parallaxFrame = null

  const section = sectionRef.value
  if (!section) return

  const bounds = section.getBoundingClientRect()
  const viewportHeight = window.innerHeight || 1
  const themeSwitchLine = document.querySelector('.nav')?.getBoundingClientRect().height
    || (window.innerWidth <= 900 ? 68 : 80)
  document.body.classList.toggle(
    'nemo-showcase-active',
    bounds.top <= themeSwitchLine && bounds.bottom > themeSwitchLine,
  )

  const supportsParallax = window.matchMedia(
    '(min-width: 901px) and (prefers-reduced-motion: no-preference)',
  ).matches

  if (!supportsParallax) {
    section.style.setProperty('--copy-parallax-y', '0px')
    section.style.setProperty('--product-parallax-y', '0px')
    return
  }

  const scrollDistance = Math.max(1, section.offsetHeight - viewportHeight)
  const progress = clamp(-bounds.top / scrollDistance, 0, 1)
  const easedProgress = progress * progress * (3 - 2 * progress)
  const direction = easedProgress * 2 - 1

  section.style.setProperty('--copy-parallax-y', `${(-direction * 52).toFixed(2)}px`)
  section.style.setProperty('--product-parallax-y', `${(direction * 38).toFixed(2)}px`)
}

const requestParallaxUpdate = () => {
  if (parallaxFrame !== null) return
  parallaxFrame = window.requestAnimationFrame(updateParallax)
}

const handlePointerMove = (event) => {
  if (!window.matchMedia('(pointer: fine) and (min-width: 901px)').matches) return

  const section = sectionRef.value
  if (!section) return

  const bounds = section.getBoundingClientRect()
  const pointerX = clamp(((event.clientX - bounds.left) / bounds.width - 0.5) * 2)
  const pointerY = clamp(((event.clientY - bounds.top) / bounds.height - 0.5) * 2)

  section.style.setProperty('--pointer-x', `${(pointerX * 7).toFixed(2)}px`)
  section.style.setProperty('--pointer-y', `${(pointerY * 4).toFixed(2)}px`)
}

const resetPointer = () => {
  sectionRef.value?.style.setProperty('--pointer-x', '0px')
  sectionRef.value?.style.setProperty('--pointer-y', '0px')
}

onMounted(() => {
  const section = sectionRef.value
  if (!section) return

  updateParallax()
  window.addEventListener('scroll', requestParallaxUpdate, { passive: true })
  window.addEventListener('resize', requestParallaxUpdate, { passive: true })

  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.intersectionRatio >= 0.1) isVisible.value = true
      },
      { threshold: [0, 0.1, 0.5] },
    )
    observer.observe(section)
  } else {
    isVisible.value = true
  }
})

onBeforeUnmount(() => {
  observer?.disconnect()
  window.removeEventListener('scroll', requestParallaxUpdate)
  window.removeEventListener('resize', requestParallaxUpdate)
  if (parallaxFrame !== null) window.cancelAnimationFrame(parallaxFrame)
  resetPointer()
  document.body.classList.remove('nemo-showcase-active')
})
</script>

<style scoped>
.nemo-one-showcase {
  --pointer-x: 0px;
  --pointer-y: 0px;
  --copy-parallax-y: 0px;
  --product-parallax-y: 0px;
  position: relative;
  z-index: 2;
  width: 100%;
  min-height: 148vh;
  min-height: 148svh;
  margin: 0;
  padding: 0;
  overflow: hidden;
  border: 0;
  background: #000000;
  color: #f7f8fa;
  isolation: isolate;
}

.nemo-stage {
  position: sticky;
  top: 0;
  width: 100%;
  height: 100vh;
  height: 100svh;
  overflow: hidden;
  background: #000000;
}

.nemo-stage::after {
  content: '';
  position: absolute;
  z-index: 3;
  inset: 0;
  background:
    linear-gradient(90deg, #000000 0%, transparent 12%, transparent 88%, #000000 100%),
    linear-gradient(180deg, #000000 0%, transparent 13%, transparent 87%, #000000 100%);
  pointer-events: none;
}

.nemo-ambient {
  position: absolute;
  z-index: 0;
  right: 2vw;
  bottom: 5vh;
  width: min(74vw, 1180px);
  height: min(42vh, 420px);
  border-radius: 50%;
  background: radial-gradient(
    ellipse at center,
    rgba(0, 105, 232, 0.3) 0%,
    rgba(0, 76, 170, 0.1) 42%,
    transparent 74%
  );
  filter: blur(50px);
  opacity: 0;
  transform: translate3d(var(--pointer-x), var(--pointer-y), 0);
  transition: opacity 1.6s ease, transform 0.45s ease-out;
  pointer-events: none;
}

.nemo-one-showcase--visible .nemo-ambient {
  opacity: 0.52;
  animation: nemo-glow 7s ease-in-out 1.2s infinite;
}

.nemo-copy {
  position: absolute;
  z-index: 4;
  top: clamp(126px, 20vh, 196px);
  left: clamp(34px, 6vw, 112px);
  width: min(39vw, 600px);
  opacity: 0;
  transform: translate3d(0, calc(24px + var(--copy-parallax-y)), 0);
  transition: opacity 1s ease 0.12s, transform 1.15s cubic-bezier(0.22, 1, 0.36, 1) 0.12s;
}

.nemo-one-showcase--visible .nemo-copy {
  opacity: 1;
  transform: translate3d(0, var(--copy-parallax-y), 0);
}

.nemo-eyebrow {
  margin: 0 0 clamp(22px, 3vh, 38px);
  color: rgba(225, 234, 246, 0.64);
  font-family: 'IBM Plex Mono', 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: clamp(10px, 0.78vw, 13px);
  font-weight: 500;
  letter-spacing: 0.2em;
  line-height: 1.5;
  text-transform: uppercase;
}

.nemo-title {
  max-width: 10.5ch;
  margin: 0;
  color: #ffffff;
  font-size: clamp(46px, 5.3vw, 92px);
  font-weight: 430;
  letter-spacing: -0.055em;
  line-height: 0.96;
  text-wrap: balance;
}

.nemo-title span {
  display: block;
}

.nemo-description {
  max-width: 35rem;
  margin: clamp(26px, 4vh, 42px) 0 0;
  color: rgba(225, 234, 246, 0.7);
  font-size: clamp(14px, 1.08vw, 18px);
  font-weight: 400;
  letter-spacing: 0.005em;
  line-height: 1.65;
}

.nemo-product-shell {
  position: absolute;
  z-index: 2;
  top: 54%;
  right: clamp(-90px, -3vw, -34px);
  width: min(88vw, 1240px);
  height: min(74vh, 700px);
  opacity: 0;
  transform: translate3d(
      calc(var(--pointer-x) + 18px),
      calc(-50% + var(--pointer-y) + var(--product-parallax-y) + 96px),
      0
    )
    scale(0.955);
  transform-origin: 62% 54%;
  transition: opacity 0.78s ease 0.08s, transform 0.96s cubic-bezier(0.16, 1, 0.3, 1) 0.08s;
  will-change: transform, opacity;
}

.nemo-one-showcase--visible .nemo-product-shell {
  opacity: 1;
  transform: translate3d(
      var(--pointer-x),
      calc(-50% + var(--pointer-y) + var(--product-parallax-y)),
      0
    )
    scale(1);
}

.nemo-product-motion {
  position: absolute;
  inset: 0;
  transform-origin: 62% 54%;
}

.nemo-one-showcase--visible .nemo-product-motion {
  animation: nemo-product-drift 8s ease-in-out 1.5s infinite;
}

.nemo-product-frame {
  position: absolute;
  inset: 0;
  overflow: hidden;
  -webkit-mask-image:
    linear-gradient(90deg, transparent 0%, #000000 13%, #000000 87%, transparent 100%),
    linear-gradient(180deg, transparent 0%, #000000 14%, #000000 88%, transparent 100%);
  -webkit-mask-composite: source-in;
  mask-image:
    linear-gradient(90deg, transparent 0%, #000000 13%, #000000 87%, transparent 100%),
    linear-gradient(180deg, transparent 0%, #000000 14%, #000000 88%, transparent 100%);
  mask-composite: intersect;
}

.nemo-product-frame::after {
  content: '';
  position: absolute;
  inset: -2px;
  background: radial-gradient(
    ellipse 75% 70% at 61% 54%,
    transparent 44%,
    rgba(0, 0, 0, 0.08) 58%,
    rgba(0, 0, 0, 0.55) 82%,
    #000000 100%
  );
  pointer-events: none;
}

.nemo-product-frame img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  filter: saturate(1.04) contrast(1.035);
  transform: scale(1.015);
  user-select: none;
  pointer-events: none;
}

.nemo-sheen {
  position: absolute;
  z-index: 3;
  top: -14%;
  left: 25%;
  width: 11%;
  height: 130%;
  background: linear-gradient(
    100deg,
    transparent 0%,
    rgba(175, 215, 255, 0.06) 32%,
    rgba(226, 243, 255, 0.34) 50%,
    rgba(118, 188, 255, 0.08) 68%,
    transparent 100%
  );
  filter: blur(17px);
  opacity: 0;
  transform: translate3d(-180%, 0, 0) rotate(14deg);
  mix-blend-mode: screen;
  pointer-events: none;
}

.nemo-one-showcase--visible .nemo-sheen {
  animation: nemo-sheen-pass 7.5s ease-in-out 2s infinite;
}

@keyframes nemo-product-drift {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
  }

  50% {
    transform: translate3d(-0.45vw, -8px, 0) scale(1.018);
  }
}

@keyframes nemo-glow {
  0%,
  100% {
    opacity: 0.42;
  }

  50% {
    opacity: 0.58;
  }
}

@keyframes nemo-sheen-pass {
  0%,
  62% {
    opacity: 0;
    transform: translate3d(-180%, 0, 0) rotate(14deg);
  }

  70% {
    opacity: 0.22;
  }

  86% {
    opacity: 0.06;
    transform: translate3d(680%, 0, 0) rotate(14deg);
  }

  100% {
    opacity: 0;
    transform: translate3d(680%, 0, 0) rotate(14deg);
  }
}

@media (max-width: 900px) {
  .nemo-one-showcase {
    min-height: 100vh;
    min-height: 100svh;
  }

  .nemo-stage {
    position: relative;
    top: auto;
  }

  .nemo-copy {
    top: clamp(94px, 13svh, 124px);
    left: 22px;
    width: calc(100% - 44px);
  }

  .nemo-eyebrow {
    margin-bottom: 18px;
    font-size: 9px;
    letter-spacing: 0.16em;
  }

  .nemo-title {
    max-width: 12ch;
    font-size: clamp(38px, 12vw, 60px);
    line-height: 0.98;
  }

  .nemo-description {
    max-width: 31rem;
    margin-top: 18px;
    font-size: clamp(13px, 3.7vw, 16px);
    line-height: 1.55;
  }

  .nemo-product-shell {
    top: 68%;
    right: -27vw;
    width: 152vw;
    height: 58svh;
    transform-origin: 60% 52%;
  }

  .nemo-product-frame {
    -webkit-mask-image:
      linear-gradient(90deg, transparent 0%, #000000 16%, #000000 84%, transparent 100%),
      linear-gradient(180deg, transparent 0%, #000000 15%, #000000 87%, transparent 100%);
    mask-image:
      linear-gradient(90deg, transparent 0%, #000000 16%, #000000 84%, transparent 100%),
      linear-gradient(180deg, transparent 0%, #000000 15%, #000000 87%, transparent 100%);
  }

  .nemo-ambient {
    right: -22vw;
    bottom: 3vh;
    width: 125vw;
    height: 33vh;
    filter: blur(36px);
  }

  .nemo-sheen {
    filter: blur(20px);
  }
}

@media (max-width: 480px) and (max-height: 720px) {
  .nemo-copy {
    top: 80px;
  }

  .nemo-title {
    font-size: clamp(34px, 10.5vw, 46px);
  }

  .nemo-description {
    margin-top: 13px;
    font-size: 12px;
  }

  .nemo-product-shell {
    top: 70%;
    height: 52svh;
  }
}

@media (prefers-reduced-motion: reduce) {
  .nemo-copy,
  .nemo-product-shell,
  .nemo-ambient {
    opacity: 1;
    transition: none;
  }

  .nemo-copy {
    transform: none;
  }

  .nemo-product-shell,
  .nemo-one-showcase--visible .nemo-product-shell {
    transform: translate3d(0, -50%, 0) scale(1);
  }

  .nemo-product-motion,
  .nemo-one-showcase--visible .nemo-product-motion,
  .nemo-one-showcase--visible .nemo-ambient {
    animation: none;
  }

  .nemo-sheen {
    display: none;
  }
}
</style>

<style>
body.nemo-showcase-active .nav,
body.nemo-showcase-active .nav.scrolled {
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
}

body.nemo-showcase-active .nav .logo {
  filter: invert(1) grayscale(1) brightness(1.8);
}

body.nemo-showcase-active .nav .menu-link,
body.nemo-showcase-active .nav .mobile-language-toggle {
  color: rgba(255, 255, 255, 0.82);
}

body.nemo-showcase-active .nav .menu-link:hover {
  color: #ffffff;
}

body.nemo-showcase-active .nav .btn-12 {
  background-color: #ffffff;
  color: #050505;
}

body.nemo-showcase-active .nav .btn-12:hover {
  background-color: #dcebfa;
  color: #050505;
}

body.nemo-showcase-active .nav .wave-group .input {
  color: #ffffff;
  border-bottom-color: rgba(255, 255, 255, 0.72);
}

body.nemo-showcase-active .nav .wave-group .label {
  color: rgba(255, 255, 255, 0.7);
}

body.nemo-showcase-active .nav .wave-group .bar::before,
body.nemo-showcase-active .nav .wave-group .bar::after {
  background: #ffffff;
}

body.nemo-showcase-active .nav .login-icon {
  border-color: rgba(255, 255, 255, 0.88);
}

body.nemo-showcase-active .nav .login-icon:not(.login-icon--has-photo) img {
  filter: invert(1);
}

body.nemo-showcase-active .nav .login-icon:hover {
  background: #ffffff;
  border-color: #ffffff;
}

body.nemo-showcase-active .nav .login-icon:not(.login-icon--has-photo):hover img {
  filter: invert(0);
}

body.nemo-showcase-active .nav .user-avatar {
  color: #ffffff;
}

body.nemo-showcase-active .nav .login-icon:hover .user-avatar {
  color: #050505;
}

body.nemo-showcase-active .nav .menu-toggle span {
  background: #ffffff;
}

@media (max-width: 900px) {
  body.nemo-showcase-active .nav,
  body.nemo-showcase-active .nav.scrolled {
    background: transparent;
    box-shadow: none;
    backdrop-filter: none;
  }

  body.nemo-showcase-active .nav .menu--open {
    background: #ffffff;
  }

  body.nemo-showcase-active .nav .menu--open .menu-link,
  body.nemo-showcase-active .nav .menu--open .dropdown-item {
    color: #1f2933;
  }

  body.nemo-showcase-active .nav:has(.menu--open),
  body.nemo-showcase-active .nav.scrolled:has(.menu--open) {
    background: rgba(255, 255, 255, 0.98);
    box-shadow: 0 1px 0 rgba(15, 23, 42, 0.08);
  }

  body.nemo-showcase-active .nav:has(.menu--open) .logo {
    filter: none;
  }

  body.nemo-showcase-active .nav:has(.menu--open) .mobile-language-toggle {
    color: rgba(17, 24, 39, 0.68);
  }

  body.nemo-showcase-active .nav:has(.menu--open) .menu-toggle span {
    background: #111827;
  }

  body.nemo-showcase-active .nav:has(.menu--open) .login-icon {
    border-color: #111827;
  }

  body.nemo-showcase-active .nav:has(.menu--open) .login-icon:not(.login-icon--has-photo) img {
    filter: invert(0);
  }
}
</style>
