<template>
  <section
    ref="sectionRef"
    class="company-orbit-section"
    aria-labelledby="company-transition-title"
  >
    <div ref="stageRef" class="company-orbit-stage">
      <div v-show="showPhotos" class="orbit-ring" aria-hidden="true"></div>

      <div v-show="showPhotos" class="photo-orbit" aria-hidden="true">
        <figure
          v-for="(image, index) in aboutImages"
          :key="image"
          :ref="(element) => setPhotoRef(element, index)"
          class="photo-card"
          :style="{ '--photo-delay': (index * 0.065).toFixed(3) }"
        >
          <img
            :src="image"
            alt=""
            loading="lazy"
            decoding="async"
            draggable="false"
          />
        </figure>
      </div>

      <div class="transition-summary">
        <h2 id="company-transition-title" class="transition-title">
          {{ t('companyTransition.title') }}
        </h2>

        <div class="logo-gate" aria-hidden="true">
          <img :src="logoMark" alt="" draggable="false" />
        </div>
      </div>

      <div v-show="showPhotos" class="gallery-haze" aria-hidden="true"></div>
      <div class="background-wash" aria-hidden="true"></div>
      <div class="white-fill"></div>
    </div>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18nStore } from '@/stores/i18n'
import logoMark from '@/assets/images/black-logo.png'

const i18n = useI18nStore()
const t = (key) => i18n.t(key)
const showPhotos = false

const baseUrl = 'https://pages-1327732770.cos.ap-guangzhou.myqcloud.com/about'
const aboutImages = Array.from({ length: 6 }, (_, index) => `${baseUrl}/${index + 1}.jpg?v2`)

const sectionRef = ref(null)
const stageRef = ref(null)
const photoRefs = []

const SCRUB_RESPONSE_MS = 105
const PROGRESS_EPSILON = 0.00035

let animationFrame = 0
let targetFrame = 0
let lastFrameTime = 0
let renderedProgress = 0
let targetProgress = 0
let sceneInitialized = false

const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value))

const range = (value, start, end) => clamp((value - start) / (end - start))

const smooth = (value) => {
  const normalized = clamp(value)
  return normalized * normalized * normalized
    * (normalized * (normalized * 6 - 15) + 10)
}

const setPhotoRef = (element, index) => {
  if (element) photoRefs[index] = element
}

const setSceneVariable = (name, value) => {
  stageRef.value?.style.setProperty(name, value)
}

const updatePhotoPositions = (rotationProgress) => {
  const stage = stageRef.value
  if (!stage) return

  const bounds = stage.getBoundingClientRect()
  const radius = Math.min(bounds.width * 0.58, bounds.height * 0.88)
  const centerX = bounds.width * 0.5
  const centerY = bounds.height * 1.04
  const rotation = 38 - rotationProgress * 76
  const baseAngles = [-72, -44, -16, 16, 44, 72]

  setSceneVariable('--orbit-radius', `${radius}px`)

  photoRefs.forEach((element, index) => {
    if (!element) return

    const angle = baseAngles[index] + rotation
    const radians = (angle * Math.PI) / 180
    const x = centerX + Math.sin(radians) * radius
    const y = centerY - Math.cos(radians) * radius
    const tilt = clamp(angle * 0.2, -18, 18)

    element.style.setProperty('--card-x', `${x.toFixed(2)}px`)
    element.style.setProperty('--card-y', `${y.toFixed(2)}px`)
    element.style.setProperty('--card-tilt', `${tilt.toFixed(2)}deg`)
  })
}

const renderScene = (progress) => {
  const section = sectionRef.value
  const stage = stageRef.value
  if (!section || !stage) return

  const photosReveal = smooth(range(progress, 0.17, 0.265))
  const rotationProgress = smooth(range(progress, 0.2, 0.58))
  const exitProgress = smooth(range(progress, 0.57, 0.7))
  const whiteProgress = smooth(range(progress, 0.05, 0.92))
  const whiteFill = smooth(range(progress, 0.9, 0.998))
  const washY = 42 - whiteProgress * 48
  const washScaleX = 0.72 + whiteProgress * 0.3
  const washScaleY = 0.7 + whiteProgress * 0.35

  setSceneVariable('--photos-reveal', photosReveal.toFixed(4))
  setSceneVariable('--exit-progress', exitProgress.toFixed(4))
  setSceneVariable('--white-progress', whiteProgress.toFixed(4))
  setSceneVariable('--wash-y', `${washY.toFixed(2)}%`)
  setSceneVariable('--wash-scale-x', washScaleX.toFixed(4))
  setSceneVariable('--wash-scale-y', washScaleY.toFixed(4))
  setSceneVariable('--white-fill', whiteFill.toFixed(4))

  updatePhotoPositions(rotationProgress)

  const bounds = section.getBoundingClientRect()
  const sectionIsVisible = bounds.top < window.innerHeight && bounds.bottom > 0
  document.body.classList.toggle(
    'company-orbit-dark',
    sectionIsVisible && whiteProgress < 0.56,
  )
}

