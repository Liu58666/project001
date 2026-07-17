<template>
  <div class="home-page">
    <Main />
    <DailOverview />
    <TechnologyNemoTransition />
    <AIOSShowcase />
    <Third home-handoff />
    <End />
  </div>
</template>

<script setup>
import Main from '@/page_components/Main.vue'
import DailOverview from '@/page_components/DailOverview.vue'
import TechnologyNemoTransition from '@/page_components/TechnologyNemoTransition.vue'
import AIOSShowcase from '@/page_components/AIOSShowcase.vue'
import Third from '@/page_components/Third.vue'
import End from '@/page_components/End.vue'
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-width: 0;
  overflow: hidden;
  overflow: clip;
}
</style>
