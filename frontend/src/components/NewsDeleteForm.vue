<template>
  <form class="nd" @submit.prevent="emit('submit')">
    <header class="nd__header">
      <div class="nd__eyebrow">{{ title }}</div>
      <div class="nd__meta">
        <span class="nd__meta-item">{{ metaLeft }}</span>
        <span class="nd__dot" aria-hidden="true"></span>
        <span class="nd__meta-item">{{ metaRight }}</span>
      </div>
    </header>

    <section class="nd__section">
      <div class="nd__section-title">{{ sectionTitle }}</div>

      <label class="nd__field">
        <span class="nd__label">{{ labels.id }}</span>
        <input
          class="nd__control"
          v-model.trim="newsId"
          inputmode="numeric"
          autocomplete="off"
          placeholder="9"
          required
        />
        <span class="nd__hint">{{ hints.id }}</span>
      </label>

      <label class="nd__confirm">
        <input class="nd__checkbox" type="checkbox" v-model="confirm" />
        <span class="nd__confirm-text">{{ confirmText }}</span>
      </label>
    </section>

    <div class="nd__actions">
      <button class="nd__btn nd__btn--ghost" type="button" :disabled="disabled" @click="emit('reset')">
        {{ resetText }}
      </button>
      <button class="nd__btn nd__btn--danger" type="submit" :disabled="disabled || !confirm || !newsId">
        {{ submitText }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue'

const newsId = defineModel('newsId', { type: String, required: true })

const props = defineProps({
  disabled: { type: Boolean, default: false },
  title: { type: String, default: 'Delete News' },
  metaLeft: { type: String, default: 'Irreversible' },
  metaRight: { type: String, default: 'By id' },
  sectionTitle: { type: String, default: 'Target' },
  confirmText: { type: String, default: 'I understand this cannot be undone.' },
  submitText: { type: String, default: 'Delete' },
  resetText: { type: String, default: 'Reset' },
  labels: {
    type: Object,
    default: () => ({ id: 'News id' }),
  },
  hints: {
    type: Object,
    default: () => ({ id: 'Numeric id from backend response.' }),
  },
})

const emit = defineEmits(['submit', 'reset'])

const confirm = ref(false)

// Reset confirm when id changes (avoid accidental delete after changing target)
watch(newsId, () => {
  confirm.value = false
})
</script>

<style scoped>
.nd {
  --ink: #0b0f19;
  --muted: rgba(15, 23, 42, 0.62);
  --muted2: rgba(15, 23, 42, 0.48);
  --line: rgba(15, 23, 42, 0.12);
  --card: rgba(255, 255, 255, 0.78);
  --card2: rgba(255, 255, 255, 0.92);
  --shadow: 0 22px 60px rgba(0, 0, 0, 0.08);
}

.nd__header {
  padding: 2px 0 18px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 18px;
}

.nd__eyebrow {
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--ink);
}

.nd__meta {
  margin-top: 10px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--muted);
  font-size: 13px;
}

.nd__dot {
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.35);
}

.nd__section {
  margin-top: 18px;
  padding: 16px 16px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--card);
  box-shadow: var(--shadow);
}

.nd__section-title {
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--muted2);
  margin-bottom: 14px;
}

.nd__field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nd__label {
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}

.nd__control {
  height: 46px;
  width: 100%;
  border-radius: 14px;
  border: 1px solid rgba(15, 23, 42, 0.14);
  background: var(--card2);
  padding: 0 14px;
  font-size: 14px;
  color: var(--ink);
  outline: none;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.nd__control:focus {
  border-color: rgba(0, 0, 0, 0.65);
  box-shadow: 0 0 0 4px rgba(0, 0, 0, 0.12);
}

.nd__hint {
  font-size: 12px;
  color: rgba(15, 23, 42, 0.52);
}

.nd__confirm {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid rgba(15, 23, 42, 0.10);
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.nd__checkbox {
  margin-top: 2px;
  width: 16px;
  height: 16px;
  accent-color: #000000;
}

.nd__confirm-text {
  font-size: 13px;
  line-height: 1.6;
  color: rgba(15, 23, 42, 0.72);
}

.nd__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 18px;
}

.nd__btn {
  height: 42px;
  padding: 0 16px;
  border-radius: 999px;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  border: 1px solid rgba(15, 23, 42, 0.14);
  background: transparent;
  color: rgba(15, 23, 42, 0.86);
  transition: transform 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease, color 0.15s ease,
    border-color 0.15s ease;
}

.nd__btn--ghost:hover {
  transform: translateY(-1px);
  background: rgba(15, 23, 42, 0.06);
  border-color: rgba(15, 23, 42, 0.18);
}

.nd__btn--danger {
  background: #000000;
  border-color: #000000;
  color: #ffffff;
  box-shadow: 0 14px 35px rgba(0, 0, 0, 0.12);
}

.nd__btn--danger:hover {
  transform: translateY(-1px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.14);
}

.nd__btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

@media (max-width: 640px) {
  .nd__actions { flex-direction: column; align-items: stretch; }
  .nd__btn { width: 100%; min-height: 44px; }
}
</style>