const animateScene = (timestamp) => {
  animationFrame = 0

  const deltaTime = lastFrameTime
    ? Math.min(48, timestamp - lastFrameTime)
    : 16
  lastFrameTime = timestamp

  const blend = 1 - Math.exp(-deltaTime / SCRUB_RESPONSE_MS)
  renderedProgress += (targetProgress - renderedProgress) * blend

  if (Math.abs(targetProgress - renderedProgress) <= PROGRESS_EPSILON) {
    renderedProgress = targetProgress
  }

  renderScene(renderedProgress)

  if (renderedProgress !== targetProgress) {
    animationFrame = window.requestAnimationFrame(animateScene)
  } else {
    lastFrameTime = 0
  }
}

const updateSceneTarget = (immediate = false) => {
  targetFrame = 0

  const section = sectionRef.value
  if (!section) return

  // 手机端使用独立的紧凑渐变场景，不运行桌面的 sticky 滚动擦除。
  if (window.matchMedia('(max-width: 900px)').matches) {
    if (animationFrame) window.cancelAnimationFrame(animationFrame)
    animationFrame = 0
    lastFrameTime = 0
    sceneInitialized = false

    const bounds = section.getBoundingClientRect()
    const navSwitchLine = Math.max(68, window.innerHeight * 0.38)
    document.body.classList.toggle(
      'company-orbit-dark',
      bounds.top <= 68 && bounds.bottom > navSwitchLine,
    )
    return
  }

  const bounds = section.getBoundingClientRect()
  const stageHeight = stageRef.value?.offsetHeight || window.innerHeight
  const scrollDistance = Math.max(1, section.offsetHeight - stageHeight)
  targetProgress = clamp(-bounds.top / scrollDistance)

  if (!sceneInitialized || immediate) {
    sceneInitialized = true
    renderedProgress = targetProgress
    renderScene(renderedProgress)
    return
  }

  if (!animationFrame) {
    lastFrameTime = 0
    animationFrame = window.requestAnimationFrame(animateScene)
  }
}

const requestSceneUpdate = () => {
  if (targetFrame) return
  targetFrame = window.requestAnimationFrame(() => updateSceneTarget())
}

