<template>
  <section class="join-page">
    <div class="join-container">
      <!-- 页面标题 -->
      <header class="join-header">
        <h1 class="join-title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '80ms' }">
          {{ isZh ? '加入 DAIL Tech' : 'Join DAIL Tech' }}
        </h1>
        <p class="join-subtitle reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '140ms' }">
          {{ isZh ? '与我们一起定义 AI 的未来' : 'Shape the future of AI with us' }}
        </p>
      </header>

      <!-- 介绍区域 -->
      <div class="intro-section reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '200ms' }">
        <p>{{ isZh 
          ? 'DAIL Tech 正在寻找充满热情的人才，与我们一起构建下一代 AI 解决方案。无论你是技术专家还是创意思考者，这里都有属于你的舞台。' 
          : 'DAIL Tech is looking for passionate talents to build next-generation AI solutions together. Whether you\'re a tech expert or creative thinker, there\'s a stage for you here.' 
        }}</p>
      </div>

      <!-- 招聘岗位 -->
      <div class="positions-section">
        <h2 class="section-title reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '260ms' }">
          {{ isZh ? '开放岗位' : 'Open Positions' }}
        </h2>

        <div class="positions-grid">
          <div class="position-card reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '320ms' }">
            <div class="position-icon">
              <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="3"/>
                <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/>
              </svg>
            </div>
            <div class="position-content">
              <h3>{{ isZh ? 'AI 智能体开发工程师' : 'AI Agent Developer' }}</h3>
              <p>{{ isZh 
                ? '负责设计和开发基于大语言模型的智能体系统，构建多智能体协作框架，实现复杂业务场景的自动化解决方案。' 
                : 'Design and develop LLM-based agent systems, build multi-agent collaboration frameworks, and implement automated solutions for complex business scenarios.' 
              }}</p>
              <div class="position-tags">
                <span>LLM</span>
                <span>Agent</span>
                <span>Python</span>
              </div>
            </div>
          </div>

          <div class="position-card reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '380ms' }">
            <div class="position-icon">
              <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5">
                <polyline points="16 18 22 12 16 6"/>
                <polyline points="8 6 2 12 8 18"/>
              </svg>
            </div>
            <div class="position-content">
              <h3>{{ isZh ? '全栈开发工程师' : 'Full-Stack Developer' }}</h3>
              <p>{{ isZh 
                ? '参与 AI 产品的前后端开发，使用 Vue/React 构建现代化用户界面，使用 Python/Node.js 开发高性能后端服务。' 
                : 'Participate in AI product development, build modern UIs with Vue/React, and develop high-performance backend services with Python/Node.js.' 
              }}</p>
              <div class="position-tags">
                <span>Vue</span>
                <span>Node.js</span>
                <span>Python</span>
              </div>
            </div>
          </div>

          <div class="position-card reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '440ms' }">
            <div class="position-icon">
              <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 2a4 4 0 0 1 4 4v2a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"/>
                <path d="M6 10v1a6 6 0 0 0 12 0v-1"/>
                <path d="M12 17v5"/>
                <path d="M8 22h8"/>
              </svg>
            </div>
            <div class="position-content">
              <h3>{{ isZh ? 'AI 模型训练工程师' : 'AI Training Engineer' }}</h3>
              <p>{{ isZh 
                ? '负责大语言模型的微调、RLHF 训练、模型评估与优化，探索前沿的模型训练技术，提升模型在垂直领域的表现。' 
                : 'Responsible for LLM fine-tuning, RLHF training, model evaluation and optimization. Explore cutting-edge training techniques to improve model performance in vertical domains.' 
              }}</p>
              <div class="position-tags">
                <span>PyTorch</span>
                <span>RLHF</span>
                <span>Fine-tuning</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 福利待遇 -->
      <div class="benefits-section reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '500ms' }">
        <h2 class="section-title">{{ isZh ? '为什么选择我们' : 'Why Join Us' }}</h2>
        <div class="benefits-grid">
          <div class="benefit-card">
            <div class="benefit-icon">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
              </svg>
            </div>
            <h4>{{ isZh ? '前沿技术栈' : 'Cutting-edge Tech' }}</h4>
            <p>{{ isZh ? '接触最新的 AI 技术与工具' : 'Work with the latest AI technologies' }}</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5">
                <line x1="12" y1="1" x2="12" y2="23"/>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
            </div>
            <h4>{{ isZh ? '有竞争力的薪酬' : 'Competitive Pay' }}</h4>
            <p>{{ isZh ? '行业领先的薪资待遇' : 'Industry-leading compensation' }}</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
            </div>
            <h4>{{ isZh ? '股权期权激励' : 'Equity & Options' }}</h4>
            <p>{{ isZh ? '与公司共同成长的机会' : 'Grow together with the company' }}</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
                <polyline points="17 6 23 6 23 12"/>
              </svg>
            </div>
            <h4>{{ isZh ? '快速成长空间' : 'Growth Opportunities' }}</h4>
            <p>{{ isZh ? '清晰的职业发展路径' : 'Clear career development path' }}</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <h4>{{ isZh ? '弹性工作制度' : 'Flexible Work' }}</h4>
            <p>{{ isZh ? '灵活的工作时间安排' : 'Flexible working hours' }}</p>
          </div>
        </div>
      </div>

      <!-- 联系方式 -->
      <div class="contact-section reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '560ms' }">
        <div class="contact-card">
          <div class="contact-left">
            <h3>{{ isZh ? '有意向？联系我们' : 'Interested? Contact Us' }}</h3>
            <p>{{ isZh ? '发送简历至以下邮箱，我们会尽快与你联系' : 'Send your resume to the email below, we\'ll get back to you soon' }}</p>
          </div>
          <div class="contact-right">
            <a href="mailto:912527541@qq.com" class="contact-email">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
              912527541@qq.com
            </a>
            <button class="copy-btn" @click="copyEmail">
              {{ emailCopied ? (isZh ? '已复制!' : 'Copied!') : (isZh ? '复制邮箱' : 'Copy') }}
            </button>
          </div>
        </div>
      </div>

      <!-- 返回按钮 -->
      <div class="back-section reveal" :class="{ 'is-in': pageEnter }" :style="{ '--d': '620ms' }">
        <button class="back-btn" @click="router.push('/career')">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          {{ isZh ? '返回' : 'Back' }}
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18nStore } from '@/stores/i18n'

