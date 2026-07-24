<template>
  <section
    id="technology-nemo-scene"
    ref="sectionRef"
    class="technology-nemo-scene"
    :lang="i18n.locale"
  >
    <span id="nemo-one" class="nemo-navigation-anchor" aria-hidden="true"></span>
    <div class="scene-stage">
      <div
        ref="surfaceRef"
        class="scene-surface"
        :class="{
          'scene-surface--transitioning': transitionStarted,
          'scene-surface--transition-complete': transitionComplete,
        }"
      >
        <div class="technology-layer">
          <div class="technology-copy">
            <h2>{{ t('technologyPage.mapTitle') }}</h2>
            <p>{{ t('technologyPage.mapInstruction') }}</p>
          </div>
        </div>

        <div class="nemo-layer">
          <div class="nemo-copy">
            <p class="nemo-eyebrow">{{ t('nemoOne.eyebrow') }}</p>
            <h2 class="nemo-title">
              <span>{{ t('nemoOne.titleLine1') }}</span>
              <span>{{ t('nemoOne.titleLine2') }}</span>
            </h2>
            <p class="nemo-description">{{ t('nemoOne.description') }}</p>
          </div>

          <div class="nemo-product" aria-hidden="true">
            <div class="nemo-product-frame">
              <img
                :src="nemoCooling"
                alt=""
                width="1024"
                height="576"
                loading="eager"
                decoding="async"
                fetchpriority="high"
              />
            </div>
            <div class="nemo-sheen"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import nemoCooling from '@/assets/images/prod/nemo-cooling.png'

const i18n = useI18nStore()
const t = (key) => i18n.t(key)

const sectionRef = ref(null)
const surfaceRef = ref(null)
const transitionStarted = ref(false)
const transitionComplete = ref(false)

let updateFrame = null
let transitionTimer = null
let transitionRunning = false
let expansionReady = false
let interactionZoneActive = false
let transitionAnchorProgress = 0
let lastScrollY = 0

const TRANSITION_DURATION_MS = 980

const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value))
const range = (value, start, end) => clamp((value - start) / (end - start))
const smooth = (value) => {
  const normalized = clamp(value)
  return normalized * normalized * (3 - 2 * normalized)
}

const setSceneVariable = (name, value) => {
  surfaceRef.value?.style.setProperty(name, value)
}

const cancelTransition = () => {
  if (transitionTimer !== null) {
    window.clearTimeout(transitionTimer)
    transitionTimer = null
  }
  transitionRunning = false
  transitionStarted.value = false
  transitionComplete.value = false
  transitionAnchorProgress = 0
}