onMounted(async () => {
  await nextTick()
  updateSceneTarget(true)
  window.addEventListener('scroll', requestSceneUpdate, { passive: true })
  window.addEventListener('resize', requestSceneUpdate, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', requestSceneUpdate)
  window.removeEventListener('resize', requestSceneUpdate)
  if (animationFrame) window.cancelAnimationFrame(animationFrame)
  if (targetFrame) window.cancelAnimationFrame(targetFrame)
  document.body.classList.remove('company-orbit-dark')
})
</script>

<style scoped>
.company-orbit-section {
  position: relative;
  z-index: 3;
  width: 100%;
  height: 132vh;
  background: #000000;
}

.company-orbit-stage {
  --photos-reveal: 0;
  --exit-progress: 0;
  --white-progress: 0;
  --wash-y: 42%;
  --wash-scale-x: 0.72;
  --wash-scale-y: 0.7;
  --white-fill: 0;
  --orbit-radius: 520px;
  position: sticky;
  top: 0;
  width: 100%;
  height: 100vh;
  height: 100svh;
  overflow: hidden;
  background: #000000;
  isolation: isolate;
}

.orbit-ring {
  position: absolute;
  z-index: 2;
  left: 50%;
  top: 104%;
  width: calc(var(--orbit-radius) * 2);
  height: calc(var(--orbit-radius) * 2);
  border: 1px dashed rgba(255, 255, 255, 0.14);
  border-radius: 50%;
  opacity: clamp(0, calc(var(--photos-reveal) - var(--exit-progress) * 1.4), 0.52);
  transform: translate(-50%, -50%) scale(calc(0.9 + var(--photos-reveal) * 0.1));
  pointer-events: none;
}

.orbit-ring::after {
  content: '';
  position: absolute;
  inset: -5px;
  border: 6px solid transparent;
  border-top-color: rgba(255, 255, 255, 0.94);
  border-left-color: rgba(255, 255, 255, 0.94);
  border-radius: 50%;
  clip-path: polygon(0 0, 54% 0, 54% 54%, 0 54%);
  transform: rotate(8deg);
}

.photo-orbit {
  position: absolute;
  z-index: 4;
  inset: 0;
  opacity: calc(1 - var(--white-fill));
  pointer-events: none;
}

.photo-card {
  --card-x: 50vw;
  --card-y: 50vh;
  --card-tilt: 0deg;
  --photo-delay: 0;
  position: absolute;
  top: 0;
  left: 0;
  width: clamp(176px, 16vw, 252px);
  aspect-ratio: 4 / 5;
  margin: 0;
  overflow: hidden;
  border: 0;
  border-radius: 0;
  background: #000000;
  box-shadow: 0 28px 72px rgba(0, 0, 0, 0.5);
  opacity: clamp(
    0,
    calc((var(--photos-reveal) - var(--photo-delay)) * 4.5 - var(--exit-progress) * 1.35),
    1
  );
  filter:
    blur(calc(var(--exit-progress) * 18px))
    saturate(calc(1 - var(--exit-progress) * 0.5));
  transform:
    translate3d(var(--card-x), var(--card-y), 0)
    translate(-50%, -50%)
    rotate(var(--card-tilt))
    scale(calc(0.76 + var(--photos-reveal) * 0.24 - var(--exit-progress) * 0.08));
  transform-origin: center;
  will-change: transform, opacity, filter;
  -webkit-mask-image: linear-gradient(
    to bottom,
    #000000 0%,
    #000000 56%,
    rgba(0, 0, 0, 0.86) 70%,
    rgba(0, 0, 0, 0.34) 88%,
    transparent 100%
  );
  mask-image: linear-gradient(
    to bottom,
    #000000 0%,
    #000000 56%,
    rgba(0, 0, 0, 0.86) 70%,
    rgba(0, 0, 0, 0.34) 88%,
    transparent 100%
  );
}

.photo-card:nth-child(even) {
  aspect-ratio: 3 / 4;
}

.photo-card img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: contrast(1.03) saturate(0.92);
  transform: scale(1.025);
  user-select: none;
}

.transition-summary {
  position: absolute;
  z-index: 5;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: clamp(34px, 5.5vh, 58px);
  padding: 96px 32px 48px;
  text-align: center;
  transform: translateY(-2vh);
}

.transition-title {
  max-width: 14ch;
  margin: 0;
  color: #ffffff;
  font-size: clamp(44px, 5.8vw, 86px);
  font-weight: 430;
  letter-spacing: -0.055em;
  line-height: 1.04;
  text-wrap: balance;
}

.logo-gate {
  position: relative;
  width: clamp(96px, 9vw, 138px);
  aspect-ratio: 1;
  flex: 0 0 auto;
}

.logo-gate img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: invert(1) grayscale(1) brightness(2.4);
  user-select: none;
}

.gallery-haze {
  position: absolute;
  z-index: 6;
  left: 50%;
  bottom: -26vh;
  width: 150vw;
  height: 96vh;
  border-radius: 50%;
  background: radial-gradient(
    ellipse at 50% 70%,
    #ffffff 0%,
    rgba(255, 255, 255, 0.98) 24%,
    rgba(224, 246, 249, 0.92) 39%,
    rgba(105, 203, 220, 0.58) 56%,
    rgba(44, 127, 145, 0.26) 68%,
    transparent 82%
  );
  filter: blur(24px);
  opacity: clamp(
    0,
    calc(var(--white-progress) * 2.2 - var(--white-fill) * 0.8),
    1
  );
  transform:
    translateX(-50%)
    translateY(calc((1 - var(--white-progress)) * 18%))
    scale(calc(0.78 + var(--white-progress) * 0.24));
  transform-origin: center bottom;
  will-change: transform, opacity;
  pointer-events: none;
}