const router = useRouter()
const i18n = useI18nStore()
const isZh = computed(() => i18n.locale === 'zh')
const pageEnter = ref(false)
const emailCopied = ref(false)

function copyEmail() {
  navigator.clipboard.writeText('912527541@qq.com').then(() => {
    emailCopied.value = true
    setTimeout(() => { emailCopied.value = false }, 2000)
  }).catch(() => {
    const input = document.createElement('input')
    input.value = '912527541@qq.com'
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    emailCopied.value = true
    setTimeout(() => { emailCopied.value = false }, 2000)
  })
}

onMounted(() => {
  requestAnimationFrame(() => { pageEnter.value = true })
})
</script>

<style scoped>
.join-page {
  background: #fbfbfb;
  padding: 120px 24px 80px;
  min-height: 100vh;
}

.join-container {
  max-width: 900px;
  margin: 0 auto;
}

/* 标题 */
.join-header {
  text-align: center;
  margin-bottom: 48px;
}

.join-title {
  font-size: 56px;
  line-height: 1.1;
  letter-spacing: -0.03em;
  font-weight: 600;
  color: #0b0f19;
  margin: 0 0 16px;
}

.join-subtitle {
  font-size: 18px;
  color: #6b7280;
  margin: 0;
}

/* 动画 */
.reveal {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), 
              transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: var(--d, 0ms);
}

.reveal.is-in {
  opacity: 1;
  transform: translateY(0);
}

/* 介绍 */
.intro-section {
  text-align: center;
  margin-bottom: 64px;
}

.intro-section p {
  font-size: 16px;
  line-height: 1.8;
  color: #4b5563;
  max-width: 700px;
  margin: 0 auto;
}

/* 区块标题 */
.section-title {
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #9ca3af;
  margin: 0 0 24px;
}

/* 岗位区域 */
.positions-section {
  margin-bottom: 64px;
}

.positions-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.position-card {
  display: flex;
  gap: 24px;
  padding: 28px 32px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  cursor: pointer;
}

