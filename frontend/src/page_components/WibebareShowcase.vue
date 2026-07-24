<template>
  <section
    ref="heroRef"
    class="home-hero"
    :class="{
      'is-section-active': isSectionActive,
    }"
    :lang="i18n.locale"
  >
    <div class="home-hero-inner">
      <h1 class="home-headline">
        <span class="home-headline-line">{{ t("pages.home.headlineLine1") }}</span>
        <span class="home-headline-line">
          <span>{{ t("pages.home.headlineLine2Prefix") }}</span>
          <span class="home-headline-muted">{{ t("pages.home.headlineAccent") }}</span>
        </span>
        <span class="home-headline-gradient" aria-hidden="true">
          <span class="home-headline-line">{{ t("pages.home.headlineLine1") }}</span>
          <span class="home-headline-line">
            <span>{{ t("pages.home.headlineLine2Prefix") }}</span>
            <span class="home-headline-muted">{{ t("pages.home.headlineAccent") }}</span>
          </span>
        </span>
      </h1>

      <div class="home-motion-layer">
        <p class="home-subtitle">
          <span class="home-subtitle-line">{{ t("pages.home.subtitleLine1") }}</span>
          <span v-if="t('pages.home.subtitleLine2')" class="home-subtitle-line">
            {{ t("pages.home.subtitleLine2") }}
          </span>
        </p>

        <div class="home-workflow" :aria-label="t('pages.home.workflowLabel')">
          <button
            v-for="stage in stages"
            :key="stage.key"
            class="home-workflow-item"
            :class="{ 'is-active': activeWorkflow === stage.key }"
            type="button"
            @click="selectWorkflow(stage.key)"
          >
            <svg
              class="home-workflow-icon"
              viewBox="0 0 1024 1024"
              aria-hidden="true"
              focusable="false"
            >
              <path v-for="path in stage.paths" :key="path" :d="path" />
            </svg>
            {{ t(stage.labelKey) }}
          </button>
        </div>

        <div class="home-visual">
          <span class="home-visual-frame" aria-hidden="true"></span>
          <img class="home-visual-image" :src="dashboardImageUrl" alt="" />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { useI18nStore } from "@/stores/i18n";
import dashboardImageUrl from "@/assets/images/prod/wibebare-dashboard.png";

const i18n = useI18nStore();
const t = (key) => i18n.t(key);
const activeWorkflow = ref("analyze");
const isSectionActive = ref(false);
const heroRef = ref(null);
let motionFrame = 0;