.background-wash {
  position: absolute;
  z-index: 7;
  left: 50%;
  top: -12%;
  width: 164vw;
  height: 150vh;
  background:
    radial-gradient(
      ellipse 56% 72% at 47% 84%,
      #ffffff 0%,
      rgba(255, 255, 255, 0.99) 32%,
      rgba(231, 247, 250, 0.96) 47%,
      rgba(147, 219, 230, 0.8) 61%,
      rgba(56, 151, 170, 0.48) 74%,
      rgba(9, 51, 61, 0.14) 86%,
      transparent 100%
    ),
    radial-gradient(
      ellipse 31% 54% at 53% 31%,
      rgba(84, 204, 226, 0.78) 0%,
      rgba(49, 159, 181, 0.5) 42%,
      rgba(16, 75, 89, 0.16) 70%,
      transparent 100%
    ),
    radial-gradient(
      ellipse 28% 43% at 31% 56%,
      rgba(74, 185, 204, 0.34) 0%,
      rgba(25, 99, 115, 0.16) 54%,
      transparent 100%
    ),
    radial-gradient(
      ellipse 32% 48% at 76% 59%,
      rgba(92, 192, 208, 0.3) 0%,
      rgba(22, 89, 103, 0.13) 56%,
      transparent 100%
    );
  filter: blur(34px);
  opacity: clamp(0, calc(var(--white-progress) * 1.4), 1);
  transform:
    translateX(-50%)
    translateY(var(--wash-y))
    scaleX(var(--wash-scale-x))
    scaleY(var(--wash-scale-y));
  transform-origin: center 78%;
  will-change: transform, opacity;
  pointer-events: none;
}

.background-wash::before {
  content: '';
  position: absolute;
  z-index: 1;
  left: 15%;
  right: 10%;
  bottom: -8%;
  height: 58%;
  background: radial-gradient(
    ellipse 68% 100% at 49% 100%,
    rgba(255, 255, 255, 0.98) 0%,
    rgba(255, 255, 255, 0.86) 45%,
    rgba(228, 246, 249, 0.5) 70%,
    transparent 100%
  );
  filter: blur(42px);
  transform: translateX(-3%) skewX(-4deg);
  pointer-events: none;
}

.background-wash::after {
  content: '';
  position: absolute;
  z-index: 2;
  left: -8%;
  right: -12%;
  bottom: -18%;
  height: 56%;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(255, 255, 255, 0.76) 34%,
    #ffffff 72%
  );
  filter: blur(36px);
  transform: rotate(-1.5deg);
  pointer-events: none;
}

.white-fill {
  position: absolute;
  z-index: 9;
  inset: -2px;
  background: #ffffff;
  opacity: var(--white-fill);
  pointer-events: none;
}

@media (max-width: 900px) {
  .company-orbit-section {
    --mobile-company-gradient: linear-gradient(
      180deg,
      #000000 0%,
      #000000 24%,
      #040404 34%,
      #111212 45%,
      #292a2a 56%,
      #4c4e4e 66%,
      #737575 73%,
      #989a9a 79%,
      #bfc0c0 84%,
      #dddddd 88%,
      #f1f1f1 91%,
      #ffffff 94%,
      #ffffff 100%
    );
    display: block;
    height: clamp(520px, 78svh, 680px);
    margin-top: -1px;
    background: var(--mobile-company-gradient);
  }

  .company-orbit-stage {
    position: relative;
    top: auto;
    height: 100%;
    background: var(--mobile-company-gradient);
  }

  .transition-summary {
    z-index: 8;
    justify-content: flex-start;
    gap: clamp(28px, 4.4svh, 38px);
    padding: clamp(108px, 15svh, 132px) 24px 34px;
    transform: none;
  }

  .transition-title {
    max-width: 10ch;
    font-size: clamp(38px, 10.2vw, 50px);
    font-weight: 440;
    line-height: 0.98;
    letter-spacing: -0.06em;
    color: #ffffff;
    text-shadow:
      0 1px 0 rgba(255, 255, 255, 0.08),
      0 12px 34px rgba(0, 0, 0, 0.42);
    opacity: 1;
    transform: none;
    transition: none;
  }

  .logo-gate {
    width: clamp(74px, 21vw, 94px);
    opacity: 1;
    transform: none;
    transition: none;
  }

  .logo-gate img {
    position: relative;
    z-index: 1;
    filter: invert(1) grayscale(1) brightness(2.6)
      drop-shadow(0 8px 18px rgba(0, 0, 0, 0.28));
  }

  .background-wash,
  .white-fill {
    display: none;
  }
}