.position-card:hover {
  background: #0b0f19;
  border-color: #0b0f19;
  box-shadow: 0 16px 40px rgba(11, 15, 25, 0.2);
  transform: translateY(-4px);
}

.position-card:hover .position-icon {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.position-card:hover .position-content h3 {
  color: #fff;
}

.position-card:hover .position-content p {
  color: rgba(255, 255, 255, 0.7);
}

.position-card:hover .position-tags span {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.position-icon {
  width: 56px;
  height: 56px;
  background: #f9fafb;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4b5563;
  flex-shrink: 0;
  transition: all 0.3s ease;
  margin-top: 25px;
}

.position-content {
  flex: 1;
}

.position-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #0b0f19;
  margin: 0 0 8px;
  transition: color 0.3s ease;
}

.position-content p {
  font-size: 14px;
  line-height: 1.7;
  color: #6b7280;
  margin: 0 0 12px;
  transition: color 0.3s ease;
}

.position-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.position-tags span {
  padding: 4px 12px;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.3s ease;
}

/* 福利区域 */
.benefits-section {
  margin-bottom: 64px;
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.benefit-card {
  padding: 24px 20px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  text-align: center;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  cursor: pointer;
}

.benefit-card:hover {
  background: #0b0f19;
  border-color: #0b0f19;
  box-shadow: 0 12px 32px rgba(11, 15, 25, 0.18);
  transform: translateY(-4px);
}

.benefit-card:hover .benefit-icon {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.benefit-card:hover h4 {
  color: #fff;
}

.benefit-card:hover p {
  color: rgba(255, 255, 255, 0.6);
}

.benefit-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  background: #f9fafb;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4b5563;
  transition: all 0.3s ease;
}

.benefit-card h4 {
  font-size: 14px;
  font-weight: 600;
  color: #0b0f19;
  margin: 0 0 6px;
  transition: color 0.3s ease;
}

.benefit-card p {
  font-size: 12px;
  color: #9ca3af;
  margin: 0;
  transition: color 0.3s ease;
}

/* 联系区域 */
.contact-section {
  margin-bottom: 48px;
}

.contact-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32px 40px;
  background: #0b0f19;
  border-radius: 20px;
  color: #fff;
}

.contact-left h3 {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 6px;
}

.contact-left p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.contact-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.contact-email {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 500;
  color: #fff;
  text-decoration: none;
  transition: opacity 0.2s;
}

.contact-email:hover {
  opacity: 0.8;
}

.copy-btn {
  padding: 10px 20px;
  background: #fff;
  color: #0b0f19;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.copy-btn:hover {
  transform: scale(1.05);
}

/* 返回按钮 */
.back-section {
  text-align: center;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 32px;
  background: transparent;
  color: #6b7280;
  border: none;
  border-radius: 100px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
}

.back-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 100px;
  border: 1.5px solid #e5e7eb;
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.back-btn svg {
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.back-btn:hover {
  color: #fff;
  background: #0b0f19;
  padding-left: 28px;
  padding-right: 36px;
}

.back-btn:hover::before {
  border-color: #0b0f19;
}

.back-btn:hover svg {
  transform: translateX(-4px);
}

@media (max-width: 900px) {
  .join-page { padding: 104px 20px 64px; }
  .join-header { margin-bottom: 36px; }
  .join-title { font-size: clamp(40px, 11vw, 52px); }
  .join-subtitle { font-size: 16px; }
  .intro-section, .positions-section, .benefits-section { margin-bottom: 48px; }
  .position-card { gap: 16px; padding: 22px 18px; }
  .position-icon { width: 48px; height: 48px; margin-top: 0; }
  .benefits-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
  .benefit-card { padding: 20px 12px; }
  .contact-card { align-items: stretch; flex-direction: column; gap: 24px; padding: 24px 20px; }
  .contact-right { align-items: stretch; flex-direction: column; gap: 12px; }
  .contact-email { min-width: 0; font-size: 14px; overflow-wrap: anywhere; }
  .copy-btn { min-height: 44px; }
}

@media (max-width: 480px) {
  .position-card { flex-direction: column; }
  .benefits-grid { grid-template-columns: minmax(0, 1fr); }
}
</style>