function selectWorkflow(key) {
  activeWorkflow.value = key;
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function smoothStep(value) {
  const normalized = clamp(value, 0, 1);
  return normalized * normalized * (3 - 2 * normalized);
}

const PHASE = {
  lift: 0.134,
  detent: 0.067,
  takeover: 0.089,
};
const TAKEOVER_END = PHASE.lift + PHASE.detent + PHASE.takeover;
const FULL_CP = TAKEOVER_END;
const EXIT_DOWN_OFFSET = 0.18;

function setCoverTransition(hero, element, token, headlineBottom, motionLayerTop, liftDistance, progress, options = {}) {
  if (!element) return;

  const startGap = options.startGap ?? 12;
  const range = options.range ?? 84;
  const maxBlur = options.maxBlur ?? 7;
  const minOpacity = options.minOpacity ?? 0.18;
  // How small the element shrinks to as it lifts/blurs away (1 = no shrink).
  const minScale = options.minScale ?? 1;
  // The lift-based fade can leave content partially visible (its strength depends on the
  // headline gap, which is larger for Chinese). `extraHide` (driven by the takeover) forces
  // the element to vanish completely — opacity AND blur reach 0 — so no blurred residual
  // band lingers behind the docked image (e.g. the workflow pills).
  const extraHide = clamp(options.extraHide ?? 0, 0, 1);
  const reveal = 1 - extraHide;
  const elementTop = motionLayerTop + element.offsetTop - progress * liftDistance;
  const blend = clamp((headlineBottom + startGap - elementTop) / range, 0, 1);

  hero.style.setProperty(`--home-${token}-blur`, `${(blend * maxBlur * reveal).toFixed(2)}px`);
  hero.style.setProperty(`--home-${token}-opacity`, ((1 - blend * (1 - minOpacity)) * reveal).toFixed(3));
  // Shrink as it recedes: driven by the lift blend, then pushed a touch further by the
  // takeover so it keeps contracting right up until it disappears.
  if (minScale < 1) {
    const shrink = clamp(blend + extraHide * 0.5, 0, 1);
    hero.style.setProperty(`--home-${token}-scale`, (1 - shrink * (1 - minScale)).toFixed(3));
  }
}

function updateTerminalMotion() {
  const hero = heroRef.value;
  if (!hero) return;

  const sectionBounds = hero.getBoundingClientRect();
  const navHeight = document.querySelector(".nav")?.getBoundingClientRect().height ?? 80;
  const entryStart = window.innerHeight * (window.innerWidth <= 900 ? 0.4 : 0.26);
  const entryEnd = window.innerHeight * (window.innerWidth <= 900 ? 0.14 : 0.1);
  const localEntryProgress = smoothStep(
    (entryStart - sectionBounds.top) / Math.max(entryStart - entryEnd, 1),
  );

  const aiosSection = hero.previousElementSibling?.classList.contains("aios-showcase")
    ? hero.previousElementSibling
    : null;
  let aiosHandoffProgress = 0;
  if (aiosSection) {
    if (window.innerWidth > 900) {
      const aiosStage = aiosSection.querySelector(".aios-stage");
      const aiosScrollRange = Math.max(
        aiosSection.offsetHeight - (aiosStage?.offsetHeight ?? window.innerHeight),
        1,
      );
      const aiosProgress = clamp((window.scrollY - aiosSection.offsetTop) / aiosScrollRange, 0, 1);
      aiosHandoffProgress = smoothStep((aiosProgress - 0.75) / 0.25);
    } else {
      const aiosBottom = aiosSection.getBoundingClientRect().bottom;
      aiosHandoffProgress = smoothStep(
        (window.innerHeight * 0.7 - aiosBottom) / Math.max(window.innerHeight * 0.34, 1),
      );
    }
  }

  const entryProgress = Math.max(localEntryProgress, aiosHandoffProgress);

  const headline = hero.querySelector(".home-headline");
  const motionLayer = hero.querySelector(".home-motion-layer");
  const visual = hero.querySelector(".home-visual");
  const subtitle = hero.querySelector(".home-subtitle");
  const workflow = hero.querySelector(".home-workflow");
  if (!headline || !motionLayer || !visual) return;

  const heroScrollRange = Math.max(hero.offsetHeight - window.innerHeight, 1);
  const terminalY = hero.offsetTop + heroScrollRange;
  const exitEndY = terminalY + window.innerHeight * EXIT_DOWN_OFFSET;
  const exitEase = smoothStep(
    (window.scrollY - terminalY) / Math.max(exitEndY - terminalY, 1),
  );
  // Visibility is isolated from animation progress. The full timed sequence continues
  // offscreen, while the fixed layer is clipped before the CTA becomes visible.
  const visibilityFloor = Math.max(navHeight, window.innerHeight * 0.58);
  const isInsideDisplayBand = sectionBounds.top < window.innerHeight
    && sectionBounds.bottom > visibilityFloor;
  isSectionActive.value = entryProgress > 0.001 && isInsideDisplayBand;
  hero.style.setProperty("--home-section-entry-opacity", entryProgress.toFixed(3));
  const physicalProgress = clamp(
    (window.scrollY - hero.offsetTop) / heroScrollRange,
    0,
    1,
  );
  const timedProgress = physicalProgress * FULL_CP;
  const liftProgress = clamp(timedProgress / PHASE.lift, 0, 1);
  const takeoverProgress = clamp(
    (timedProgress - PHASE.lift - PHASE.detent) / PHASE.takeover,
    0,
    1,
  );
  // The dashboard image follows the physical scroll position independently from the
  // timed text checkpoints, so its movement can be scrubbed in either direction.
  const visualProgress = physicalProgress * FULL_CP;
  const visualLiftProgress = clamp(visualProgress / PHASE.lift, 0, 1);
  const rawVisualTakeoverProgress = clamp(
    (visualProgress - PHASE.lift - PHASE.detent) / PHASE.takeover,
    0,
    1,
  );
  const visualTakeoverProgress = rawVisualTakeoverProgress;

  const bandStart = clamp(window.innerWidth * 0.05, 46, 82);
  const bandEnd = clamp(window.innerWidth * 0.03, 28, 42);
  const visualBandBase = bandStart - visualLiftProgress * (bandStart - bandEnd);
  const bandBlurStart = clamp(window.innerWidth * 0.026, 28, 42);
  const bandBlurEnd = clamp(window.innerWidth * 0.014, 16, 24);
  const visualBandBlurBase = bandBlurStart
    - visualLiftProgress * (bandBlurStart - bandBlurEnd);
  const isZhHeadline = i18n.locale === "zh" || i18n.locale === "zh-CN";
  const targetGap = isZhHeadline
    ? clamp(window.innerHeight * 0.045, 34, 54)
    : clamp(window.innerHeight * 0.02, 16, 22);
  const visualTop = motionLayer.offsetTop + visual.offsetTop;
  const headlineBottom = headline.offsetTop + headline.offsetHeight;
  const liftDistance = Math.max(0, visualTop - headlineBottom - targetGap);
  const visualTopAfterLift = headlineBottom + targetGap;
  const endScale = 1.32;
  const visualRenderedHeight = visual.offsetHeight * endScale;
  const availableHeight = window.innerHeight - navHeight;
  const centeredTop = navHeight + (availableHeight - visualRenderedHeight) / 2;
  const centeringLift = Math.max(0, visualTopAfterLift - centeredTop);
  const maxTakeoverLift = Math.max(0, visualTopAfterLift - navHeight - 8);
  const takeoverLift = Math.min(centeringLift, maxTakeoverLift);
  const textMotionY = -(liftProgress * liftDistance + takeoverProgress * takeoverLift);
  const visualMotionY = -(
    visualLiftProgress * liftDistance
    + visualTakeoverProgress * takeoverLift
  );
  const visualTopScreen = visualTop + visualMotionY;
  const bandSafeRoom = Math.max(0, visualTopScreen - navHeight);
  const bandCompressionLead = clamp(window.innerHeight * 0.03, 22, 36);
  const bandCompression = clamp(
    bandSafeRoom / (visualBandBase + visualBandBlurBase + bandCompressionLead),
    0,
    1,
  );
  const exitReveal = 1 - exitEase;
  const visualBand = visualBandBase * bandCompression * exitReveal;
  const visualBandBlur = visualBandBlurBase * bandCompression * exitReveal;
  const visualBandTight = visualBand * 0.42;
  const visualBandSoftBlur = visualBandBlur * 0.34;
  const headlineRise = takeoverProgress * (takeoverLift - headline.offsetHeight * 0.35);
  const visualScale = (
    1
    + visualLiftProgress * 0.12
    + visualTakeoverProgress * 0.2
  ) * (1 - exitEase * 0.18);
  const visualOffsetY = visualMotionY - textMotionY - exitEase * 38;
  const visualOpacity = 1 - exitEase;

  hero.style.setProperty("--home-headline-cover", `${(liftProgress * 100).toFixed(2)}%`);
  hero.style.setProperty("--home-headline-scale", (1 - takeoverProgress * 0.35).toFixed(4));
  hero.style.setProperty("--home-headline-opacity", (1 - takeoverProgress).toFixed(3));
  hero.style.setProperty("--home-headline-y", `${(-headlineRise).toFixed(2)}px`);
  hero.style.setProperty("--home-motion-y", `${textMotionY.toFixed(2)}px`);
  hero.style.setProperty("--home-visual-scale", visualScale.toFixed(4));
  hero.style.setProperty("--home-visual-x", "0px");
  hero.style.setProperty("--home-visual-y", `${visualOffsetY.toFixed(2)}px`);
  hero.style.setProperty("--home-visual-opacity", visualOpacity.toFixed(3));
  hero.style.setProperty("--home-visual-blur", `${(exitEase * 8).toFixed(2)}px`);
  hero.style.setProperty("--home-collapse-progress", "0");
  hero.style.setProperty("--home-visual-band", `${visualBand.toFixed(2)}px`);
  hero.style.setProperty("--home-visual-band-blur", `${visualBandBlur.toFixed(2)}px`);
  hero.style.setProperty("--home-visual-band-offset", `${(-visualBand).toFixed(2)}px`);
  hero.style.setProperty("--home-visual-band-top-offset", `${(-visualBand).toFixed(2)}px`);
  hero.style.setProperty("--home-visual-band-soft-blur", `${visualBandSoftBlur.toFixed(2)}px`);
  hero.style.setProperty("--home-visual-band-tight", `${visualBandTight.toFixed(2)}px`);
  hero.style.setProperty("--home-visual-band-tight-offset", `${(-visualBandTight).toFixed(2)}px`);
  hero.style.setProperty("--home-visual-band-tight-top-offset", `${(-visualBandTight).toFixed(2)}px`);

  setCoverTransition(hero, subtitle, "subtitle", headlineBottom, motionLayer.offsetTop, liftDistance, liftProgress, {
    maxBlur: 8,
    minOpacity: 0,
    minScale: 0.78,
    extraHide: takeoverProgress,
  });
  setCoverTransition(hero, workflow, "workflow", headlineBottom, motionLayer.offsetTop, liftDistance, liftProgress, {
    startGap: 24,
    range: 56,
    maxBlur: 7,
    minOpacity: 0,
    minScale: 0.8,
    extraHide: takeoverProgress,
  });
}

function updateHomeMotion() {
  updateTerminalMotion();
}

function requestHomeMotionUpdate() {
  if (motionFrame) return;
  motionFrame = window.requestAnimationFrame(() => {
    motionFrame = 0;
    updateHomeMotion();
  });
}

onMounted(async () => {
  await nextTick();
  updateHomeMotion();
  window.addEventListener("scroll", requestHomeMotionUpdate, { passive: true });
  window.addEventListener("resize", requestHomeMotionUpdate);
});

onBeforeUnmount(() => {
  if (motionFrame) {
    window.cancelAnimationFrame(motionFrame);
    motionFrame = 0;
  }

  window.removeEventListener("scroll", requestHomeMotionUpdate);
  window.removeEventListener("resize", requestHomeMotionUpdate);
});

const stages = [
  {
    key: "analyze",
    labelKey: "pages.home.stages.analyze",
    paths: [
      "M586.752 457.728l20.48 60.928c2.56 7.68 10.24 13.312 17.92 13.312 2.048 0 3.584 0 5.632-1.024 9.216-3.584 14.848-14.336 11.264-23.552l-20.48-60.928c-3.584-9.728-13.824-15.36-23.552-11.264-9.216 3.072-13.824 13.312-11.264 22.528z m314.368 425.984H139.776V121.344c0-10.24-8.192-18.944-18.944-18.944-10.24 0-18.432 8.704-18.432 18.944v781.312c0 10.24 8.192 18.944 18.944 18.944H901.12c10.24 0 18.944-8.704 18.944-18.944-0.512-10.24-8.704-18.944-18.944-18.944z m-273.408-302.592l18.944 54.272c2.56 7.68 9.216 12.288 17.92 12.288h56.32c10.24 0 18.944-8.704 18.944-18.944s-8.192-18.944-18.944-18.944h-43.008l-13.824-41.472c-3.584-9.728-13.824-15.36-23.552-11.264-10.752 3.072-16.384 13.824-12.8 24.064zM199.68 655.872h70.144c6.656 0 12.288-3.072 14.848-8.704l58.88-86.528 82.432 152.576c3.584 5.632 9.216 9.728 16.896 9.728h2.048c7.68-1.024 13.824-5.632 15.872-12.288l105.472-314.88v1.024c2.56 7.68 10.24 13.312 17.92 13.312 2.048 0 3.584 0 5.632-1.024 9.216-3.072 14.848-14.336 12.288-23.552l-17.92-54.272s0-1.024-1.024-1.024c0-1.024-1.024-1.024-1.024-2.048s-1.024-1.024-1.024-2.048-1.024-1.024-1.024-1.024c0-1.024-1.024-1.024-1.024-2.048l-0.512 0.512-2.048-2.048c-1.024 0-1.024-1.024-2.048-1.024s-1.024-1.024-2.048-1.024c0 0-1.024 0-1.024-1.024H558.08s-1.024 0-1.024 1.024c-1.024 0-1.024 1.024-2.048 1.024s-1.024 1.024-2.048 1.024c0 0 0 1.024-0.512 1.024l-1.024 1.024-1.024 1.024s-1.024 1.024-1.024 2.048-1.024 1.024-1.024 2.048-1.024 1.024-1.024 2.048c0 0 0 1.024-1.024 1.024l-107.52 327.168L363.52 516.608c-2.56-5.632-9.216-9.728-14.848-9.728-6.656 0-13.312 3.072-16.896 7.68l-71.168 102.4H199.68c-10.24 0-18.944 8.704-18.944 18.944 0 10.752 8.704 19.968 18.944 19.968z m720.896-34.816c0-1.024 0-1.024-1.024-2.048 0-1.024-1.024-1.024-1.024-2.048 0 0 0-1.024-1.024-1.024 0-1.024-1.024-1.024-1.024-1.024s-1.024-1.024-2.048-1.024L843.264 558.08c-8.192-6.656-19.456-4.608-26.112 3.584-7.68 6.656-5.632 18.944 2.56 25.6l29.184 22.528h-40.448c-10.24 0-18.944 8.704-18.944 18.944s8.192 18.944 18.944 18.944h37.376l-26.112 20.992c-8.192 6.656-9.216 17.92-3.584 26.624 3.584 4.608 9.216 7.68 14.848 7.68 3.584 0 8.192-1.024 11.264-3.584l71.168-55.808 1.024-1.024 2.048-2.048s0-1.024 1.024-1.024c0-1.024 1.024-1.024 1.024-2.048s1.024-1.024 1.024-2.048 0-1.024 1.024-2.048c0-1.024 0-2.048 1.024-2.048v-9.728c0 0.512 0 0.512-1.024-0.512z",
    ],
  },
  {
    key: "pack",
    labelKey: "pages.home.stages.pack",
    paths: [
      "M940 191.58a83.38 83.38 0 0 0-61.2-26.75H634.16a28.68 28.68 0 0 0-27.87 21.94s-18.69 87.5-20.2 93-4.74 8.82-13.24 8.82H145.47a83.65 83.65 0 0 0-62 27.56c-14.41 16-21.19 36.08-19.07 56.61q0 0.26 0.06 0.52L114 780.5v0.21c4.82 37.3 37.16 77.56 81 77.56h400.46a28.68 28.68 0 0 0 0-57.35H195c-11.89 0-22.62-16.37-24.1-27.46l-49.47-406.74c-0.47-5.26 2.24-9.49 4.62-12.12a26.93 26.93 0 0 1 19.42-8.6h458.78a28.68 28.68 0 0 0 27.88-22l22-93a12.05 12.05 0 0 1 11.47-8.82h213.2a26.23 26.23 0 0 1 19 8.25 17.47 17.47 0 0 1 5 13.15l-22.69 243.13a28.68 28.68 0 1 0 57.11 5.29l22.69-243.31v-0.31c1.74-20.79-5.34-40.97-19.91-56.8z",
      "M791.81 523.81c-92.41 0-167.33 75-167.33 167.43s74.92 167.43 167.33 167.43 167.33-75 167.33-167.43-74.92-167.43-167.33-167.43z m0 294.27a126.84 126.84 0 1 1 126.77-126.84 126.8 126.8 0 0 1-126.77 126.85z",
      "M850.8 634.19l-87.57 88.24-34.4-38.7a12.72 12.72 0 0 0-17.65 0 12.58 12.58 0 0 0 0 17.8l46.34 46.69a12.37 12.37 0 0 0 9.71 3.61 12.19 12.19 0 0 0 9.69-3.61L872.45 652a12.6 12.6 0 0 0 0-17.8c-4.72-4.77-12.93-4.77-21.65-0.01zM142.9 222.18h359.4a28.68 28.68 0 1 0 0-57.35H142.9a28.68 28.68 0 0 0 0 57.35z",
    ],
  },
  {
    key: "deploy",
    labelKey: "pages.home.stages.deploy",
    paths: [
      "M560.472 76.344l304.58 175.85a96.944 96.944 0 0 1 48.473 83.956v351.7a96.944 96.944 0 0 1-48.472 83.956l-304.581 175.85a96.944 96.944 0 0 1-96.944 0l-304.58-175.85a96.944 96.944 0 0 1-48.473-83.956v-351.7a96.944 96.944 0 0 1 48.472-83.956l304.581-175.85a96.944 96.944 0 0 1 96.944 0z m-66.944 51.962l-304.58 175.85a36.944 36.944 0 0 0-18.473 31.994v351.7a36.944 36.944 0 0 0 18.472 31.994l304.581 175.85a36.944 36.944 0 0 0 36.944 0l304.58-175.85a36.944 36.944 0 0 0 18.473-31.994v-351.7a36.944 36.944 0 0 0-18.472-31.994l-304.581-175.85a36.944 36.944 0 0 0-36.944 0z m168.686 261.733c14.338-8.303 32.692-3.41 40.995 10.927 8.303 14.338 3.411 32.692-10.927 40.995L542 528.987 542 705.451c0 16.569-13.431 30-30 30-16.569 0-30-13.431-30-30V529.293l-150.282-87.026c-14.338-8.302-19.23-26.657-10.927-40.995 8.303-14.338 26.657-19.23 40.995-10.927l149.95 86.834z",
    ],
  },
  {
    key: "collaborate",
    labelKey: "pages.home.stages.collaborate",
    paths: [
      "M358.595166 45.713203c-0.099999 0-0.199997 0.099999-0.299996 0.099999 13.299821 16.899772 22.1997 37.399495 24.799665 59.899191 0.099999 0 0.299996-0.099999 0.399995-0.099998-2.699964-22.499696-11.499845-42.99942-24.899664-59.899192z m550.592569 594.191981c0.499993 0 0.999987 0 1.49998-0.099999h0.299996c-0.599992 0-1.199984 0.099999-1.799976 0.099999zM1023.986186 520.006802c0 59.199201-42.899421 108.498536-99.398659 118.198405-0.799989 0.099999-1.49998 0.299996-2.299969 0.399994-0.499993 0.099999-0.999987 0.199997-1.49998 0.199998-0.499993 0.099999-1.099985 0.099999-1.599978 0.199997-0.699991 0.099999-1.399981 0.199997-2.19997 0.299996l-2.99996 0.299996h-0.299996c-0.499993 0-0.999987 0.099999-1.49998 0.099998h-1.299982c-0.599992 0-1.199984 0.099999-1.699977 0.099999-1.699977 0.099999-3.299955 0.099999-4.999933 0.099999H901.38784c-14.699802-0.299996-28.699613-3.299955-41.599438-8.399887-44.299402-17.599762-75.698978-60.899178-75.698979-111.498495 0-48.999339 29.299605-91.098771 71.299038-109.69852 7.299901-3.199957 11.199849-11.199849 8.999879-18.799746-4.499939-15.699788-9.899866-31.09958-16.29978-46.199376-20.499723-48.599344-49.999325-92.198756-87.49882-129.69825s-81.198904-66.999096-129.798248-87.598818c-50.299321-21.299713-103.6986-31.999568-158.797857-31.999568-8.399887 0-16.699775 0.299996-24.999662 0.799989-2.099972-16.599776-6.499912-32.899556-12.999825-48.399346-2.099972-4.899934-4.299942-9.59987-6.799908-14.299807 14.7998-1.399981 29.699599-2.099972 44.799395-2.099972 222.99699 0 409.894468 154.597914 459.293802 362.595106 1.299982 5.299928 5.19993 9.699869 10.399859 11.499845 47.799355 15.699788 82.298889 60.799179 82.29889 113.898463z",
      "M909.187735 639.905184c0.499993 0 0.999987 0 1.49998-0.099999h0.299996c-0.599992 0-1.199984 0.099999-1.799976 0.099999z m13.099823-1.299983c-0.499993 0.099999-0.999987 0.199997-1.49998 0.199998-0.499993 0.099999-1.099985 0.099999-1.599978 0.199997-0.699991 0.099999-1.399981 0.199997-2.19997 0.299996l-2.99996 0.299996h-0.299996c-0.499993 0-0.999987 0.099999-1.49998 0.099998h-0.499993c4.399941-0.299996 8.699883-0.699991 12.899826-1.499979v-0.099999c-0.699991 0.299996-1.49998 0.399995-2.299969 0.499993zM899.687863 703.90432C824.388879 864.70215 661.191082 976.000648 471.993635 976.000648c-27.299632 0-53.999271-2.299969-79.99892-6.799908-5.999919-0.999987-11.999838 1.399981-15.599789 6.199916-21.599708 29.099607-55.999244 47.999352-94.89872 48.499345-65.999109 0.799989-121.398362-53.799274-121.49836-119.898381 0-14.09981 2.399968-27.499629 6.799908-40.099459 7.299901-20.799719 20.199727-38.899475 36.899502-52.699289 20.699721-17.099769 47.299362-27.39963 76.298971-27.39963 57.999217 0 106.498563 41.199444 117.598412 95.998704 0.699991 3.299955 1.199984 8.499885 1.599979 13.299821 0.599992 7.3999 6.299915 13.499818 13.599816 14.499804 19.499737 2.799962 39.199471 4.199943 59.199201 4.199943 55.099256 0 108.498536-10.799854 158.797857-31.999568 48.599344-20.499723 92.198756-49.999325 129.69825-87.498819 30.199592-30.199592 55.199255-64.49913 74.498994-101.998623 20.599722 8.499885 42.299429 13.099823 64.699127 13.599816zM383.994823 121.712177c-0.899988 64.899124-53.999271 117.79841-118.898395 118.298404-24.999663 0.199997-48.299348-7.199903-67.599088-20.099729-6.399914-4.299942-14.999798-3.399954-20.399725 2.099972-0.799989 0.799989-1.399981 1.49998-1.899974 1.999973-33.599547 35.499521-60.199188 76.29897-79.198931 121.198364-21.299713 50.299321-31.999568 103.6986-31.999568 158.797857s10.799854 108.498536 31.999568 158.797857c15.799787 37.399495 36.899502 71.89903 62.99915 102.99861-2.99996 2.599965-5.89992 5.299928-8.699883 8.09989-12.799827 12.799827-23.399684 27.099634-31.89957 42.799423C44.699402 733.403922 0.000005 623.9054 0.000005 504.007018c0-132.898206 54.899259-252.996586 143.298066-338.795428 4.099945-3.999946 5.799922-9.799868 4.399941-15.299793-2.599965-9.999865-3.899947-20.599722-3.799949-31.399576C144.798051 52.413113 199.69731-0.986167 265.896417 0.01382c37.499494 0.599992 70.799044 18.399752 92.398753 45.799382 13.299821 16.899772 22.1997 37.399495 24.799665 59.899191 0.699991 5.19993 0.999987 10.499858 0.899988 15.999784z",
    ],
  },
];
</script>

<style scoped src="./WibebareShowcase.css"></style>