const updateScene = () => {
  updateFrame = null

  const section = sectionRef.value
  const surface = surfaceRef.value
  if (!section || !surface) return

  const bounds = section.getBoundingClientRect()
  const viewportHeight = window.innerHeight || 1
  const isDesktop = window.matchMedia(
    '(min-width: 901px) and (prefers-reduced-motion: no-preference)',
  ).matches
  const navHeight = document.querySelector('.nav')?.getBoundingClientRect().height
    || (window.innerWidth <= 900 ? 68 : 80)

  if (!isDesktop) {
    cancelTransition()
    expansionReady = false
    interactionZoneActive = false
    surface.style.clipPath = 'none'
    document.body.classList.toggle(
      'technology-nemo-theme-active',
      bounds.top <= navHeight && bounds.bottom > navHeight,
    )
    return
  }

  const expansionProgress = smooth(
    clamp((viewportHeight * 0.58 - bounds.top) / (viewportHeight * 0.58)),
  )
  expansionReady = expansionProgress >= 0.999
  const topInset = Math.max(0, (viewportHeight - 430) / 2) * (1 - expansionProgress)
  const sideInset = 19 * (1 - expansionProgress)
  const cornerRadius = 28 * (1 - expansionProgress)
  surface.style.clipPath = `inset(${topInset.toFixed(2)}px ${sideInset.toFixed(3)}% round ${cornerRadius.toFixed(2)}px)`

  const scrollDistance = Math.max(1, section.offsetHeight - viewportHeight)
  const sceneProgress = clamp(-bounds.top / scrollDistance)
  interactionZoneActive = bounds.top <= 1 && bounds.bottom >= viewportHeight - 1

  // Leaving the scene or returning to the page top must not leave a delayed
  // handoff or its CSS state behind.
  if (
    transitionStarted.value
    && (window.scrollY <= 8 || bounds.bottom <= 0 || bounds.top >= viewportHeight)
  ) {
    cancelTransition()
  }

  if (
    !transitionStarted.value
    && !transitionRunning
    && !transitionComplete.value
    && expansionReady
    && interactionZoneActive
    && sceneProgress >= 0.035
  ) {
    startFixedTransition()
  }

  if (
    transitionStarted.value
    && !transitionRunning
    && window.scrollY < lastScrollY - 1
    && bounds.top > 1
  ) {
    cancelTransition()
  }
  lastScrollY = window.scrollY

  const nemoDrift = transitionComplete.value
    ? smooth(range(sceneProgress, transitionAnchorProgress, 0.96))
    : 0
  setSceneVariable('--nemo-copy-drift-y', `${(-nemoDrift * 34).toFixed(2)}px`)
  setSceneVariable('--nemo-product-drift-y', `${(nemoDrift * 30).toFixed(2)}px`)

  const darkTop = bounds.top + topInset
  document.body.classList.toggle(
    'technology-nemo-theme-active',
    darkTop <= navHeight && bounds.bottom > navHeight,
  )
}

const requestSceneUpdate = () => {
  if (updateFrame !== null) return
  updateFrame = window.requestAnimationFrame(updateScene)
}

const startFixedTransition = () => {
  if (
    transitionStarted.value
    || transitionRunning
    || transitionComplete.value
  ) return

  const section = sectionRef.value
  if (!section) return

  const viewportHeight = window.innerHeight || 1
  const scrollDistance = Math.max(1, section.offsetHeight - viewportHeight)
  transitionAnchorProgress = clamp(-section.getBoundingClientRect().top / scrollDistance)
  transitionStarted.value = true
  transitionRunning = true

  transitionTimer = window.setTimeout(() => {
    transitionTimer = null
    transitionRunning = false
    transitionComplete.value = true
    requestSceneUpdate()
  }, TRANSITION_DURATION_MS)
}

