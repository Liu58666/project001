<template>
  <div class="home-page">
    <Main />
    <DailOverview />
    <Second />
    <NemoOneShowcase />
    <CompanyOrbitTransition />
    <Third home-handoff />
    <End />
  </div>
</template>

<script setup>
import Main from '@/page_components/Main.vue'
import DailOverview from '@/page_components/DailOverview.vue'
import Second from '@/page_components/Second.vue'
import NemoOneShowcase from '@/page_components/NemoOneShowcase.vue'
import CompanyOrbitTransition from '@/page_components/CompanyOrbitTransition.vue'
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
