<template>
  <Transition name="detail-panel" mode="out-in">
    <article v-if="topic" :key="topic.id" class="detail" :aria-labelledby="`topic-${topic.id}`">
      <div class="detail-heading">
        <div>
          <p class="detail-index">{{ topic.index }} / {{ total }}</p>
          <h3 :id="`topic-${topic.id}`">{{ topic.title }}</h3>
        </div>
        <button class="detail-close" type="button" :aria-label="closeLabel" @click="$emit('close')">
          <span></span>
          <span></span>
        </button>
      </div>

      <p class="detail-summary">{{ topic.summary }}</p>

      <ul class="detail-points">
        <li v-for="point in topic.points" :key="point">{{ point }}</li>
      </ul>
    </article>
  </Transition>
</template>

<script setup>
defineProps({
  topic: {
    type: Object,
    default: null,
  },
  total: {
    type: Number,
    default: 4,
  },
  closeLabel: {
    type: String,
    default: 'Close',
  },
})

defineEmits(['close'])
</script>

<style scoped>
.detail {
  width: min(100%, 760px);
  padding: clamp(28px, 5vw, 56px);
  border: 1px solid rgba(250, 249, 245, 0.24);
  border-radius: 24px;
  background: rgba(250, 249, 245, 0.08);
  color: #faf9f5;
  backdrop-filter: blur(18px);
}

.detail-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.detail-index {
  margin: 0 0 14px;
  color: rgba(250, 249, 245, 0.55);
  font-size: 12px;
  letter-spacing: 0.16em;
}

h3 {
  margin: 0;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(36px, 6vw, 64px);
  font-weight: 400;
  line-height: 1;
  letter-spacing: -0.04em;
}

.detail-close {
  position: relative;
  width: 44px;
  height: 44px;
  flex: 0 0 44px;
  border: 1px solid rgba(250, 249, 245, 0.28);
  border-radius: 50%;
  background: transparent;
  cursor: pointer;
}

.detail-close span {
  position: absolute;
  top: 21px;
  left: 13px;
  width: 18px;
  height: 1px;
  background: #faf9f5;
}

.detail-close span:first-child {
  transform: rotate(45deg);
}

.detail-close span:last-child {
  transform: rotate(-45deg);
}

.detail-summary {
  max-width: 640px;
  margin: 36px 0 30px;
  color: rgba(250, 249, 245, 0.8);
  font-size: clamp(17px, 2vw, 21px);
  line-height: 1.65;
}

.detail-points {
  display: grid;
  margin: 0;
  padding: 0;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0;
  list-style: none;
  border-top: 1px solid rgba(250, 249, 245, 0.18);
}

.detail-points li {
  padding: 18px 18px 18px 0;
  border-bottom: 1px solid rgba(250, 249, 245, 0.18);
  color: rgba(250, 249, 245, 0.72);
  font-size: 14px;
  line-height: 1.5;
}

.detail-points li:nth-child(odd) {
  border-right: 1px solid rgba(250, 249, 245, 0.18);
}

.detail-points li:nth-child(even) {
  padding-left: 18px;
}

.detail-panel-enter-active,
.detail-panel-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.detail-panel-enter-from,
.detail-panel-leave-to {
  opacity: 0;
  transform: translateY(18px);
}

@media (max-width: 600px) {
  .detail {
    padding: 26px 22px;
    border-radius: 18px;
  }

  .detail-summary {
    margin-top: 28px;
  }

  .detail-points {
    grid-template-columns: minmax(0, 1fr);
  }

  .detail-points li,
  .detail-points li:nth-child(even) {
    padding: 16px 0;
    border-right: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .detail-panel-enter-active,
  .detail-panel-leave-active {
    transition: none;
  }
}
</style>