onMounted(() => {
  lastScrollY = window.scrollY
  updateScene()
  window.requestAnimationFrame(requestSceneUpdate)
  window.addEventListener('scroll', requestSceneUpdate, { passive: true })
  window.addEventListener('resize', requestSceneUpdate, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', requestSceneUpdate)
  window.removeEventListener('resize', requestSceneUpdate)
  if (updateFrame !== null) window.cancelAnimationFrame(updateFrame)
  cancelTransition()
  document.body.classList.remove('technology-nemo-theme-active')
})
</script>

<style scoped>
.technology-nemo-scene {
  position: relative;
  z-index: 2;
  min-height: 185vh;
  min-height: 185svh;
  background: #ffffff;
}

.nemo-navigation-anchor {
  position: absolute;
  top: 3.5svh;
  left: 0;
  width: 1px;
  height: 1px;
  pointer-events: none;
}

.scene-stage {
  position: sticky;
  top: 0;
  width: 100%;
  height: 100vh;
  height: 100svh;
  overflow: hidden;
}

.scene-surface {
  --nemo-copy-drift-y: 0px;
  --nemo-product-drift-y: 0px;
  position: absolute;
  inset: 0;
  overflow: hidden;
  background: #000000;
  color: #ffffff;
  isolation: isolate;
  will-change: clip-path;
}

.technology-layer,
.nemo-layer {
  position: absolute;
  inset: 0;
}

.technology-layer {
  z-index: 4;
  display: grid;
  place-items: center;
  opacity: 1;
  filter: blur(0);
  transform: translateY(0) scale(1);
  transform-origin: center;
  transition:
    opacity 0.72s cubic-bezier(0.22, 1, 0.36, 1),
    filter 0.82s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.82s cubic-bezier(0.22, 1, 0.36, 1);
  will-change: opacity, filter, transform;
  pointer-events: none;
}

.technology-copy {
  width: min(46vw, 740px);
  text-align: center;
}

.technology-copy h2 {
  margin: 0;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(48px, 5vw, 82px);
  font-weight: 400;
  line-height: 0.98;
  letter-spacing: -0.055em;
}

.technology-copy p {
  max-width: 650px;
  margin: 28px auto 0;
  color: rgba(250, 249, 245, 0.72);
  font-size: clamp(15px, 1.25vw, 19px);
  line-height: 1.6;
}

.nemo-layer {
  z-index: 3;
  opacity: 0;
  transition: opacity 0.74s ease 0.12s;
  pointer-events: none;
}

.nemo-copy {
  position: absolute;
  z-index: 5;
  top: clamp(168px, 34vh, 360px);
  left: clamp(34px, 6vw, 112px);
  width: min(39vw, 600px);
  transform: translate3d(0, calc(72px + var(--nemo-copy-drift-y)), 0);
  transition: transform 0.86s cubic-bezier(0.16, 1, 0.3, 1) 0.08s;
  will-change: transform;
}

.nemo-eyebrow {
  margin: 0 0 clamp(22px, 3vh, 38px);
  color: rgba(225, 234, 246, 0.64);
  font-family: 'IBM Plex Mono', 'JetBrains Mono', ui-monospace, monospace;
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

@media (min-width: 901px) {
  .technology-nemo-scene:lang(zh) .nemo-copy {
    width: min(52vw, 820px);
  }

  .technology-nemo-scene:lang(zh) .nemo-title {
    max-width: none;
    font-size: clamp(44px, 4.7vw, 80px);
  }

  .technology-nemo-scene:lang(zh) .nemo-title span {
    white-space: nowrap;
  }
}

.nemo-description {
  max-width: 35rem;
  margin: clamp(26px, 4vh, 42px) 0 0;
  color: rgba(225, 234, 246, 0.7);
  font-size: clamp(14px, 1.08vw, 18px);
  line-height: 1.65;
}

.nemo-product {
  position: absolute;
  z-index: 2;
  top: 54%;
  right: clamp(-90px, -3vw, -34px);
  width: min(88vw, 1240px);
  height: min(74vh, 700px);
  transform:
    translate3d(0, calc(-50% + 118px + var(--nemo-product-drift-y)), 0)
    scale(0.95);
  transform-origin: 62% 54%;
  transition: transform 0.92s cubic-bezier(0.16, 1, 0.3, 1) 0.06s;
  will-change: transform;
}

.scene-surface--transitioning .technology-layer,
.scene-surface--transition-complete .technology-layer {
  opacity: 0;
  filter: blur(8px);
  transform: translateY(-62px) scale(0.955);
}

.scene-surface--transitioning .nemo-layer,
.scene-surface--transition-complete .nemo-layer {
  opacity: 1;
}

.scene-surface--transitioning .nemo-copy,
.scene-surface--transition-complete .nemo-copy {
  transform: translate3d(0, var(--nemo-copy-drift-y), 0);
}

.scene-surface--transitioning .nemo-product,
.scene-surface--transition-complete .nemo-product {
  transform:
    translate3d(0, calc(-50% + var(--nemo-product-drift-y)), 0)
    scale(1);
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
    transparent,
    rgba(226, 243, 255, 0.3),
    transparent
  );
  filter: blur(17px);
  opacity: 0.16;
  transform: translate3d(320%, 0, 0) rotate(14deg);
  mix-blend-mode: screen;
}

@media (max-width: 900px) {
  .technology-nemo-scene {
    min-height: 0;
    background: #000000;
  }

  .nemo-navigation-anchor {
    top: 100svh;
  }

  .scene-stage {
    position: relative;
    top: auto;
    height: auto;
    overflow: visible;
  }

  .scene-surface {
    position: relative;
    inset: auto;
    clip-path: none;
  }

  .technology-layer,
  .nemo-layer {
    position: relative;
    inset: auto;
    min-height: 100vh;
    min-height: 100svh;
    opacity: 1;
    filter: none;
    transform: none;
  }

  .technology-layer {
    padding: 88px 20px 44px;
  }

  .technology-copy {
    width: min(100%, 440px);
  }

  .technology-copy h2 {
    font-size: clamp(36px, 10.4vw, 52px);
  }

  .technology-copy p {
    max-width: 31ch;
    margin-top: 16px;
    font-size: clamp(12px, 3.4vw, 15px);
  }

  .nemo-copy {
    top: clamp(94px, 13svh, 124px);
    left: 22px;
    width: calc(100% - 44px);
    transform: none;
  }

  .nemo-eyebrow {
    margin-bottom: 18px;
    font-size: 9px;
  }

  .nemo-title {
    max-width: 12ch;
    font-size: clamp(38px, 12vw, 60px);
  }

  .nemo-description {
    max-width: 31rem;
    margin-top: 18px;
    font-size: clamp(13px, 3.7vw, 16px);
  }

  .nemo-product {
    top: 68%;
    right: -27vw;
    width: 152vw;
    height: 58svh;
    transform: translate3d(0, -50%, 0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .technology-nemo-scene {
    min-height: 0;
    background: #000000;
  }

  .nemo-navigation-anchor {
    top: 100svh;
  }

  .scene-stage {
    position: relative;
    height: auto;
  }

  .scene-surface {
    position: relative;
    clip-path: none !important;
  }

  .technology-layer,
  .nemo-layer {
    position: relative;
    min-height: 100svh;
    opacity: 1;
    filter: none;
    transform: none;
  }
}
</style>

<style>
body.technology-nemo-theme-active .nav,
body.technology-nemo-theme-active .nav.scrolled {
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
}

body.technology-nemo-theme-active .nav .logo {
  filter: invert(1) grayscale(1) brightness(1.8);
}

body.technology-nemo-theme-active .nav .menu-link,
body.technology-nemo-theme-active .nav .mobile-language-toggle {
  color: rgba(255, 255, 255, 0.82);
}

body.technology-nemo-theme-active .nav .btn-12 {
  background-color: #ffffff;
  color: #050505;
}

body.technology-nemo-theme-active .nav .login-icon {
  border-color: rgba(255, 255, 255, 0.88);
}

body.technology-nemo-theme-active .nav .login-icon:not(.login-icon--has-photo) img {
  filter: invert(1);
}

body.technology-nemo-theme-active .nav .user-avatar {
  color: #ffffff;
}

body.technology-nemo-theme-active .nav .menu-toggle span {
  background: #ffffff;
}

@media (max-width: 900px) {
  body.technology-nemo-theme-active .nav:has(.menu--open),
  body.technology-nemo-theme-active .nav.scrolled:has(.menu--open) {
    background: rgba(255, 255, 255, 0.98);
  }

  body.technology-nemo-theme-active .nav:has(.menu--open) .logo {
    filter: none;
  }

  body.technology-nemo-theme-active .nav:has(.menu--open) .mobile-language-toggle {
    color: rgba(17, 24, 39, 0.68);
  }

  body.technology-nemo-theme-active .nav:has(.menu--open) .login-icon {
    border-color: #111827;
  }

  body.technology-nemo-theme-active .nav:has(.menu--open) .menu-toggle span {
    background: #111827;
  }
}
</style>
