<template>
  <form class="np" @submit.prevent="emit('submit')">
    <header class="np__header">
      <div class="np__title-wrap">
        <div class="np__eyebrow">{{ title }}</div>
        <div class="np__meta">
          <span class="np__meta-item">{{ metaLeft }}</span>
          <span class="np__dot" aria-hidden="true"></span>
          <span class="np__meta-item">{{ metaRight }}</span>
        </div>
      </div>
    </header>

    <section class="np__section">
      <div class="np__section-title">{{ sectionBasics }}</div>

      <div class="np__grid">
        <label class="np__field np__field--span2">
          <span class="np__label">{{ labels.slug }}</span>
          <input
            class="np__control"
            v-model.trim="model.slug"
            autocomplete="off"
            spellcheck="false"
            inputmode="url"
            placeholder="openai-appoints-denise-dresser"
            required
          />
          <span class="np__hint">{{ hints.slug }}</span>
        </label>

        <label class="np__field">
          <span class="np__label">{{ labels.category }}</span>
          <select class="np__control" v-model="model.category" required>
            <option v-for="c in categories" :key="c.value" :value="c.value">
              {{ c.label }}
            </option>
          </select>
          <span class="np__hint">{{ hints.category }}</span>
        </label>

        <label class="np__field">
          <span class="np__label">{{ labels.author }}</span>
          <input class="np__control" v-model.trim="model.author" autocomplete="organization" placeholder="Company" />
          <span class="np__hint">{{ hints.author }}</span>
        </label>

        <label class="np__field np__field--span2">
          <span class="np__label">{{ labels.title }}</span>
          <input class="np__control" v-model.trim="model.title" autocomplete="off" placeholder="Write the headline…" required />
        </label>

        <label class="np__field np__field--span2">
          <span class="np__label">{{ labels.subtitle }}</span>
          <input class="np__control" v-model.trim="model.subtitle" autocomplete="off" placeholder="Optional short dek…" />
        </label>
      </div>
    </section>

    <section class="np__section">
      <div class="np__section-title">{{ sectionContent }}</div>

      <label class="np__field np__field--span2">
        <span class="np__label">{{ labels.content }}</span>
        <textarea
          class="np__control np__control--textarea"
          v-model="contentText"
          rows="10"
          :placeholder="hints.content"
          required
        ></textarea>
        <div class="np__footer">
          <div class="np__counter">
            <span class="np__counter-num">{{ paragraphCount }}</span>
            <span class="np__counter-label">{{ counterLabel }}</span>
          </div>
          <button class="np__btn np__btn--ghost" type="button" :disabled="disabled" @click="emit('reset')">
            {{ resetText }}
          </button>
        </div>
      </label>
    </section>

    <div class="np__actions">
      <button class="np__btn np__btn--primary" type="submit" :disabled="disabled">
        <span class="np__btn-text">{{ submitText }}</span>
      </button>
    </div>
  </form>
</template>

<script setup>
import { computed } from 'vue'

const model = defineModel('model', { type: Object, required: true })
const contentText = defineModel('contentText', { type: String, required: true })

const props = defineProps({
  disabled: { type: Boolean, default: false },
  title: { type: String, default: 'Publish News' },
  metaLeft: { type: String, default: 'Monochrome editor' },
  metaRight: { type: String, default: 'Auto date' },
  sectionBasics: { type: String, default: 'Basics' },
  sectionContent: { type: String, default: 'Content' },
  counterLabel: { type: String, default: 'paragraphs' },
  submitText: { type: String, default: 'Publish' },
  resetText: { type: String, default: 'Reset' },
  labels: {
    type: Object,
    default: () => ({
      slug: 'Slug',
      category: 'Category',
      title: 'Title',
      subtitle: 'Subtitle',
      author: 'Author',
      content: 'Content',
    }),
  },
  hints: {
    type: Object,
    default: () => ({
      slug: 'Lowercase words separated by dashes.',
      category: 'Choose one of the fixed categories.',
      author: 'Optional.',
      content: 'One paragraph per line.',
    }),
  },
  categories: {
    type: Array,
    default: () => [
      { value: 'Alliance', label: 'Alliance' },
      { value: 'Milestone', label: 'Milestone' },
      { value: 'Partnership', label: 'Partnership' },
      { value: 'News', label: 'New Tools' },
    ],
  },
})

const emit = defineEmits(['submit', 'reset'])

const paragraphCount = computed(() => {
  return String(contentText.value || '')
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean).length
})
</script>

<style scoped>
.np {
  --ink: #0b0f19;
  --muted: rgba(15, 23, 42, 0.62);
  --muted2: rgba(15, 23, 42, 0.48);
  --line: rgba(15, 23, 42, 0.12);
  --card: rgba(255, 255, 255, 0.78);
  --card2: rgba(255, 255, 255, 0.92);
  --shadow: 0 22px 60px rgba(0, 0, 0, 0.08);

  width: 100%;
}

.np__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 2px 0 18px;
  border-bottom: 1px solid var(--line);
  margin-bottom: 18px;
}

.np__eyebrow {
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--ink);
}

.np__meta {
  margin-top: 10px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: var(--muted);
  font-size: 13px;
}

.np__dot {
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.35);
}

.np__section {
  margin-top: 18px;
  padding: 16px 16px;
  border: 1px solid var(--line);
  border-radius: 18px;
  background: var(--card);
  box-shadow: var(--shadow);
}

.np__section-title {
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--muted2);
  margin-bottom: 14px;
}

.np__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px 12px;
}

.np__field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.np__field--span2 {
  grid-column: 1 / -1;
}

.np__label {
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}

.np__control {
  height: 46px;
  width: 100%;
  border-radius: 14px;
  border: 1px solid rgba(15, 23, 42, 0.14);
  background: var(--card2);
  padding: 0 14px;
  font-size: 14px;
  color: var(--ink);
  outline: none;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.np__control--textarea {
  height: auto;
  padding: 12px 14px;
  resize: vertical;
  line-height: 1.65;
}

.np__control::placeholder {
  color: rgba(15, 23, 42, 0.40);
}

.np__control:focus {
  border-color: rgba(0, 0, 0, 0.65);
  box-shadow: 0 0 0 4px rgba(0, 0, 0, 0.12);
}

.np__hint {
  font-size: 12px;
  color: rgba(15, 23, 42, 0.52);
}

.np__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 10px;
}

.np__counter {
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
  color: rgba(15, 23, 42, 0.62);
}

.np__counter-num {
  font-weight: 900;
  color: rgba(15, 23, 42, 0.86);
}

.np__counter-label {
  font-size: 12px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.np__actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.np__btn {
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

.np__btn--primary {
  background: #000000;
  border-color: #000000;
  color: #ffffff;
  box-shadow: 0 14px 35px rgba(0, 0, 0, 0.12);
}

.np__btn--primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.14);
}

.np__btn--ghost:hover {
  transform: translateY(-1px);
  background: rgba(15, 23, 42, 0.06);
  border-color: rgba(15, 23, 42, 0.18);
}

.np__btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

</style>


