<template>
    <section class="user-page">
      <!-- 背景视频（全屏） -->
      <div class="bg-layer" aria-hidden="true">
        <video class="bg-video" autoplay loop muted playsinline :src="bgVideo"></video>
        <div class="bg-mask"></div>
      </div>

      <!-- 右侧背景视频 -->
      <!-- <div class="bg-layer-right" aria-hidden="true">
        <video class="bg-video-right" autoplay loop muted playsinline :src="bgVideoRight"></video>
        <div class="bg-mask-right"></div>
      </div> -->
  
      <!-- 主体布局：左侧分选栏 + 右侧内容 -->
      <div class="layout">
        <!-- 汉堡菜单按钮 -->
        <button 
          class="menu-toggle" 
          :class="{ 'is-hidden': isSidebarOpen }"
          type="button" 
          @click="toggleSidebar"
          :aria-label="i18n.locale === 'zh' ? '打开菜单' : 'Open menu'"
        >
          <span class="menu-toggle-bar"></span>
          <span class="menu-toggle-bar"></span>
          <span class="menu-toggle-bar"></span>
        </button>

        <!-- 遮罩层 -->
        <div 
          class="sidebar-overlay" 
          :class="{ 'is-visible': isSidebarOpen }"
          @click="closeSidebar"
        ></div>

        <!-- Sidebar -->
        <aside class="sidebar" :class="{ 'is-open': isSidebarOpen }">
  
          <nav class="nav" :class="{ 'nav--ready': indicatorReady }" :aria-label="t('user.navAria')" ref="navRef">
            <!-- 弹性滑动指示器 -->
            <div 
              class="nav-indicator" 
              :class="{ 'nav-indicator--ready': indicatorReady }"
              :style="indicatorStyle"
            ></div>
            
            <button
              class="nav-item float-in"
              :style="{ '--d': '80ms' }"
              :class="{ active: activeTab === 'profile', animate: isMounted }"
              @click="switchTab('profile')"
              type="button"
              ref="navItemProfile"
            >
              <span class="nav-text">{{ t('user.navProfile') }}</span>
              <span class="nav-desc">{{ t('user.navProfileDesc') }}</span>
            </button>
  
            <button
              class="nav-item float-in"
              :style="{ '--d': '140ms' }"
              :class="{ active: activeTab === 'dominate', animate: isMounted }"
              @click="switchTab('dominate')"
              type="button"
              ref="navItemDominate"
            >
              <span class="nav-text">{{ t('user.navDominate') }}</span>
              <span class="nav-desc">{{ t('user.navDominateDesc') }}</span>
            </button>

            <button
              v-if="canPublishNews"
              class="nav-item float-in"
              :style="{ '--d': '200ms' }"
              :class="{ active: activeTab === 'news', animate: isMounted }"
              type="button"
              @click="switchTab('news')"
              ref="navItemNews"
            >
              <span class="nav-text">{{ t('user.navNews') }}</span>
              <span class="nav-desc">{{ t('user.navNewsDesc') }}</span>
            </button>

            <button
              class="nav-item float-in"
              :style="{ '--d': '260ms' }"
              :class="{ active: activeTab === 'messages', animate: isMounted }"
              type="button"
              @click="switchTab('messages'); loadMessages()"
              ref="navItemMessages"
            >
              <span class="nav-content">
                <span class="nav-text">{{ t('messages.navMessages') }}</span>
                <span class="nav-desc">{{ t('messages.navMessagesDesc') }}</span>
              </span>
              <span v-if="unreadCount > 0" class="nav-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
            </button>
          </nav>
  
          <div class="sidebar-footer">
            <!-- Stepper（替换原 meta 卡片） -->
            <div class="stepper-wrapper float-in" :style="{ '--d': '220ms' }" :class="{ animate: isMounted }">
              <div class="stepper">
                <!-- 1: Account -->
                <div class="stepper-step is-done float-in" :style="{ '--d': '240ms' }" :class="{ animate: isMounted }">
                  <div class="stepper-circle" aria-hidden="true">
                    <svg viewBox="0 0 16 16" fill="currentColor" width="14" height="14" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425z"></path>
                    </svg>
                  </div>
                  <div class="stepper-line"></div>
                  <div class="stepper-content">
                    <div class="stepper-title">{{ t('user.stepAccount') }}</div>
                    <div class="stepper-sub">{{ displayName }}</div>
                  </div>
                </div>

                <!-- 2: Profile Updated -->
                <div class="stepper-step float-in" :style="{ '--d': '300ms' }" :class="{ animate: isMounted, 'is-done': hasUpdatedProfile, 'is-pending': !hasUpdatedProfile }">
                  <div class="stepper-circle" aria-hidden="true">
                    <svg v-if="hasUpdatedProfile" viewBox="0 0 16 16" fill="currentColor" width="14" height="14" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425z"></path>
                    </svg>
                    <span v-else>2</span>
                  </div>
                  <div class="stepper-line"></div>
                  <div class="stepper-content">
                    <div class="stepper-title">{{ t('user.stepProgress') }}</div>
                    <div class="stepper-sub">{{ hasUpdatedProfile ? (i18n.locale === 'zh' ? '已更新个人资料' : 'Profile updated') : (i18n.locale === 'zh' ? '请完善个人资料' : 'Please update profile') }}</div>
                  </div>
                </div>

                <!-- 3: Resume Updated -->
                <div class="stepper-step float-in" :style="{ '--d': '360ms' }" :class="{ animate: isMounted, 'is-done': hasUpdatedResume, 'is-pending': !hasUpdatedResume }">
                  <div class="stepper-circle" aria-hidden="true">
                    <svg v-if="hasUpdatedResume" viewBox="0 0 16 16" fill="currentColor" width="14" height="14" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425z"></path>
                    </svg>
                    <span v-else>3</span>
                  </div>
                  <div class="stepper-content">
                    <div class="stepper-title">{{ t('user.stepDominate') }}</div>
                    <div class="stepper-sub">{{ hasUpdatedResume ? (i18n.locale === 'zh' ? '已更新履历' : 'Resume updated') : t('user.navDominateDesc') }}</div>
                  </div>
              </div>
              </div>
            </div>
  
            <button
              class="ghost-btn float-in"
              :style="{ '--d': '420ms' }"
              :class="{ animate: isMounted }"
              type="button"
              @click="handleLogout"
            >
              {{ t('user.logout') }}
            </button>
          </div>
        </aside>
  
        <!-- Content -->
        <main class="content">
          <!-- 顶部标题 -->
          <header class="content-header">
            <h2 class="content-title float-in" :style="{ '--d': '80ms' }" :class="{ animate: contentAnimate }">
              {{ headerText }}
            </h2>
            <p class="content-subtitle float-in" :style="{ '--d': '140ms' }" :class="{ animate: contentAnimate }">
              {{ subtitleText }}
            </p>
          </header>
  
          <!-- Profile -->
          <section v-if="activeTab === 'profile'" class="panel">
            <div class="profile-cards">
              <!-- Profile photo -->
              <label class="info-card info-card--action float-in" :style="{ '--d': '220ms' }" :class="{ animate: contentAnimate, uploading: isUploadingPhoto }">
                <input
                  ref="photoInputRef"
                  type="file"
                  accept="image/jpeg,image/png,image/gif,image/webp"
                  class="sr-only"
                  :disabled="isUploadingPhoto"
                  @change="handlePhotoUpload"
                />
                <div class="info-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h4l2-2h6l2 2h4a2 2 0 0 1 2 2z"/>
                    <circle cx="12" cy="13" r="4"/>
                  </svg>
                </div>

                <div class="info-body">
                  <div class="info-title">{{ t('user.profilePhoto') }}</div>
                  <div class="info-sub">{{ isUploadingPhoto ? (i18n.locale === 'zh' ? '上传中...' : 'Uploading...') : t('user.profilePhotoDesc') }}</div>
                </div>
  
                <div class="avatar" :class="{ 'avatar--has-image': !!userPhotoUrl }" :aria-label="t('user.avatarAria')">
                  <img v-if="userPhotoUrl" :src="userPhotoUrl" alt="avatar" />
                  <span v-else>{{ avatarLetter }}</span>
                  <div class="avatar-overlay">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                      <polyline points="17 8 12 3 7 8"></polyline>
                      <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                  </div>
                </div>
              </label>
  
              <!-- Name -->
              <button
                class="info-card info-card--action float-in"
                :style="{ '--d': '280ms' }"
                :class="{ animate: contentAnimate }"
                type="button"
                @click="openEdit('username')"
                :aria-label="t('user.editNameAria')"
              >
                <div class="info-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 12v7a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h9"/>
                    <path d="M16 3h6v6"/>
                    <path d="M16 9 22 3"/>
                    <circle cx="8" cy="12" r="2"/>
                    <path d="M6 17c.6-1.6 2-2.5 4-2.5s3.4.9 4 2.5"/>
                  </svg>
                </div>
  
                <div class="info-body">
                  <div class="info-title">{{ t('user.name') }}</div>
                  <div class="info-value">{{ profileName }}</div>
                </div>

                <div class="info-action" aria-hidden="true">
                  <span class="info-action-badge" :title="t('user.edit')">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 3 21l.5-4.5L17 3z"></path>
                      <path d="m15 5 4 4"></path>
                    </svg>
                  </span>
                </div>
              </button>

              <!-- Created At (read-only) -->
              <div class="info-card float-in" :style="{ '--d': '310ms' }" :class="{ animate: contentAnimate }">
                <div class="info-icon" aria-hidden="true">
                  <!-- clock -->
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="9"></circle>
                    <path d="M12 7v5l3 2"></path>
                  </svg>
                </div>

                <div class="info-body">
                  <div class="info-title">{{ t('user.createdAt') }}</div>
                  <div class="info-value">{{ createdAtText }}</div>
                </div>
              </div>

              <!-- Updated At (read-only) -->
              <div class="info-card float-in" :style="{ '--d': '325ms' }" :class="{ animate: contentAnimate }">
                <div class="info-icon" aria-hidden="true">
                  <svg viewBox="0 0 1024 1024" width="22" height="22" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path d="M794.7 312.7c-15.6-58.1-49.2-110.5-95.9-149.3C646.5 119.9 580.1 96 512 96c-68.1 0-134.5 23.9-186.8 67.4-46.7 38.8-80.2 91.2-95.8 149.3-92 33.5-154.7 121.5-154.7 220.6 0 62.5 24.5 121.4 68.9 165.8C188 743.5 246.9 768 309.4 768H352v-64h-42.6c-94.1 0-170.7-76.6-170.7-170.7 0-76.8 51.9-144.5 126.1-164.7l19.1-5.2 3.8-19.5C308.8 237.3 403.1 160 512 160c108.8 0 203.2 77.4 224.3 183.9l3.9 19.4 19.1 5.2c74.2 20.2 126.1 87.9 126.1 164.7 0 94.1-76.6 170.7-170.7 170.7H549.5l77.2-77.3-45.2-45.2-109.3 109.3L427 736l45.2 45.3 118.7 118.6 45.2-45.3-86.6-86.6h165.2c62.5 0 121.4-24.5 165.8-68.9s68.9-103.3 68.9-165.8c0-99-62.7-187.1-154.7-220.6z" />
                  </svg>
                </div>

                <div class="info-body">
                  <div class="info-title">{{ t('user.updatedAt') }}</div>
                  <div class="info-value">{{ updatedAtText }}</div>
                </div>
              </div>

              <!-- Birthday -->
              <button
                class="info-card info-card--action float-in"
                :style="{ '--d': '340ms' }"
                :class="{ animate: contentAnimate }"
                type="button"
                @click="openEdit('birthday')"
                :aria-label="birthdayRaw ? t('user.editBirthdayAria') : t('user.setBirthdayAria')"
              >
                <div class="info-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21H4v-7a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4z"/>
                    <path d="M4 17c1.2 0 1.2 1 2.4 1s1.2-1 2.4-1 1.2 1 2.4 1 1.2-1 2.4-1 1.2 1 2.4 1 1.2-1 2.4-1"/>
                    <path d="M12 2c1.2 1 .9 2.2 0 3-1-1-1.2-2.1 0-3z"/>
                    <path d="M8 10v-1"/>
                    <path d="M16 10v-1"/>
                  </svg>
                  </div>

                <div class="info-body">
                  <div class="info-title">{{ t('user.birthday') }}</div>
                  <div class="info-value">{{ birthdayText }}</div>
                  </div>
                <div class="info-action" aria-hidden="true">
                  <span class="info-action-badge" :title="birthdayRaw ? t('user.edit') : t('user.set')">
                    <!-- edit-2 (Feather) -->
                    <svg v-if="birthdayRaw" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 3 21l.5-4.5L17 3z"></path>
                      <path d="m15 5 4 4"></path>
                    </svg>
                    <!-- plus-circle (Feather) -->
                    <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <path d="M12 8v8"></path>
                      <path d="M8 12h8"></path>
                    </svg>
                  </span>
                </div>
              </button>

              <!-- Email -->
              <button
                class="info-card info-card--action float-in"
                :style="{ '--d': '400ms' }"
                :class="{ animate: contentAnimate }"
                type="button"
                @click="openEdit('email')"
                :aria-label="(profileEmail || userStore.email) ? t('user.editEmailAria') : t('user.setEmailAria')"
              >
                <div class="info-icon" aria-hidden="true">
                  <!-- mail -->
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/>
                    <path d="m22 6-10 7L2 6"/>
                  </svg>
              </div>
  
                <div class="info-body">
                  <div class="info-title">{{ t('user.email') }}</div>
                  <div class="info-value">{{ emailText }}</div>
                </div>
                <div class="info-action" aria-hidden="true">
                  <span class="info-action-badge" :title="(profileEmail || userStore.email) ? t('user.edit') : t('user.set')">
                    <!-- edit-2 (Feather) -->
                    <svg v-if="(profileEmail || userStore.email)" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 3 21l.5-4.5L17 3z"></path>
                      <path d="m15 5 4 4"></path>
                    </svg>
                    <!-- plus-circle (Feather) -->
                    <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <path d="M12 8v8"></path>
                      <path d="M8 12h8"></path>
                    </svg>
                  </span>
                </div>
              </button>

              <!-- PDF Resume -->
              <button
                class="info-card info-card--action float-in"
                :style="{ '--d': '460ms' }"
                :class="{ animate: contentAnimate }"
                type="button"
                @click="router.push({ name: 'resume-pdf' })"
              >
                <div class="info-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <path d="M12 18v-6"/>
                    <path d="M9 15l3-3 3 3"/>
                  </svg>
                </div>

                <div class="info-body">
                  <div class="info-title">{{ i18n.locale === 'zh' ? 'PDF 简历' : 'PDF Resume' }}</div>
                  <div class="info-sub">{{ i18n.locale === 'zh' ? '上传或更新您的 PDF 格式简历' : 'Upload or update your PDF resume' }}</div>
                </div>

                <div class="info-action" aria-hidden="true">
                  <span class="info-action-badge" :title="i18n.locale === 'zh' ? '进入' : 'Open'">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M5 12h14"></path>
                      <path d="m13 5 7 7-7 7"></path>
                    </svg>
                  </span>
                </div>
              </button>
            </div>
          </section>
  
          <!-- Dominate -->
          <section v-else-if="activeTab === 'dominate'" class="panel">
            <div class="profile-cards">
              <!-- My Tasks (All logged-in users) -->
              <button
                class="info-card info-card--action float-in"
                :style="{ '--d': '220ms' }"
                :class="{ animate: contentAnimate }"
                type="button"
                @click="router.push({ name: 'my-tasks' })"
              >
                <div class="info-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 11l3 3L22 4"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  </svg>
                </div>

                <div class="info-body">
                  <div class="info-title">{{ i18n.locale === 'zh' ? '我的任务' : 'My Tasks' }}</div>
                  <div class="info-sub">{{ i18n.locale === 'zh' ? '查看分配给我的任务并提交完成情况。' : 'View assigned tasks and submit your progress.' }}</div>
                </div>

                <div class="info-action" aria-hidden="true">
                  <span class="info-action-badge" :title="i18n.locale === 'zh' ? '进入' : 'Open'">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M5 12h14"></path>
                      <path d="m13 5 7 7-7 7"></path>
                    </svg>
                  </span>
                </div>
              </button>

              <!-- Upload Resume (placeholder card) -->
              <button
                class="info-card info-card--action float-in"
                :style="{ '--d': '280ms' }"
                :class="{ animate: contentAnimate }"
                type="button"
                @click="router.push({ name: 'resume-settings' })"
              >
                <div class="info-icon" aria-hidden="true">
                  <!-- upload-cloud -->
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 17.5a4.5 4.5 0 0 0-3-8.4A6 6 0 0 0 5 10.5a4 4 0 0 0 1 7.8" />
                    <path d="M12 12v9" />
                    <path d="M8.5 15.5 12 12l3.5 3.5" />
                  </svg>
                </div>

                <div class="info-body">
                  <div class="info-title">{{ resumeCardTitle }}</div>
                  <div class="info-sub">{{ resumeCardSub }}</div>
                </div>

                <div class="info-action" aria-hidden="true">
                  <span class="info-action-badge" :title="i18n.locale === 'zh' ? '进入' : 'Open'">
                    <!-- arrow-right -->
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M5 12h14"></path>
                      <path d="m13 5 7 7-7 7"></path>
                    </svg>
                  </span>
                </div>
              </button>

              <!-- Browse All Users -->
              <button
                v-if="isManager"
                class="info-card info-card--action float-in"
                :style="{ '--d': '340ms' }"
                :class="{ animate: contentAnimate }"
                type="button"
                @click="router.push({ name: 'user-list' })"
              >
                <div class="info-icon" aria-hidden="true">
                  <!-- users -->
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                  </svg>
                </div>

                <div class="info-body">
                  <div class="info-title">{{ i18n.locale === 'zh' ? '查询所有用户' : 'Browse All Users' }}</div>
                  <div class="info-sub">{{ i18n.locale === 'zh' ? '查看平台所有注册用户的公开信息与简历。' : 'View public profiles and resumes of all registered users.' }}</div>
                </div>

                <div class="info-action" aria-hidden="true">
                  <span class="info-action-badge" :title="i18n.locale === 'zh' ? '进入' : 'Open'">
                    <!-- arrow-right -->
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M5 12h14"></path>
                      <path d="m13 5 7 7-7 7"></path>
                    </svg>
                  </span>
                </div>
              </button>

              <!-- Intern Applications Management -->
              <button
                v-if="isManager"
                class="info-card info-card--action float-in"
                :style="{ '--d': '400ms' }"
                :class="{ animate: contentAnimate }"
                type="button"
                @click="router.push({ name: 'intern-manage' })"
              >
                <div class="info-icon" aria-hidden="true">
                  <!-- clipboard-list -->
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
                    <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
                    <path d="M9 12h6"></path>
                    <path d="M9 16h6"></path>
                  </svg>
                </div>

                <div class="info-body">
                  <div class="info-title">{{ i18n.locale === 'zh' ? '实习生申请管理' : 'Intern Applications' }}</div>
                  <div class="info-sub">{{ i18n.locale === 'zh' ? '查看、审批或拒绝实习生的报名申请。' : 'Review, approve or reject intern applications.' }}</div>
                </div>

                <div class="info-action" aria-hidden="true">
                  <span class="info-action-badge" :title="i18n.locale === 'zh' ? '进入' : 'Open'">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M5 12h14"></path>
                      <path d="m13 5 7 7-7 7"></path>
                    </svg>
                  </span>
                </div>
              </button>

              <!-- Broadcast Message (Manager only, role >= 3) -->
              <button
                v-if="isManager"
                class="info-card info-card--action float-in"
                :style="{ '--d': '460ms' }"
                :class="{ animate: contentAnimate }"
                type="button"
                @click="router.push({ name: 'broadcast-message' })"
              >
                <div class="info-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 2 11 13"/>
                    <path d="M22 2 15 22 11 13 2 9 22 2"/>
                  </svg>
                </div>

                <div class="info-body">
                  <div class="info-title">{{ i18n.locale === 'zh' ? '群发系统消息' : 'Broadcast Message' }}</div>
                  <div class="info-sub">{{ i18n.locale === 'zh' ? '向多个用户发送系统通知，支持按角色群发或指定用户。' : 'Send system notifications to multiple users by role or specific IDs.' }}</div>
                </div>

                <div class="info-action" aria-hidden="true">
                  <span class="info-action-badge" :title="i18n.locale === 'zh' ? '打开' : 'Open'">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M5 12h14"></path>
                      <path d="m13 5 7 7-7 7"></path>
                    </svg>
                  </span>
                </div>
              </button>

              <!-- Task Management (Manager only, role >= 3) -->
              <button
                v-if="isManager"
                class="info-card info-card--action float-in"
                :style="{ '--d': '520ms' }"
                :class="{ animate: contentAnimate }"
                type="button"
                @click="router.push({ name: 'task-list' })"
              >
                <div class="info-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 11l3 3L22 4"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  </svg>
                </div>

                <div class="info-body">
                  <div class="info-title">{{ i18n.locale === 'zh' ? '任务管理' : 'Task Management' }}</div>
                  <div class="info-sub">{{ i18n.locale === 'zh' ? '发布任务、查看提交、评分管理。' : 'Publish tasks, view submissions, and manage scores.' }}</div>
                </div>

                <div class="info-action" aria-hidden="true">
                  <span class="info-action-badge" :title="i18n.locale === 'zh' ? '打开' : 'Open'">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M5 12h14"></path>
                      <path d="m13 5 7 7-7 7"></path>
                    </svg>
                  </span>
                </div>
              </button>
            </div>
          </section>

          <!-- News -->
          <section v-else-if="activeTab === 'news'" class="panel panel--news">
            <div v-if="!canPublishNews" class="placeholder">
              <div class="placeholder-title">{{ t('user.newsNoAccessTitle') }}</div>
              <div class="placeholder-text">{{ t('user.newsNoAccessText') }}</div>
            </div>

            <div v-else class="news-hub">
              <div class="news-choice">
                <div class="profile-cards">
                  <button
                    class="info-card info-card--action float-in"
                    :class="{ animate: contentAnimate }"
                    :style="{ '--d': '120ms' }"
                    type="button"
                    @click="router.push({ name: 'news-preview' })"
                  >
                    <div class="info-icon" aria-hidden="true">
                      <!-- send -->
                      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 2 11 13"></path>
                        <path d="M22 2 15 22 11 13 2 9 22 2"></path>
                      </svg>
                    </div>

                    <div class="info-body">
                      <div class="info-title">{{ t('user.newsPublishTab') }}</div>
                      <div class="info-value">{{ t('user.newsPublish') }}</div>
                    </div>
                  </button>

                  <button
                    class="info-card info-card--action float-in"
                    :class="{ animate: contentAnimate }"
                    :style="{ '--d': '200ms' }"
                    type="button"
                    @click="router.push({ name: 'news-delete' })"
                  >
                    <div class="info-icon" aria-hidden="true">
                      <!-- trash -->
                      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M3 6h18"></path>
                        <path d="M8 6V4h8v2"></path>
                        <path d="M6 6l1 16h10l1-16"></path>
                        <path d="M10 11v6"></path>
                        <path d="M14 11v6"></path>
                      </svg>
                    </div>

                    <div class="info-body">
                      <div class="info-title">{{ t('user.newsDeleteTab') }}</div>
                      <div class="info-value">{{ t('user.newsDelete') }}</div>
                    </div>
                  </button>
                </div>
                </div>
            </div>
          </section>

          <!-- Messages -->
          <section v-else class="panel panel--messages">
            <!-- Filter Tabs -->
            <div class="msg-filter-tabs float-in" :class="{ animate: contentAnimate }" :style="{ '--d': '120ms' }">
              <button 
                class="msg-filter-tab" 
                :class="{ active: msgFilter === 'all' }"
                @click="msgFilter = 'all'; loadMessages()"
              >
                {{ t('messages.all') }}
              </button>
              <button 
                class="msg-filter-tab" 
                :class="{ active: msgFilter === 'unread' }"
                @click="msgFilter = 'unread'; loadMessages()"
              >
                {{ t('messages.unread') }}
                <span v-if="unreadCount > 0" class="msg-filter-badge">{{ unreadCount }}</span>
              </button>
            </div>

            <!-- Loading -->
            <div v-if="isLoadingMessages" class="msg-loading float-in" :class="{ animate: contentAnimate }" :style="{ '--d': '180ms' }">
              <div class="msg-spinner"></div>
              <span>{{ t('messages.loading') }}</span>
            </div>

            <!-- Empty State -->
            <div v-else-if="messages.length === 0" class="msg-empty float-in" :class="{ animate: contentAnimate }" :style="{ '--d': '180ms' }">
              <div class="msg-empty-icon">
                <svg viewBox="0 0 24 24" width="56" height="56" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                  <polyline points="22,6 12,13 2,6"/>
                </svg>
              </div>
              <div class="msg-empty-title">{{ t('messages.empty') }}</div>
              <div class="msg-empty-desc">{{ t('messages.emptyDesc') }}</div>
            </div>

            <!-- Messages List -->
            <div v-else class="msg-list">
              <div 
                v-for="(msg, idx) in messages" 
                :key="msg.id" 
                class="msg-item"
                :class="{ 
                  'msg-item--unread': !msg.read_at,
                  'msg-item--read': msg.read_at,
                  'msg-item--ready': messagesReady
                }"
                :style="{ '--idx': idx }"
                @click="openMessageDetail(msg)"
              >
                <div class="msg-item-indicator" :class="{ 'msg-item-indicator--read': msg.read_at }"></div>
                <div class="msg-item-content">
                  <div class="msg-item-header">
                    <div class="msg-item-title">{{ msg.title }}</div>
                    <div class="msg-item-time">{{ formatMsgTime(msg.created_at) }}</div>
                  </div>
                  <div class="msg-item-body">{{ msg.content }}</div>
                  <div class="msg-item-footer">
                    <div class="msg-item-actions">
                      <button 
                        v-if="!msg.read_at" 
                        class="msg-item-action"
                        :disabled="markingReadId === msg.id"
                        @click.stop="markAsRead(msg.id)"
                      >
                        {{ markingReadId === msg.id ? '...' : t('messages.markRead') }}
                      </button>
                      <div v-else class="msg-item-read">
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                        {{ t('messages.read') }}
                      </div>
                    </div>
                    <button 
                      class="msg-item-delete"
                      :disabled="deletingMsgId === msg.id"
                      @click.stop="openDeleteMsgModal(msg.id)"
                      :title="t('messages.delete')"
                    >
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 6h18"/>
                        <path d="M8 6V4h8v2"/>
                        <path d="M6 6l1 14h10l1-14"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Message Detail Modal -->
            <div v-if="isMessageDetailOpen" class="modal-layer" role="dialog" aria-modal="true" @keydown.esc.prevent="closeMessageDetail">
              <div class="modal-backdrop" @click="closeMessageDetail" aria-hidden="true"></div>
              <div class="modal msg-detail-modal" @click.stop>
                <div class="modal-header">
                  <div class="modal-title">{{ selectedMessage?.title || (i18n.locale === 'zh' ? '消息详情' : 'Message Detail') }}</div>
                  <button type="button" class="modal-close" @click="closeMessageDetail">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M18 6 6 18" />
                      <path d="M6 6 18 18" />
                    </svg>
                  </button>
                </div>
                <div class="modal-body msg-detail-body">
                  <div class="msg-detail-meta">
                    <span class="msg-detail-time">{{ selectedMessage ? formatMsgTime(selectedMessage.created_at) : '' }}</span>
                    <span v-if="selectedMessage?.read_at" class="msg-detail-status msg-detail-status--read">
                      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                      {{ t('messages.read') }}
                    </span>
                    <span v-else class="msg-detail-status msg-detail-status--unread">{{ t('messages.unread') }}</span>
                  </div>
                  <div class="msg-detail-content">{{ selectedMessage?.content }}</div>
                </div>
                <div class="modal-footer msg-detail-footer">
                  <button 
                    v-if="selectedMessage && !selectedMessage.read_at" 
                    class="btn btn--primary"
                    :disabled="markingReadId === selectedMessage?.id"
                    @click="markAsReadAndClose(selectedMessage.id)"
                  >
                    {{ markingReadId === selectedMessage?.id ? '...' : t('messages.markRead') }}
                  </button>
                  <button class="btn btn--ghost" @click="closeMessageDetail">
                    {{ i18n.locale === 'zh' ? '关闭' : 'Close' }}
                  </button>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>

      <!-- Logout Confirmation Modal -->
      <WarningModal
        v-model="isLogoutModalOpen"
        type="warning"
        :title="i18n.locale === 'zh' ? '确认退出' : 'Confirm Logout'"
        :message="i18n.locale === 'zh' ? '确定要退出登录吗？' : 'Are you sure you want to log out?'"
        :show-cancel="true"
        :confirm-text="t('user.logout')"
        :cancel-text="t('user.cancel')"
        @confirm="confirmLogout"
      />

      <!-- Delete Message Confirmation Modal -->
      <WarningModal
        v-model="isDeleteMsgModalOpen"
        type="warning"
        :title="i18n.locale === 'zh' ? '确认删除' : 'Confirm Delete'"
        :message="i18n.locale === 'zh' ? '确定要删除这条消息吗？此操作无法撤销。' : 'Are you sure you want to delete this message? This action cannot be undone.'"
        :show-cancel="true"
        :confirm-text="i18n.locale === 'zh' ? '删除' : 'Delete'"
        :cancel-text="t('user.cancel')"
        @confirm="confirmDeleteMsg"
      />

      <!-- Edit Modal (Birthday / Email / Username) -->
      <div v-if="isEditOpen" class="modal-layer" role="dialog" aria-modal="true" :aria-label="editModalTitle" @keydown.esc.prevent="closeEdit">
        <div class="modal-backdrop" @click="closeEdit" aria-hidden="true"></div>
        <div class="modal" @click.stop>
          <div class="modal-header">
            <div class="modal-title">{{ editModalTitle }}</div>
            <button type="button" class="modal-close" @click="closeEdit" :aria-label="t('user.closeDialogAria')">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 6 6 18" />
                <path d="M6 6 18 18" />
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <label class="modal-label" :for="editInputId">{{ editFieldLabel }}</label>

            <div v-if="editKey === 'birthday'" class="date-row" :id="editInputId">
              <select class="modal-select" v-model="draftBirthYear" :aria-label="t('user.birthYear')">
                <option value="">{{ t('user.birthYear') }}</option>
                <option v-for="y in birthYearOptions" :key="y" :value="String(y)">{{ y }}</option>
              </select>
              <select class="modal-select" v-model="draftBirthMonth" :aria-label="t('user.birthMonth')">
                <option value="">{{ t('user.birthMonth') }}</option>
                <option v-for="m in 12" :key="m" :value="String(m)">{{ String(m).padStart(2, '0') }}</option>
              </select>
              <select class="modal-select" v-model="draftBirthDay" :aria-label="t('user.birthDay')">
                <option value="">{{ t('user.birthDay') }}</option>
                <option v-for="d in birthDayOptions" :key="d" :value="String(d)">{{ String(d).padStart(2, '0') }}</option>
              </select>
            </div>

            <input
              v-else-if="editKey === 'username'"
              :id="editInputId"
              class="modal-input"
              type="text"
              v-model="draftValue"
              :placeholder="i18n.locale === 'zh' ? '请输入新用户名' : 'Enter new username'"
              :aria-invalid="editError ? 'true' : 'false'"
              autocomplete="username"
            />

            <input
              v-else
              :id="editInputId"
              class="modal-input"
              type="email"
              v-model="draftValue"
              :placeholder="t('user.emailPlaceholder')"
              :aria-invalid="editError ? 'true' : 'false'"
              autocomplete="email"
              inputmode="email"
            />

            <div v-if="editError" class="modal-error" role="alert">{{ editError }}</div>
          </div>

          <div class="modal-actions">
            <button type="button" class="modal-btn ghost" @click="closeEdit" :disabled="isSavingEdit">{{ t('user.cancel') }}</button>
            <button type="button" class="modal-btn primary" @click="saveEdit" :disabled="isSavingEdit">{{ t('user.confirm') }}</button>
          </div>
        </div>
      </div>
    </section>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, watch, nextTick } from 'vue'
  import { useRouter } from 'vue-router'
  import { useUserStore } from '@/stores/user'
  import { useErrorStore } from '@/stores/error'
  import { useSuccessStore } from '@/stores/success'
  import { useI18nStore } from '@/stores/i18n'
  import WarningModal from '@/components/WarningModal.vue'
  import bgVideo from '@/assets/images/section4.webm'
  import bgVideoRight from '@/assets/images/about.mp4'
  
  const router = useRouter()
  const userStore = useUserStore()
  const errorStore = useErrorStore()
  const successStore = useSuccessStore()
  const i18n = useI18nStore()
  const t = (key, vars) => i18n.t(key, vars)
  
  const isMounted = ref(false)
  const contentAnimate = ref(false)
  const activeTab = ref('profile') // 'profile' | 'dominate' | 'news' | 'messages'
  const isSidebarOpen = ref(false) // 侧边栏抽屉状态
  
  // 导航栏弹性滑动指示器
  const navRef = ref(null)
  const navItemProfile = ref(null)
  const navItemDominate = ref(null)
  const navItemNews = ref(null)
  const navItemMessages = ref(null)
  const indicatorTop = ref(0)
  const indicatorHeight = ref(0)
  const isAnimating = ref(false)
  const indicatorReady = ref(false)
  
  const indicatorStyle = computed(() => ({
    transform: `translateY(${indicatorTop.value}px) scaleY(${isAnimating.value ? 1.08 : 1})`,
    height: `${indicatorHeight.value}px`,
  }))
  
  // 获取当前 tab 对应的按钮元素
  function getNavItemRef(tab) {
    const refs = {
      profile: navItemProfile,
      dominate: navItemDominate,
      news: navItemNews,
      messages: navItemMessages,
    }
    return refs[tab]?.value
  }
  
  // 更新指示器位置
  function updateIndicatorPosition(tab, animate = true) {
    const navEl = navRef.value
    const itemEl = getNavItemRef(tab)
    if (!navEl || !itemEl) return
    
    const navRect = navEl.getBoundingClientRect()
    const itemRect = itemEl.getBoundingClientRect()
    
    if (animate) {
      isAnimating.value = true
      setTimeout(() => { isAnimating.value = false }, 300)
    }
    
    indicatorTop.value = itemRect.top - navRect.top
    indicatorHeight.value = itemRect.height
  }
  
  // 切换 tab
  function switchTab(tab) {
    if (activeTab.value === tab) return
    activeTab.value = tab
    sessionStorage.setItem('user_active_tab', tab)
    updateIndicatorPosition(tab, true)
    // 选择后关闭侧边栏
    isSidebarOpen.value = false
  }

  function toggleSidebar() {
    isSidebarOpen.value = !isSidebarOpen.value
  }

  function closeSidebar() {
    isSidebarOpen.value = false
  }

  const headerText = computed(() => {
    if (activeTab.value === 'profile') return t('user.headerProfile')
    if (activeTab.value === 'dominate') return t('user.headerDominate')
    if (activeTab.value === 'messages') return t('messages.headerMessages')
    return t('user.headerNews')
  })

  const subtitleText = computed(() => {
    if (activeTab.value === 'profile') return t('user.subtitleProfile')
    if (activeTab.value === 'dominate') return t('user.subtitleDominate')
    if (activeTab.value === 'messages') return t('messages.subtitleMessages')
    return t('user.subtitleNews')
  })

  const resumeCardTitle = computed(() =>
    i18n.locale === 'zh' ? '履历 / 资料与头像管理' : 'Resume & Images'
  )

  const resumeCardSub = computed(() =>
    i18n.locale === 'zh'
      ? '填写履历、设置公开状态，并管理头像/证书/项目/作品集/bio 图片。'
      : 'Edit resume, toggle public visibility, and manage avatar/certificate/project/portfolio/bio images.'
  )

  const canPublishNews = ref(false)
  const isAdmin = ref(false)
  const isManager = ref(false)
  const hasUpdatedResume = ref(false)

  // Messages state
  const messages = ref([])
  const isLoadingMessages = ref(false)
  const msgFilter = ref('all') // 'all' | 'unread'
  const unreadCount = ref(0)
  const markingReadId = ref(null)
  const deletingMsgId = ref(null)
  const isMessageDetailOpen = ref(false)
  const selectedMessage = ref(null)
  const messagesReady = ref(false) // 控制消息列表出场动画
  const isDeleteMsgModalOpen = ref(false)
  const pendingDeleteMsgId = ref(null)

  // (Broadcast moved to separate page)

  // 检查用户是否更新了 profile（有 email 或 birthday 或 photo）
  const hasUpdatedProfile = computed(() => {
    const hasEmail = !!(userStore.email || profileEmail.value)
    const hasBirthday = !!userStore.birthday
    const hasPhoto = !!(userStore.photo || userPhotoUrl.value)
    return hasEmail || hasBirthday || hasPhoto
  })

  function todayYmd() {
    const d = new Date()
    const yyyy = d.getFullYear()
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    return `${yyyy}-${mm}-${dd}`
  }

  function computeCanPublishNewsFromToken(token) {
    // Minimal JWT payload inspection. If the backend changes role rules,
    // the POST response (401/403) will still enforce the source of truth.
    try {
      const [, payload] = String(token || '').split('.')
      if (!payload) return false
      const json = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
      const role = json?.role
      // role >= 3 can publish/delete news
      if (typeof role === 'number' && role >= 3) return true
      // If token exists but no role claims, allow and let backend decide
      if (!('role' in json)) return true
      return false
    } catch {
      return !!token
    }
  }

  function computeIsAdminFromToken(token) {
    // Check if user has admin role (role === 4)
    try {
      const [, payload] = String(token || '').split('.')
      if (!payload) return false
      const json = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
      return json?.role === 4
    } catch {
      return false
    }
  }

  function computeIsManagerFromToken(token) {
    // Check if user has manager role (role >= 3)
    try {
      const [, payload] = String(token || '').split('.')
      if (!payload) return false
      const json = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
      return typeof json?.role === 'number' && json.role >= 3
    } catch {
      return false
    }
  }

  function parseApiDate(s) {
    if (!s) return null
    const hasTz = /Z$|[+-]\d{2}:\d{2}$/.test(s)
    return new Date(hasTz ? s : `${s}Z`)
  }

  function applyProfileFromApi(data) {
    if (!data || typeof data !== 'object') return

    const nextDisplayName = data.display_name ?? data.displayName
    const nextPhone = data.phone
    const nextEmail = data.email
    const nextBirthday = data.birthday ?? data.birthdate ?? data.birth_day
    const nextUsername = data.username
    const nextCreatedAt = data.created_at ?? data.createdAt
    const nextUpdatedAt = data.updated_at ?? data.updatedAt
    const nextPhoto = data.photo ?? data.photo_url ?? data.avatar ?? data.avatar_url

    const storePatch = {}
    if (nextDisplayName !== undefined) storePatch.displayName = String(nextDisplayName || '')
    if (nextPhone !== undefined) storePatch.phone = String(nextPhone || '')
    if (nextEmail !== undefined) storePatch.email = String(nextEmail || '')
    if (nextBirthday !== undefined) storePatch.birthday = String(nextBirthday || '')
    if (nextUpdatedAt !== undefined) storePatch.updatedAt = String(nextUpdatedAt || '')
    if (nextPhoto !== undefined) storePatch.photo = String(nextPhoto || '')

    if (Object.keys(storePatch).length) {
      userStore.setProfileFields(storePatch)
      if (storePatch.email !== undefined) profileEmail.value = storePatch.email
      if (storePatch.photo !== undefined) userPhotoUrl.value = storePatch.photo
    }

    if (nextUsername !== undefined) userStore.username = String(nextUsername || '')
    if (nextCreatedAt !== undefined) userStore.createdAt = String(nextCreatedAt || '')
    if (nextUpdatedAt !== undefined) userStore.updatedAt = String(nextUpdatedAt || '')
  }
  
  const DAY_MS = 1000 * 60 * 60 * 24
  
  const displayName = computed(
    () => userStore.displayName || userStore.username || t('common.guest')
  )
  const username = computed(() => userStore.username || userStore.phone || '—')
  const createdAtRaw = computed(() => userStore.createdAt || userStore.created_at || '')
  const updatedAtRaw = computed(() => userStore.updatedAt || userStore.updated_at || '')
  
  const daysInDAIL = computed(() => {
    const created = parseApiDate(createdAtRaw.value)
    if (!created) return 0
    const diff = Date.now() - created.getTime()
    return Math.max(0, Math.floor(diff / DAY_MS))
  })
  
  const createdAtText = computed(() => {
    const d = parseApiDate(createdAtRaw.value)
    if (!d) return '—'
    // 统一输出为本地可读格式
    const yyyy = d.getFullYear()
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    const hh = String(d.getHours()).padStart(2, '0')
    const mi = String(d.getMinutes()).padStart(2, '0')
    return `${yyyy}-${mm}-${dd} ${hh}:${mi}`
  })

  const updatedAtText = computed(() => {
    const d = parseApiDate(updatedAtRaw.value)
    if (!d) return '—'
    const yyyy = d.getFullYear()
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    const hh = String(d.getHours()).padStart(2, '0')
    const mi = String(d.getMinutes()).padStart(2, '0')
    return `${yyyy}-${mm}-${dd} ${hh}:${mi}`
  })

  const avatarLetter = computed(() => {
    const s = (displayName.value || 'U').trim()
    return (s[0] || 'U').toUpperCase()
  })

  const birthdayRaw = computed(() =>
    userStore.birthday || userStore.birthdate || userStore.birth_day || ''
  )
  const birthdayText = computed(() => birthdayRaw.value || t('common.notSet'))
  
  /** Profile 表单（先做本地 + store patch，后续你接 API 再替换） */
  const profileName = computed(() => userStore.displayName || userStore.username || t('common.guest'))
  const profilePhone = ref(userStore.phone || '')
  const profileEmail = ref(userStore.email || '')

  const emailText = computed(() => {
    const v = (profileEmail.value || userStore.email || '').trim()
    return v || t('common.notSet')
  })

  const isEditOpen = ref(false)
  const editKey = ref('email') // 'email' | 'birthday' | 'username'
  const draftValue = ref('')
  const editError = ref('')
  const draftBirthYear = ref('')
  const draftBirthMonth = ref('')
  const draftBirthDay = ref('')
  const isSavingEdit = ref(false)

  // Photo upload
  const photoInputRef = ref(null)
  const isUploadingPhoto = ref(false)
  const userPhotoUrl = ref('')

  // 监听 store 中 photo 的变化，确保刷新后能正确显示
  watch(
    () => userStore.photo,
    (newVal) => {
      if (newVal) {
        userPhotoUrl.value = newVal
      }
    },
    { immediate: true }
  )

  const editInputId = computed(() => `edit-${editKey.value}`)
  const editModalTitle = computed(() => {
    if (editKey.value === 'birthday') return t('user.editBirthdayTitle')
    if (editKey.value === 'username') return i18n.locale === 'zh' ? '修改用户名' : 'Edit Username'
    return t('user.editEmailTitle')
  })
  const editFieldLabel = computed(() => {
    if (editKey.value === 'birthday') return t('user.birthday')
    if (editKey.value === 'username') return t('user.name')
    return t('user.email')
  })

  const currentYear = computed(() => new Date().getFullYear())
  const birthYearOptions = computed(() => {
    // 1900 ~ currentYear, descending for faster picking
    const out = []
    for (let y = currentYear.value; y >= 1900; y--) out.push(y)
    return out
  })

  const birthDayOptions = computed(() => {
    const y = parseInt(draftBirthYear.value || '0', 10)
    const m = parseInt(draftBirthMonth.value || '0', 10)
    if (!y || !m) return []
    const daysInMonth = new Date(y, m, 0).getDate()
    return Array.from({ length: daysInMonth }, (_, i) => i + 1)
  })

  function normalizeYmd(s) {
    if (!s) return ''
    const trimmed = String(s).trim()
    // already YYYY-MM-DD
    if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) return trimmed
    // try Date parse
    const d = new Date(trimmed)
    if (Number.isNaN(d.getTime())) return ''
    const yyyy = d.getFullYear()
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    return `${yyyy}-${mm}-${dd}`
  }

  function openEdit(key) {
    editKey.value = key
    editError.value = ''
    if (key === 'birthday') {
      const ymd = normalizeYmd(birthdayRaw.value)
      if (ymd) {
        const [y, m, d] = ymd.split('-')
        draftBirthYear.value = y
        draftBirthMonth.value = String(parseInt(m, 10))
        draftBirthDay.value = String(parseInt(d, 10))
      } else {
        draftBirthYear.value = ''
        draftBirthMonth.value = ''
        draftBirthDay.value = ''
      }
    } else if (key === 'username') {
      draftValue.value = (userStore.username || '').trim()
    } else {
      draftValue.value = (profileEmail.value || userStore.email || '').trim()
    }
    isEditOpen.value = true
  }

  function closeEdit() {
    isEditOpen.value = false
    editError.value = ''
  }

  function isValidEmail(v) {
    const s = String(v || '').trim()
    if (!s) return true // allow empty (unset)
    // lightweight client validation; backend will be source of truth later
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s)
  }

  function extractApiErrorMessage(data, status) {
    if (Array.isArray(data?.detail)) {
      const msgs = data.detail
        .map((it) => it?.msg)
        .filter((s) => typeof s === 'string' && s.trim().length > 0)
        .map((s) => s.trim())
      if (msgs.length) {
        const uniq = []
        for (const m of msgs) if (!uniq.includes(m)) uniq.push(m)
        return uniq.join(' ; ')
      }
    }
    if (typeof data?.detail === 'string' && data.detail.trim()) return data.detail.trim()
    if (typeof data?.message === 'string' && data.message.trim()) return data.message.trim()
    if (typeof data === 'string' && data.trim()) return data.trim()
    return `Request failed (${status})`
  }

  async function patchMyProfile(patch) {
    const token = userStore.accessToken
    if (!token) {
      throw new Error(t('auth.errLoginFailed'))
    }

    const res = await fetch('/api/me/profile', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(patch),
    })

    let data = null
    try { data = await res.json() } catch (e) {}

    if (!res.ok) {
      throw new Error(extractApiErrorMessage(data, res.status))
    }
    return data
  }

  async function uploadMyPhoto(file) {
    const token = userStore.accessToken
    if (!token) {
      throw new Error(t('auth.errLoginFailed'))
    }

    const formData = new FormData()
    formData.append('file', file)
    formData.append('filename', file.name || 'avatar')

    const res = await fetch('/api/me/photo', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    })

    let data = null
    try { data = await res.json() } catch (e) {}

    if (!res.ok) {
      throw new Error(extractApiErrorMessage(data, res.status))
    }
    return data
  }

  const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  const MAX_IMAGE_SIZE = 10 * 1024 * 1024 // 10MB

  async function handlePhotoUpload(event) {
    const file = event?.target?.files?.[0]
    if (!file) return

    // Validate file type
    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      errorStore.showError(i18n.locale === 'zh' ? '仅支持 JPG、PNG、GIF、WebP 格式' : 'Only JPG/PNG/GIF/WebP are supported')
      if (photoInputRef.value) photoInputRef.value.value = ''
      return
    }

    // Validate file size
    if (file.size > MAX_IMAGE_SIZE) {
      errorStore.showError(i18n.locale === 'zh' ? '图片大小不能超过 10MB' : 'Image must be <= 10MB')
      if (photoInputRef.value) photoInputRef.value.value = ''
      return
    }

    isUploadingPhoto.value = true
    try {
      const result = await uploadMyPhoto(file)
      // Update local photo URL
      const photoUrl = result.photo || result.photo_url || result.url || ''
      if (photoUrl) {
        userPhotoUrl.value = photoUrl
        userStore.setProfileFields({ photo: photoUrl })
      }
      successStore.showSuccess(i18n.locale === 'zh' ? '头像上传成功' : 'Photo uploaded')
    } catch (e) {
      errorStore.showError(i18n.locale === 'zh' ? `头像上传失败：${e?.message || e}` : `Photo upload failed: ${e?.message || e}`)
    } finally {
      isUploadingPhoto.value = false
      if (photoInputRef.value) photoInputRef.value.value = ''
    }
  }

  async function fetchMyProfile() {
    const token = userStore.accessToken
    if (!token) return

    try {
      const res = await fetch('/api/me/profile', {
        headers: { Authorization: `Bearer ${token}` },
      })

      let data = null
      try { data = await res.json() } catch (e) {}

      if (!res.ok) {
        throw new Error(extractApiErrorMessage(data, res.status))
      }

      applyProfileFromApi(data)
    } catch (err) {
      errorStore.showError(err?.message || t('common.comingSoon'))
    }
  }

  async function fetchMyResume() {
    const token = userStore.accessToken
    if (!token) return

    try {
      const res = await fetch('/api/resumes/me', {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (res.ok) {
        let data = null
        try { data = await res.json() } catch (e) {}
        // 如果有 resume 数据，说明用户已更新过履历
        hasUpdatedResume.value = !!(data && (data.id || data.user_id || data.updated_at))
      } else if (res.status === 404) {
        // 没有 resume
        hasUpdatedResume.value = false
      }
    } catch (err) {
      // 静默失败，不影响页面显示
      hasUpdatedResume.value = false
    }
  }

  // Messages functions
  async function loadMessages() {
    const token = userStore.accessToken
    if (!token) return

    isLoadingMessages.value = true
    messagesReady.value = false // 重置动画状态
    try {
      const unreadOnly = msgFilter.value === 'unread'
      const res = await fetch(`/api/messages/me?limit=50&offset=0&unread_only=${unreadOnly}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        messages.value = await res.json()
        // 等待DOM更新后触发出场动画
        await nextTick()
        requestAnimationFrame(() => {
          messagesReady.value = true
        })
      }
    } catch (err) {
      // 静默失败
    } finally {
      isLoadingMessages.value = false
    }
  }

  async function loadUnreadCount() {
    const token = userStore.accessToken
    if (!token) return

    try {
      const res = await fetch('/api/messages/me?limit=100&offset=0&unread_only=true', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        unreadCount.value = Array.isArray(data) ? data.length : 0
      }
    } catch (err) {
      // 静默失败
    }
  }

  async function markAsRead(messageId) {
    const token = userStore.accessToken
    if (!token) return

    markingReadId.value = messageId
    try {
      const res = await fetch(`/api/messages/${messageId}/read`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        // 更新本地状态
        const msg = messages.value.find(m => m.id === messageId)
        if (msg) {
          msg.read_at = new Date().toISOString()
        }
        // 更新 selectedMessage 如果是当前选中的
        if (selectedMessage.value && selectedMessage.value.id === messageId) {
          selectedMessage.value.read_at = new Date().toISOString()
        }
        // 更新未读数
        if (unreadCount.value > 0) unreadCount.value--
      }
    } catch (err) {
      // 静默失败
    } finally {
      markingReadId.value = null
    }
  }

  async function markAsReadAndClose(messageId) {
    await markAsRead(messageId)
    closeMessageDetail()
  }

  function openMessageDetail(msg) {
    selectedMessage.value = { ...msg }
    isMessageDetailOpen.value = true
  }

  function closeMessageDetail() {
    isMessageDetailOpen.value = false
    selectedMessage.value = null
  }

  async function deleteMessage(messageId) {
    const token = userStore.accessToken
    if (!token) return

    deletingMsgId.value = messageId
    try {
      const res = await fetch(`/api/messages/${messageId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok || res.status === 204) {
        // 从列表中移除
        const idx = messages.value.findIndex(m => m.id === messageId)
        if (idx !== -1) {
          const msg = messages.value[idx]
          // 如果是未读消息，更新未读数
          if (!msg.read_at && unreadCount.value > 0) {
            unreadCount.value--
          }
          messages.value.splice(idx, 1)
        }
        successStore.showSuccess(i18n.locale === 'zh' ? '已删除' : 'Deleted')
      }
    } catch (err) {
      errorStore.showError(err?.message || (i18n.locale === 'zh' ? '删除失败' : 'Delete failed'))
    } finally {
      deletingMsgId.value = null
    }
  }

  function openDeleteMsgModal(msgId) {
    pendingDeleteMsgId.value = msgId
    isDeleteMsgModalOpen.value = true
  }

  async function confirmDeleteMsg() {
    if (pendingDeleteMsgId.value) {
      await deleteMessage(pendingDeleteMsgId.value)
    }
    isDeleteMsgModalOpen.value = false
    pendingDeleteMsgId.value = null
  }

  function formatMsgTime(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    const now = new Date()
    const diffMs = now - d
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) {
      return d.toLocaleTimeString(i18n.locale === 'zh' ? 'zh-CN' : 'en-US', { hour: '2-digit', minute: '2-digit' })
    } else if (diffDays === 1) {
      return i18n.locale === 'zh' ? '昨天' : 'Yesterday'
    } else if (diffDays < 7) {
      return `${diffDays} ${i18n.locale === 'zh' ? '天前' : 'days ago'}`
    } else {
      return d.toLocaleDateString(i18n.locale === 'zh' ? 'zh-CN' : 'en-US', { month: 'short', day: 'numeric' })
    }
  }

  // (Broadcast functions moved to separate page)

  async function saveEdit() {
    if (isSavingEdit.value) return
    editError.value = ''

    const patch = {}
    if (editKey.value === 'email') {
      const next = String(draftValue.value || '').trim()
      if (!isValidEmail(next)) {
        editError.value = t('user.invalidEmail')
        return
      }
      patch.email = next
    } else if (editKey.value === 'username') {
      const next = String(draftValue.value || '').trim()
      if (!next) {
        editError.value = i18n.locale === 'zh' ? '用户名不能为空' : 'Username cannot be empty'
        return
      }
      if (next.length < 2) {
        editError.value = i18n.locale === 'zh' ? '用户名至少需要2个字符' : 'Username must be at least 2 characters'
        return
      }
      patch.username = next
    } else {
      const y = parseInt(draftBirthYear.value || '0', 10)
      const m = parseInt(draftBirthMonth.value || '0', 10)
      const d = parseInt(draftBirthDay.value || '0', 10)
      patch.birthday = y && m && d
        ? `${String(y).padStart(4, '0')}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`
        : ''
    }

    isSavingEdit.value = true
    try {
      const resp = await patchMyProfile(patch)
      // 以接口返回为准（如果没返回字段，则回落到本次 patch 值）
      const nextEmail = Object.prototype.hasOwnProperty.call(patch, 'email') ? (resp?.email ?? patch.email) : undefined
      const nextBirthday = Object.prototype.hasOwnProperty.call(patch, 'birthday') ? (resp?.birthday ?? patch.birthday) : undefined
      const nextUsername = Object.prototype.hasOwnProperty.call(patch, 'username') ? (resp?.username ?? patch.username) : undefined
      const nextUpdatedAt = resp?.updated_at ?? resp?.updatedAt

      const storePatch = {}
      if (nextEmail !== undefined) storePatch.email = nextEmail
      if (nextBirthday !== undefined) storePatch.birthday = nextBirthday
      if (nextUpdatedAt !== undefined) storePatch.updatedAt = nextUpdatedAt
      userStore.setProfileFields(storePatch)

      if (nextEmail !== undefined) profileEmail.value = String(nextEmail || '')
      if (nextUsername !== undefined) {
        userStore.username = String(nextUsername || '')
        // 同步到 storage
        const storage = userStore.getStorage()
        storage.setItem('username', userStore.username)
      }

      closeEdit()
      successStore.showSuccess(t('common.saved'))
    } catch (err) {
      const msg = err?.message || ''
      if (msg.includes('already taken') || msg.includes('已被占用')) {
        editError.value = i18n.locale === 'zh' ? '该用户名已被占用' : 'Username already taken'
      } else {
        errorStore.showError(msg || t('common.comingSoon'))
      }
    } finally {
      isSavingEdit.value = false
    }
  }
  
  function handleResetProfile() {
    profilePhone.value = userStore.phone || ''
    profileEmail.value = userStore.email || ''
  }
  
  function handleSaveProfile() {
    // Pinia：允许直接 patch（即便后续你 store 扩展字段也不冲突）
    userStore.$patch({
      phone: profilePhone.value?.trim() || '',
      email: profileEmail.value?.trim() || '',
    })
    successStore.showSuccess(t('common.saved'))
  }
  
  // Logout confirmation modal
  const isLogoutModalOpen = ref(false)

  function handleLogout() {
    isLogoutModalOpen.value = true
  }

  function confirmLogout() {
    userStore.logout()
    router.push('/login')
  }
  
  onMounted(() => {
    // 先计算权限
    canPublishNews.value = computeCanPublishNewsFromToken(userStore.accessToken)
    isAdmin.value = computeIsAdminFromToken(userStore.accessToken)
    isManager.value = computeIsManagerFromToken(userStore.accessToken)
    
    // 恢复上次的 tab
    const savedTab = sessionStorage.getItem('user_active_tab')
    if (savedTab && ['profile', 'dominate', 'news', 'messages'].includes(savedTab)) {
      // 如果是 news tab 但没有权限，回退到 profile
      if (savedTab === 'news' && !canPublishNews.value) {
        activeTab.value = 'profile'
      } else {
        activeTab.value = savedTab
      }
    }
    
    setTimeout(() => {
      isMounted.value = true
      contentAnimate.value = true
      // 初始化指示器位置 - 延迟等待入场动画完成
      setTimeout(() => {
        updateIndicatorPosition(activeTab.value, false)
        // 再延迟一点让指示器淡入显示
        setTimeout(() => {
          indicatorReady.value = true
        }, 50)
      }, 600)
    }, 80)
    fetchMyProfile()
    fetchMyResume()
    loadUnreadCount()
  })

  watch(activeTab, async () => {
    contentAnimate.value = false
    await nextTick()
    requestAnimationFrame(() => {
      contentAnimate.value = true
    })
  })

  watch(
    () => userStore.accessToken,
    () => {
      canPublishNews.value = computeCanPublishNewsFromToken(userStore.accessToken)
      isAdmin.value = computeIsAdminFromToken(userStore.accessToken)
      isManager.value = computeIsManagerFromToken(userStore.accessToken)
      if (!userStore.accessToken) {
        if (activeTab.value === 'news') activeTab.value = 'profile'
        hasUpdatedResume.value = false
      } else {
        fetchMyProfile()
        fetchMyResume()
      }
    }
  )
  
  // 当 canPublishNews 变化时，重新计算指示器位置
  watch(canPublishNews, () => {
    nextTick(() => {
      updateIndicatorPosition(activeTab.value, false)
    })
  })
  </script>
  
  <style scoped>
  .user-page {
    position: relative;
    min-height: 100vh;
    background: #fff;
    overflow: hidden;
  }
  
  /* 只占左侧部分 */
  .bg-layer {
    position: absolute;
    top: 0;
    left: 0;
    width: 34vw;
    height: 100%;
    overflow: hidden;
    z-index: 0;
    pointer-events: none;
  }
  
  .bg-video {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: saturate(1.05);
  }
  
  /* 让右边缘柔和过渡到白底 */
  .bg-mask {
    position: absolute;
    inset: 0;
    background:
    linear-gradient(
      to right,
      rgba(255,255,255,0) 0%,
      rgba(255,255,255,0) 25%,
      rgba(255,255,255,0.25) 55%,
      rgba(255,255,255,0.65) 80%,
      rgba(255,255,255,1) 100%
    ),
    radial-gradient(
      120% 80% at 100% 50%,
      rgba(255,255,255,0.55) 0%,
      rgba(255,255,255,0) 60%
    );
  }

  /* 右侧背景视频 */
  .bg-layer-right {
    position: absolute;
    top: 0;
    right: 0;
    width: 24vw;
    height: 100%;
    overflow: hidden;
    z-index: 0;
    pointer-events: none;
  }

  .bg-video-right {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: saturate(1.05);
  }

  /* 让左边缘柔和过渡 */
  .bg-mask-right {
    position: absolute;
    inset: 0;
    background:
      linear-gradient(
        to left,
        rgba(255,255,255,0) 0%,
        rgba(255,255,255,0) 25%,
        rgba(255,255,255,0.25) 55%,
        rgba(255,255,255,0.65) 80%,
        rgba(255,255,255,1) 100%
      ),
      radial-gradient(
        120% 80% at 0% 50%,
        rgba(255,255,255,0.55) 0%,
        rgba(255,255,255,0) 60%
      );
  }
  
  /* 主布局 */
  .layout {
    position: relative;
    z-index: 1;
    min-height: 100vh;
    display: block;
  }

  /* 汉堡菜单按钮 - 贴边箭头样式 */
  .menu-toggle {
    position: fixed;
    top: 50%;
    left: 0;
    transform: translateY(-50%);
    z-index: 60;
    width: 24px;
    height: 72px;
    border: none;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 0 16px 16px 0;
    box-shadow: 2px 0 16px rgba(0, 0, 0, 0.08);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    opacity: 1;
    visibility: visible;
  }

  .menu-toggle:hover {
    width: 32px;
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.12);
  }

  .menu-toggle:active {
    width: 28px;
    background: rgba(240, 240, 240, 0.95);
  }

  .menu-toggle.is-hidden {
    opacity: 0;
    visibility: hidden;
    transform: translateY(-50%) translateX(-100%);
  }

  /* 隐藏原来的三条横线 */
  .menu-toggle-bar {
    display: none;
  }

  /* 箭头图标 */
  .menu-toggle::after {
    content: '';
    width: 8px;
    height: 8px;
    border-right: 2px solid #0f172a;
    border-bottom: 2px solid #0f172a;
    transform: rotate(-45deg) translateX(-1px);
    transition: transform 0.3s ease, border-color 0.3s ease;
  }

  .menu-toggle:hover::after {
    transform: rotate(-45deg) translateX(1px);
    border-color: #000;
  }

  /* 遮罩层 */
  .sidebar-overlay {
    position: fixed;
    inset: 0;
    z-index: 49;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.35s ease, visibility 0.35s ease;
  }

  .sidebar-overlay.is-visible {
    opacity: 1;
    visibility: visible;
  }
  
  /* Sidebar */
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 50;
    width: 320px;
    height: 100vh;
    padding: 36px 28px;
    display: flex;
    flex-direction: column;
    gap: 26px;
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-right: 1px solid rgba(255, 255, 255, 0.5);
    box-shadow: 4px 0 32px rgba(0, 0, 0, 0.08);
    transform: translateX(-100%);
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow-y: auto;
  }

  .sidebar.is-open {
    transform: translateX(0);
  }
  
  .nav {
    margin-top: 52px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    position: relative;
  }
  
  /* 弹性滑动指示器 */
  .nav-indicator {
    position: absolute;
    left: 0;
    right: 0;
    background: rgba(0, 0, 0, 0.88);
    border-radius: 16px;
    pointer-events: none;
    z-index: 0;
    opacity: 0;
    transition: 
      transform 0.45s cubic-bezier(0.34, 1.56, 0.64, 1),
      height 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
      opacity 0.3s ease;
  }
  
  .nav-indicator--ready {
    opacity: 1;
  }
  
  .nav-item {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    text-align: left;
    border: 1.2px solid rgba(0, 0, 0, 0.1);
    background: rgba(255, 255, 255, 0.5);
    border-radius: 16px;
    padding: 14px 14px;
    cursor: pointer;
    color: #0f172a;
    transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
    position: relative;
    z-index: 1;
  }

  .nav-content {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-width: 0;
  }

  /* 当没有 nav-content 包装时，让 nav-text 和 nav-desc 占满宽度 */
  .nav-item > .nav-text {
    width: 100%;
  }

  .nav-item > .nav-desc {
    width: 100%;
  }
  
  .nav-item:hover {
    transform: translateY(-1px);
    box-shadow: 0 14px 35px rgba(0, 0, 0, 0.08);
    background: rgba(255, 255, 255, 0.8);
    border-color: rgba(0, 0, 0, 0.15);
  }
  
  .nav--ready .nav-item.active {
    background: transparent;
    border-color: transparent;
    color: #fff;
  }

  .nav-item:disabled {
    opacity: 0.45;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
  }

  .nav-item:disabled:hover {
    transform: none;
    box-shadow: none;
  }

  /* News hub (Publish / Delete) */
  .news-hub {
    width: 100%;
  }

  .panel--news .news-hub {
    padding: 6px 2px;
  }

  /* Messages Panel */
  .panel--messages {
    padding: 6px 2px;
  }

  .msg-filter-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
  }

  .msg-filter-tab {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 10px 20px;
    border: 1.5px solid rgba(0, 0, 0, 0.1);
    background: transparent;
    border-radius: 999px;
    font-size: 14px;
    font-weight: 500;
    color: rgba(0, 0, 0, 0.55);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .msg-filter-tab:hover {
    border-color: rgba(0, 0, 0, 0.25);
    color: #0f172a;
  }

  .msg-filter-tab.active {
    background: #0f172a;
    border-color: #0f172a;
    color: #fff;
  }

  .msg-filter-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 18px;
    height: 18px;
    padding: 0 5px;
    border-radius: 999px;
    background: rgba(239, 68, 68, 0.15);
    color: #dc2626;
    font-size: 11px;
    font-weight: 700;
  }

  .msg-filter-tab.active .msg-filter-badge {
    background: rgba(255, 255, 255, 0.2);
    color: #fff;
  }

  .msg-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 48px 0;
    color: rgba(0, 0, 0, 0.45);
    font-size: 14px;
  }

  .msg-spinner {
    width: 28px;
    height: 28px;
    border: 2.5px solid rgba(0, 0, 0, 0.1);
    border-top-color: #0f172a;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .msg-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 56px 24px;
    text-align: center;
  }

  .msg-empty-icon {
    color: rgba(0, 0, 0, 0.2);
    margin-bottom: 16px;
  }

  .msg-empty-title {
    font-size: 18px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 6px;
  }

  .msg-empty-desc {
    font-size: 14px;
    color: rgba(0, 0, 0, 0.45);
  }

  .msg-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .msg-item {
    position: relative;
    display: flex;
    gap: 14px;
    padding: 20px 22px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.95);
    border: 1.5px solid rgba(0, 0, 0, 0.08);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
    cursor: pointer;
    /* 出场动画初始状态 */
    opacity: 0;
    transform: translateY(32px);
    filter: blur(8px);
    transition: 
      opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1),
      transform 0.6s cubic-bezier(0.16, 1, 0.3, 1),
      filter 0.6s cubic-bezier(0.16, 1, 0.3, 1),
      box-shadow 0.25s ease,
      border-color 0.25s ease,
      background 0.25s ease;
    transition-delay: calc(var(--idx, 0) * 100ms);
    /* 防止文字抖动 */
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  .msg-item--ready {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }

  .msg-item:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1);
    border-color: rgba(0, 0, 0, 0.12);
    background: #ffffff;
  }

  .msg-item--ready:hover {
    transform: translateY(-4px);
  }

  .msg-item:active {
    transform: translateY(1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    background: rgba(0, 0, 0, 0.02);
    transition: 
      transform 0.08s ease,
      box-shadow 0.08s ease,
      background 0.08s ease;
  }

  /* 未读消息 - 蓝色边框 */
  .msg-item--unread {
    border-color: rgba(59, 130, 246, 0.25);
  }

  .msg-item--unread:hover {
    border-color: rgba(59, 130, 246, 0.4);
  }

  .msg-item--unread:active {
    background: rgba(59, 130, 246, 0.03);
  }

  /* 已读消息 - 绿色边框 */
  .msg-item--read {
    border-color: rgba(34, 197, 94, 0.25);
  }

  .msg-item--read:hover {
    border-color: rgba(34, 197, 94, 0.4);
  }

  .msg-item--read:active {
    background: rgba(34, 197, 94, 0.03);
  }

  .msg-item-indicator {
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 40%;
    min-height: 24px;
    background: #3b82f6;
    border-radius: 0 4px 4px 0;
  }

  .msg-item-indicator--read {
    background: #22c55e;
  }

  .msg-item-content {
    flex: 1;
    min-width: 0;
  }

  .msg-item-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 8px;
  }

  .msg-item-title {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.01em;
  }

  .msg-item--unread .msg-item-title {
    color: #1e40af;
  }

  .msg-item-time {
    flex-shrink: 0;
    font-size: 12px;
    color: rgba(0, 0, 0, 0.4);
    font-weight: 500;
  }

  .msg-item-body {
    width: 720px;
    font-size: 14px;
    line-height: 1.6;
    color: #374151;
    /* 限制为单行，多余文字省略号 */
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .msg-item-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 6px;
  }

  .msg-item-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .msg-item-action {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 14px;
    border: 1.5px solid #3b82f6;
    background: transparent;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    color: #3b82f6;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .msg-item-action:hover:not(:disabled) {
    background: #3b82f6;
    color: #fff;
  }

  .msg-item-action:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .msg-item-read {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #16a34a;
    font-weight: 500;
  }

  .msg-item-delete {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: none;
    background: rgba(239, 68, 68, 0.08);
    border-radius: 8px;
    color: #ef4444;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
    -webkit-tap-highlight-color: transparent;
  }

  .msg-item-delete:hover:not(:disabled) {
    background: rgba(239, 68, 68, 0.15);
    transform: scale(1.08);
  }

  .msg-item-delete:active:not(:disabled) {
    transform: scale(0.92);
    transition: transform 0.1s ease;
  }

  .msg-item-delete:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  /* 消息详情弹窗 */
  .msg-detail-modal {
    max-width: 520px;
    width: 90%;
  }

  .msg-detail-body {
    padding: 24px !important;
  }

  .msg-detail-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  }

  .msg-detail-time {
    font-size: 13px;
    color: rgba(0, 0, 0, 0.5);
  }

  .msg-detail-status {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
  }

  .msg-detail-status--read {
    background: rgba(34, 197, 94, 0.1);
    color: #16a34a;
  }

  .msg-detail-status--unread {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
  }

  .msg-detail-content {
    font-size: 15px;
    line-height: 1.8;
    color: #1f2937;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .msg-detail-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 24px !important;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
  }

  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 10px 20px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn--primary {
    background: #3b82f6;
    border: none;
    color: #fff;
  }

  .btn--primary:hover:not(:disabled) {
    background: #2563eb;
  }

  .btn--primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn--ghost {
    background: transparent;
    border: 1.5px solid rgba(0, 0, 0, 0.15);
    color: #374151;
  }

  .btn--ghost:hover {
    background: rgba(0, 0, 0, 0.04);
    border-color: rgba(0, 0, 0, 0.25);
  }

  .nav-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 22px;
    height: 22px;
    padding: 0 6px;
    margin-left: 12px;
    border-radius: 999px;
    background: #ef4444;
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    flex-shrink: 0;
  }

  /* Hover invert (match profile cards) */
  .news-choice__card:hover .news-choice__card-title {
    color: #ffffff;
  }

  .news-choice__card:hover .news-choice__card-sub {
    color: rgba(255, 255, 255, 0.72);
  }

  .news-choice__card:hover .news-choice__icon {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.12);
    border-color: rgba(255, 255, 255, 0.22);
  }

  .news-choice__card:hover .news-choice__action {
    color: rgba(255, 255, 255, 0.86);
  }

  .news-choice__card:hover .news-choice__action-badge {
    background: rgba(255, 255, 255, 0.14);
    border-color: rgba(255, 255, 255, 0.22);
    color: #ffffff;
  }

  .news-switch {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 2px 0 16px;
    border-bottom: 1px solid rgba(15, 23, 42, 0.10);
    margin-bottom: 16px;
  }

  .news-switch__btn {
    height: 34px;
    padding: 0 12px;
    border-radius: 999px;
    border: 1px solid rgba(15, 23, 42, 0.12);
    background: rgba(255,255,255,0.7);
    cursor: pointer;
    font-weight: 900;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(15, 23, 42, 0.82);
    transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
  }

  .news-switch__btn.active {
    background: #000000;
    border-color: #000000;
    color: #ffffff;
  }

  .news-switch__back {
    margin-left: auto;
    height: 34px;
    padding: 0 12px;
    border-radius: 999px;
    border: 1px solid rgba(15, 23, 42, 0.12);
    background: transparent;
    cursor: pointer;
    font-weight: 900;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(15, 23, 42, 0.72);
  }

  .news-switch__back:hover {
    background: rgba(15, 23, 42, 0.06);
  }

  /* keep them horizontal when possible; wrap naturally on narrow screens */
  
  .nav-text {
    display: block;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.02em;
  }
  
  .nav-desc {
    display: block;
    margin-top: 6px;
    font-size: 12px;
    opacity: 0.75;
  }
  
  .sidebar-footer {
    margin-top: auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .ghost-btn {
    width: 100%;
    border: 1px solid rgba(0, 0, 0, 0.1);
    background: rgba(255, 255, 255, 0.5);
    border-radius: 999px;
    padding: 12px 14px;
    font-weight: 800;
    letter-spacing: 0.04em;
    cursor: pointer;
    color: #0f172a;
    transition: all 0.3s ease;
  }
  
  .ghost-btn:hover,
  .ghost-btn:active {
    transform: translateY(-1px);
    box-shadow: 0 14px 35px rgba(0, 0, 0, 0.1);
    background: #0f172a;
    color: #ffffff;
    border-color: #0f172a;
  }
  
  /* Content */
  .content {
    padding: clamp(32px, 5vw, 72px);
    padding-left: clamp(80px, 8vw, 120px); /* 给汉堡菜单留空间 */
    display: flex;
    flex-direction: column;
    gap: 0px;
    min-height: 100vh;
    position: relative;
  }

  /* 装饰光晕 */
  .content::before {
    content: '';
    position: fixed;
    top: 10%;
    right: 5%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
  }

  .content::after {
    content: '';
    position: fixed;
    bottom: 15%;
    left: 10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(236, 72, 153, 0.06) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
  }
  
  .content-header {
    max-width: 920px;
    margin: 0 auto;
    width: 100%;
    position: relative;
    z-index: 1;
    padding-bottom: 24px;
    margin-bottom: 8px;
  }
  
  .content-title {
    margin-left: 20px;
    margin-top: 20px;
    font-size: 42px;
    line-height: 1.1;
    color: #0f172a;
    letter-spacing: -0.02em;
    font-weight: 900;
    background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .content-subtitle {
    margin-top: 14px;
    margin-left: 20px;
    color: #64748b;
    font-size: 16px;
    letter-spacing: 0.01em;
    font-weight: 500;
  }
  
  /* Panel（右侧内容卡片） */
  .panel {
    width: min(980px, 100%);
    margin: 0 auto;
    position: relative;
    z-index: 1;
  }
  
  .panel-inner {
    border-radius: 24px;
    background: rgba(255,255,255,0.70);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0,0,0,0.08);
    padding: 28px 28px;
    box-shadow: 0 22px 60px rgba(0,0,0,0.08);
  }

  /* News publish form now lives in `src/components/NewsPublishForm.vue` */
  
  /* Dominate 占位 */
  .placeholder {
    padding: 6px 2px;
  }
  
  .placeholder-title {
    font-size: 18px;
    font-weight: 900;
    letter-spacing: 0.06em;
    color: #0f172a;
  }
  
  .placeholder-text {
    margin-top: 10px;
    font-size: 14px;
    color: #374151;
    line-height: 1.7;
  }
  
  .placeholder-hint {
    margin-top: 12px;
    font-size: 12px;
    color: #6b7280;
    letter-spacing: 0.02em;
  }
  
  .profile-cards {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 14px;
    padding: 6px 2px;
  }

  .profile-cards .info-card {
    width: 100%;
    max-width: 900px;
  }

  .info-card {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 20px;
    border-radius: 18px;
    background: rgba(255,255,255,0.78);
    border: none;
    box-shadow: 0 12px 30px rgba(0,0,0,0.06);
    position: relative;
    overflow: hidden;
    z-index: 1;
    transition: transform 0.2s ease, box-shadow 0.3s ease, color 0.3s ease;
  }

  /* 黑色填充层 */
  .info-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.92);
    transform: scaleX(0);
    transform-origin: right center;
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: -1;
    border-radius: 18px;
  }

  .info-card:hover::before {
    transform: scaleX(1);
    transform-origin: left center;
  }

  /* 鼠标离开时从右向左收回 */
  .info-card:not(:hover)::before {
    transform-origin: right center;
  }

  /* Button reset for clickable cards */
  .info-card--action {
    width: 100%;
    text-align: left;
    cursor: pointer;
    font: inherit;
    color: inherit;
  }

  .info-card--action:focus-visible {
    outline: 3px solid rgba(26, 115, 232, 0.35);
    outline-offset: 3px;
  }

  .info-card--action:disabled,
  .info-card--action.info-card--disabled {
    cursor: not-allowed;
    opacity: 0.55;
  }

  .info-card--action:disabled:hover,
  .info-card--action.info-card--disabled:hover {
    transform: none;
    box-shadow: none;
  }

  .info-action {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
    color: rgba(15, 23, 42, 0.62);
    font-weight: 800;
    letter-spacing: 0.02em;
  }

  .info-action-badge {
    width: 36px;
    height: 36px;
    border-radius: 999px;
    border: 1px solid rgba(0,0,0,0.10);
    background: rgba(255,255,255,0.6);
    display: grid;
    place-items: center;
  }

  .info-icon {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #111827;
    background: rgba(255,255,255,0.7);
    border: 1px solid rgba(0,0,0,0.06);
    flex-shrink: 0;
  }

  .info-body {
    flex: 1;
    min-width: 0;
  }

  .info-title {
    font-size: 16px;
    font-weight: 900;
    letter-spacing: 0.02em;
    color: #0f172a;
  }

  .info-sub {
    margin-top: 6px;
    font-size: 13px;
    color: #6b7280;
    line-height: 1.45;
  }

  .info-value {
    margin-top: 6px;
    font-size: 14px;
    font-weight: 500;
    color: gray;
    letter-spacing: 0.02em;
  }

  .avatar {
    width: 58px;
    height: 58px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 900;
    color: #fff;
    background: #1a73e8;
    flex-shrink: 0;
    position: relative;
    overflow: hidden;
  }

  .avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .avatar-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.5);
    color: #ffffff;
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .info-card--action:hover .avatar-overlay,
  .info-card--action.uploading .avatar-overlay {
    opacity: 1;
  }

  .info-card--action.uploading {
    pointer-events: none;
    opacity: 0.7;
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  .info-card:hover {
    transform: translateY(-2px);
    color: #ffffff;
    box-shadow: 0 18px 45px rgba(0,0,0,0.16);
  }

  /* 子元素跟随反转 */
  .info-card:hover .info-title,
  .info-card:hover .info-value {
    color: #ffffff;
  }

  .info-card:hover .info-sub {
    color: rgba(255,255,255,0.72);
  }

  .info-card:hover .info-icon {
    color: #ffffff;
    background: rgba(255,255,255,0.12);
    border-color: rgba(255,255,255,0.22);
  }

  .info-card:hover .info-action {
    color: rgba(255,255,255,0.86);
  }

  .info-card:hover .info-action-badge {
    background: rgba(255,255,255,0.14);
    border-color: rgba(255,255,255,0.22);
    color: #ffffff;
  }

  /* Modal */
  .modal-layer {
    position: fixed;
    inset: 0;
    z-index: 50;
    display: grid;
    place-items: center;
    padding: 20px;
  }

  .modal-backdrop {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }

  .modal {
    position: relative;
    width: min(480px, 92%);
    border-radius: 28px;
    background: #ffffff;
    border: none;
    box-shadow: 
      0 0 0 1px rgba(0, 0, 0, 0.05),
      0 40px 100px rgba(0, 0, 0, 0.25),
      0 10px 40px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    animation: modalSlideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  }

  @keyframes modalSlideIn {
    from {
      opacity: 0;
      transform: translateY(20px) scale(0.96);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 28px 28px 0 28px;
  }

  .modal-title {
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #0f172a;
    text-transform: none;
  }

  .modal-close {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: none;
    background: rgba(0, 0, 0, 0.05);
    color: #64748b;
    display: grid;
    place-items: center;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .modal-close:hover {
    background: rgba(0, 0, 0, 0.9);
    color: #ffffff;
    transform: rotate(90deg);
  }

  .modal-body {
    padding: 24px 28px 28px 28px;
  }

  .modal-label {
    display: block;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.01em;
    color: #64748b;
    margin-bottom: 12px;
  }

  .modal-input {
    width: 100%;
    height: 56px;
    border-radius: 16px;
    border: 2px solid rgba(0, 0, 0, 0.08);
    background: #f8fafc;
    padding: 0 20px;
    font-size: 16px;
    font-weight: 500;
    color: #0f172a;
    outline: none;
    transition: all 0.25s ease;
  }

  .modal-input:focus {
    border-color: #0f172a;
    background: #ffffff;
    box-shadow: 0 0 0 4px rgba(15, 23, 42, 0.08);
  }

  .modal-input::placeholder {
    color: #94a3b8;
  }

  .modal-error {
    margin-top: 12px;
    padding: 12px 16px;
    border-radius: 12px;
    background: rgba(239, 68, 68, 0.08);
    font-size: 13px;
    color: #dc2626;
    font-weight: 600;
  }

  .modal-actions {
    display: flex;
    gap: 12px;
    padding: 0 28px 28px 28px;
  }

  .modal-btn {
    flex: 1;
    height: 52px;
    border-radius: 14px;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.01em;
    cursor: pointer;
    border: 2px solid rgba(0, 0, 0, 0.08);
    background: #ffffff;
    color: #374151;
    transition: all 0.25s ease;
  }

  .modal-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    border-color: rgba(0, 0, 0, 0.15);
  }

  .modal-btn:active {
    transform: translateY(0);
  }

  .modal-btn.primary {
    background: #0f172a;
    border-color: #0f172a;
    color: #ffffff;
  }

  .modal-btn.primary:hover {
    background: #1e293b;
    border-color: #1e293b;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.3);
  }

  .date-row {
    display: grid;
    grid-template-columns: 1.2fr 1fr 1fr;
    gap: 12px;
  }

  .modal-select {
    width: 100%;
    height: 56px;
    border-radius: 16px;
    border: 2px solid rgba(0, 0, 0, 0.08);
    background: #f8fafc;
    padding: 0 16px;
    font-size: 16px;
    font-weight: 500;
    color: #0f172a;
    outline: none;
    cursor: pointer;
    transition: all 0.25s ease;
    appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 16px center;
  }

  .modal-select:focus {
    border-color: #0f172a;
    background: #ffffff;
    box-shadow: 0 0 0 4px rgba(15, 23, 42, 0.08);
  }

  /* 头像也做反转 */
  .info-card:hover .avatar {
    background: #ffffff;
    color: #000000;
  }

  /* Stepper（浅色毛玻璃主题） */
  .stepper-wrapper {
    margin-bottom: 12px;
    margin-left: 12px;
  }

  .stepper {
    padding: 2px 0;
  }

  .stepper-step {
    display: flex;
    gap: 12px;
    position: relative;
    margin-bottom: 16px;
  }

  .stepper-step:last-child {
    margin-bottom: 0;
  }

  .stepper-line {
    position: absolute;
    left: 15px;
    top: 34px;
    bottom: -16px;
    width: 2px;
    background: rgba(15, 23, 42, 0.12);
  }

  .stepper-step:last-child .stepper-line {
    display: none;
  }

  .stepper-circle {
    width: 32px;
    height: 32px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    z-index: 1;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.02em;
  }

  /* 三态：done / active / pending */
  .stepper-step.is-done .stepper-circle {
    background: #0f172a;
    color: #ffffff;
  }

  .stepper-step.is-active .stepper-circle {
    background: rgba(255, 255, 255, 0.7);
    border: 2px solid #0f172a;
    color: #0f172a;
  }

  .stepper-step.is-pending .stepper-circle {
    background: rgba(255, 255, 255, 0.5);
    border: 2px solid rgba(15, 23, 42, 0.15);
    color: rgba(15, 23, 42, 0.45);
  }

  .stepper-content {
    min-width: 0;
    padding-top: 2px;
  }

  .stepper-title {
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 0.06em;
    color: #0f172a;
  }

  .stepper-sub {
    margin-top: 4px;
    font-size: 12px;
    color: rgba(15, 23, 42, 0.6);
    line-height: 1.35;
  }

  /* pending 文案更淡 */
  .stepper-step.is-pending .stepper-title {
    color: rgba(15, 23, 42, 0.5);
  }

  .stepper-step.is-pending .stepper-sub {
    color: rgba(15, 23, 42, 0.4);
  }

  /* 通用浮现：黑白风格（不抢 hover 的质感） */
  .float-in {
    opacity: 0;
    transform: translate3d(0, 18px, 0);
    filter: blur(6px);
    transition:
      opacity 0.65s cubic-bezier(0.25, 0.46, 0.45, 0.94),
      transform 0.65s cubic-bezier(0.25, 0.46, 0.45, 0.94),
      filter 0.65s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    transition-delay: var(--d, 0ms);
    will-change: opacity, transform, filter;
  }

  .float-in.animate {
    opacity: 1;
    transform: translate3d(0, 0, 0);
    filter: blur(0);
  }

  @media (max-width: 900px) {
    .bg-video-right { display: none; }
    .sidebar { width: min(320px, calc(100vw - 24px)); padding: 28px 20px; }
    .content { min-width: 0; padding: 104px 16px 56px; }
    .content::before, .content::after { width: 220px; height: 220px; }
    .content-header { padding-bottom: 18px; }
    .content-title { margin: 0; font-size: clamp(34px, 10vw, 44px); }
    .content-subtitle { margin: 10px 0 0; font-size: 15px; }
    .panel, .panel-inner { width: 100%; min-width: 0; }
    .panel-inner { padding: 20px 16px; border-radius: 18px; }
    .info-card { align-items: flex-start; padding: 16px; }
    .info-value, .info-sub { overflow-wrap: anywhere; }
    .msg-filter-tabs { width: 100%; overflow-x: auto; }
    .msg-filter-tab { flex: 1 0 auto; min-height: 44px; }
    .msg-item { padding: 16px 14px; }
    .msg-item-header, .msg-item-footer { align-items: flex-start; flex-direction: column; gap: 10px; }
    .msg-item-actions { width: 100%; flex-wrap: wrap; }
    .msg-item-action, .msg-item-delete { min-height: 40px; }
    .modal-layer { padding: 16px; }
    .modal { width: 100%; max-height: calc(100svh - 32px); padding: 22px 18px; }
    .modal-actions { align-items: stretch; flex-direction: column-reverse; }
    .modal-btn { width: 100%; min-height: 44px; }
    .date-row { grid-template-columns: minmax(0, 1fr); gap: 12px; }
    .stepper-content { min-width: 0; }
  }

  @media (prefers-reduced-motion: reduce) {
    .float-in {
      transition: none;
    opacity: 1;
      transform: none;
      filter: none;
    }
  }
  </style>