@media (max-width: 420px) and (max-height: 720px) {
  .transition-summary {
    gap: 24px;
    padding: 96px 20px 26px;
  }

  .transition-title {
    font-size: clamp(34px, 9.6vw, 40px);
  }

  .logo-gate {
    width: 72px;
  }
}

@media (prefers-reduced-motion: reduce) and (min-width: 901px) {
  .company-orbit-section {
    height: 120vh;
  }

  .photo-card {
    filter: none;
  }

}
</style>

<style>
@media (min-width: 901px) {
  body.company-orbit-dark .nav,
  body.company-orbit-dark .nav.scrolled {
    background: rgba(0, 0, 0, 0.86);
    box-shadow: 0 1px 0 rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(18px);
  }

  body.company-orbit-dark .nav .logo {
    filter: invert(1) grayscale(1) brightness(1.8);
  }

  body.company-orbit-dark .nav .menu-link,
  body.company-orbit-dark .nav .mobile-language-toggle {
    color: rgba(255, 255, 255, 0.82);
  }

  body.company-orbit-dark .nav .menu-link:hover {
    color: #ffffff;
  }

  body.company-orbit-dark .nav .btn-12 {
    background-color: #ffffff;
    color: #050505;
  }

  body.company-orbit-dark .nav .wave-group .input {
    color: #ffffff;
    border-bottom-color: rgba(255, 255, 255, 0.72);
  }

  body.company-orbit-dark .nav .wave-group .label {
    color: rgba(255, 255, 255, 0.7);
  }

  body.company-orbit-dark .nav .wave-group .bar::before,
  body.company-orbit-dark .nav .wave-group .bar::after {
    background: #ffffff;
  }

  body.company-orbit-dark .nav .login-icon {
    border-color: rgba(255, 255, 255, 0.88);
  }

  body.company-orbit-dark .nav .login-icon:not(.login-icon--has-photo) img {
    filter: invert(1);
  }

  body.company-orbit-dark .nav .login-icon:hover {
    background: #ffffff;
    border-color: #ffffff;
  }

  body.company-orbit-dark .nav .login-icon:not(.login-icon--has-photo):hover img {
    filter: invert(0);
  }

  body.company-orbit-dark .nav .user-avatar {
    color: #ffffff;
  }

  body.company-orbit-dark .nav .login-icon:hover .user-avatar {
    color: #050505;
  }
}


@media (max-width: 900px) {
  body.company-orbit-dark .nav,
  body.company-orbit-dark .nav.scrolled {
    background: rgba(0, 0, 0, 0.9);
    box-shadow: 0 1px 0 rgba(255, 255, 255, 0.1);
  }

  body.company-orbit-dark .nav .logo {
    filter: invert(1) grayscale(1) brightness(1.8);
  }

  body.company-orbit-dark .nav .mobile-language-toggle {
    color: rgba(255, 255, 255, 0.82);
  }

  body.company-orbit-dark .nav .login-icon {
    border-color: rgba(255, 255, 255, 0.88);
  }

  body.company-orbit-dark .nav .login-icon:not(.login-icon--has-photo) img {
    filter: invert(1);
  }

  body.company-orbit-dark .nav .user-avatar {
    color: #ffffff;
  }

  body.company-orbit-dark .nav .menu-toggle span {
    background: #ffffff;
  }

  body.company-orbit-dark .nav:has(.menu--open),
  body.company-orbit-dark .nav.scrolled:has(.menu--open) {
    background: rgba(255, 255, 255, 0.98);
    box-shadow: 0 1px 0 rgba(15, 23, 42, 0.08);
  }

  body.company-orbit-dark .nav:has(.menu--open) .logo {
    filter: none;
  }

  body.company-orbit-dark .nav:has(.menu--open) .mobile-language-toggle {
    color: #1f2933;
  }

  body.company-orbit-dark .nav:has(.menu--open) .login-icon {
    border-color: #1f2933;
  }

  body.company-orbit-dark .nav:has(.menu--open) .login-icon:not(.login-icon--has-photo) img {
    filter: none;
  }

  body.company-orbit-dark .nav:has(.menu--open) .menu-toggle span {
    background: #1f2933;
  }
}
</style>
