<template>
  <div class="home-page">
    <Main />
    <Second />
    <Third />
    <End />
  </div>
</template>

<script setup>
import Main from '@/page_components/Main.vue'
import Second from '@/page_components/Second.vue'
import Third from '@/page_components/Third.vue'
import End from '@/page_components/End.vue'
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
}
</style>

