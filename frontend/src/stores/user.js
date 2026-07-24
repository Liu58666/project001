import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { refreshAccessToken as refreshSessionToken, setAuthSessionHandlers } from '@/services/authSession'

export const useUserStore = defineStore('user', () => {
  // 状态
  const accessToken = ref(localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token') || '')
  const tokenType = ref(localStorage.getItem('token_type') || sessionStorage.getItem('token_type') || 'bearer')
  const username = ref(localStorage.getItem('username') || sessionStorage.getItem('username') || '')
  const createdAt = ref(localStorage.getItem('created_at') || sessionStorage.getItem('created_at') || '')
  const updatedAt = ref(localStorage.getItem('updated_at') || sessionStorage.getItem('updated_at') || '')
  // 用户资料（可编辑）
  const displayName = ref(localStorage.getItem('display_name') || sessionStorage.getItem('display_name') || '')
  const phone = ref(localStorage.getItem('phone') || sessionStorage.getItem('phone') || '')
  const email = ref(localStorage.getItem('email') || sessionStorage.getItem('email') || '')
  const birthday = ref(localStorage.getItem('birthday') || sessionStorage.getItem('birthday') || '')
  const photo = ref(localStorage.getItem('photo') || sessionStorage.getItem('photo') || '')
  const rememberMe = ref(localStorage.getItem('remember_me') === 'true')
  
  // Token 过期时间（时间戳）
  const accessTokenExpiresAt = ref(parseInt(localStorage.getItem('access_token_expires_at') || sessionStorage.getItem('access_token_expires_at') || '0'))
  const refreshTokenExpiresAt = ref(parseInt(localStorage.getItem('refresh_token_expires_at') || sessionStorage.getItem('refresh_token_expires_at') || '0'))

  // 计算属性
  const isLoggedIn = computed(() => !!accessToken.value && !isAccessTokenExpired.value)
  // Keep i18n out of store; let UI decide the localized fallback text
  const displayNameText = computed(() => displayName.value || username.value || '')
  
  // 检查 token 是否过期
  const isAccessTokenExpired = computed(() => {
    if (!accessTokenExpiresAt.value) return false
    return Date.now() >= accessTokenExpiresAt.value
  })
  
  const isRefreshTokenExpired = computed(() => {
    if (!refreshTokenExpiresAt.value) return false
    return Date.now() >= refreshTokenExpiresAt.value
  })

  function decodeJwtPayload(token) {
    try {
      const [, payload] = String(token || '').split('.')
      if (!payload) return null
      const json = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
      return json && typeof json === 'object' ? json : null
    } catch {
      return null
    }
  }

  function inferExpiresAtFromJwt(token) {
    const payload = decodeJwtPayload(token)
    const exp = payload?.exp
    if (!exp) return 0
    const ms = Number(exp) * 1000
    return Number.isFinite(ms) ? ms : 0
  }

  // 获取当前使用的存储方式
  const getStorage = () => {
    return rememberMe.value ? localStorage : sessionStorage
  }

  const isRefreshing = ref(false)
  let refreshTimerId = null

  async function postJson(path, body) {
    const res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    let data = null
    try {
      data = await res.json()
    } catch {
      data = null
    }

    if (!res.ok) {
      const msg =
        data?.detail ||
        data?.message ||
        (typeof data === 'string' ? data : null) ||
        `Request failed (${res.status})`
      const err = new Error(msg)
      err.status = res.status
      throw err
    }
    return data
  }

  async function refreshAccessToken() {
    if (isRefreshing.value) return false
    if (!String(refreshToken.value || '').trim()) return false
    if (isRefreshTokenExpired.value) return false

    isRefreshing.value = true
    try {
      return Boolean(await refreshSessionToken())
    } finally {
      isRefreshing.value = false
    }
  }

  function clearRefreshTimer() {
    if (refreshTimerId) {
      clearTimeout(refreshTimerId)
      refreshTimerId = null
    }
  }

  function scheduleTokenRefresh() {
    clearRefreshTimer()
    const at = accessToken.value
    if (!at) return
    if (!refreshToken.value) return
    if (isRefreshTokenExpired.value) return

    // Refresh 60s before expiry (fallback to JWT exp if needed)
    const expMs = accessTokenExpiresAt.value || inferExpiresAtFromJwt(at)
    if (!expMs) return

    const leadMs = 60 * 1000
    const delay = Math.max(5 * 1000, expMs - Date.now() - leadMs)
    refreshTimerId = setTimeout(() => {
      refreshAccessToken()
    }, delay)
  }

  // 登录：保存 token 和用户信息
  function login(tokenData, userData, remember = false) {
    const storage = remember ? localStorage : sessionStorage
    
    // 清除之前的存储（如果切换了 remember 状态）
    if (remember !== rememberMe.value) {
      const oldStorage = remember ? sessionStorage : localStorage
      oldStorage.removeItem('access_token')
      oldStorage.removeItem('refresh_token')
      oldStorage.removeItem('token_type')
      oldStorage.removeItem('access_token_expires_at')
      oldStorage.removeItem('refresh_token_expires_at')
      oldStorage.removeItem('username')
      oldStorage.removeItem('created_at')
      oldStorage.removeItem('display_name')
      oldStorage.removeItem('phone')
      oldStorage.removeItem('email')
      oldStorage.removeItem('birthday')
      oldStorage.removeItem('photo')
    }

    // 保存 token 数据
    if (tokenData?.access_token) {
      accessToken.value = tokenData.access_token
      storage.setItem('access_token', tokenData.access_token)
    }
    if (tokenData?.refresh_token) {
      refreshToken.value = tokenData.refresh_token
      storage.setItem('refresh_token', tokenData.refresh_token)
    }
    if (tokenData?.token_type) {
      tokenType.value = tokenData.token_type
      storage.setItem('token_type', tokenData.token_type)
    }
    
    // 计算并保存 token 过期时间
    const now = Date.now()
    if (tokenData?.access_expires_in) {
      const expiresAt = now + (tokenData.access_expires_in * 1000)
      accessTokenExpiresAt.value = expiresAt
      storage.setItem('access_token_expires_at', expiresAt.toString())
    } else if (tokenData?.access_token) {
      const expMs = inferExpiresAtFromJwt(tokenData.access_token)
      if (expMs) {
        accessTokenExpiresAt.value = expMs
        storage.setItem('access_token_expires_at', expMs.toString())
      }
    }
    if (tokenData?.refresh_expires_in) {
      const expiresAt = now + (tokenData.refresh_expires_in * 1000)
      refreshTokenExpiresAt.value = expiresAt
      storage.setItem('refresh_token_expires_at', expiresAt.toString())
    } else if (tokenData?.refresh_token) {
      const expMs = inferExpiresAtFromJwt(tokenData.refresh_token)
      if (expMs) {
        refreshTokenExpiresAt.value = expMs
        storage.setItem('refresh_token_expires_at', expMs.toString())
      }
    }
    
    // 保存用户数据
    if (userData?.username) {
      username.value = userData.username
      storage.setItem('username', userData.username)
    }
    if (userData?.created_at) {
      createdAt.value = userData.created_at
      storage.setItem('created_at', userData.created_at)
    }
    if (userData?.updated_at) {
      updatedAt.value = userData.updated_at
      storage.setItem('updated_at', userData.updated_at)
    }
    if (userData?.display_name != null) {
      displayName.value = String(userData.display_name || '')
      storage.setItem('display_name', displayName.value)
    }
    if (userData?.phone != null) {
      phone.value = String(userData.phone || '')
      storage.setItem('phone', phone.value)
    }
    if (userData?.email != null) {
      email.value = String(userData.email || '')
      storage.setItem('email', email.value)
    }
    if (userData?.birthday != null) {
      birthday.value = String(userData.birthday || '')
      storage.setItem('birthday', birthday.value)
    }
    if (userData?.photo != null) {
      photo.value = String(userData.photo || '')
      storage.setItem('photo', photo.value)
    }

    rememberMe.value = remember
    if (remember) {
      localStorage.setItem('remember_me', 'true')
    } else {
      localStorage.removeItem('remember_me')
    }

    scheduleTokenRefresh()
  }

  // 登出：清除所有数据
  function logout() {
    clearRefreshTimer()
    accessToken.value = ''
    refreshToken.value = ''
    tokenType.value = 'bearer'
    username.value = ''
    createdAt.value = ''
    updatedAt.value = ''
    displayName.value = ''
    phone.value = ''
    email.value = ''
    birthday.value = ''
    photo.value = ''
    accessTokenExpiresAt.value = 0
    refreshTokenExpiresAt.value = 0
    
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('token_type')
    localStorage.removeItem('access_token_expires_at')
    localStorage.removeItem('refresh_token_expires_at')
    localStorage.removeItem('username')
    localStorage.removeItem('created_at')
    localStorage.removeItem('updated_at')
    localStorage.removeItem('display_name')
    localStorage.removeItem('phone')
    localStorage.removeItem('email')
    localStorage.removeItem('birthday')
    localStorage.removeItem('photo')
    localStorage.removeItem('remember_me')
    
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('refresh_token')
    sessionStorage.removeItem('token_type')
    sessionStorage.removeItem('access_token_expires_at')
    sessionStorage.removeItem('refresh_token_expires_at')
    sessionStorage.removeItem('username')
    sessionStorage.removeItem('created_at')
    sessionStorage.removeItem('updated_at')
    sessionStorage.removeItem('display_name')
    sessionStorage.removeItem('phone')
    sessionStorage.removeItem('email')
    sessionStorage.removeItem('birthday')
    sessionStorage.removeItem('photo')
  }

  // 更新 token（用于刷新 token）
  function updateToken(tokenData) {
    const storage = getStorage()
    const now = Date.now()
    
    if (tokenData?.access_token) {
      accessToken.value = tokenData.access_token
      storage.setItem('access_token', tokenData.access_token)
    }
    if (tokenData?.refresh_token) {
      refreshToken.value = tokenData.refresh_token
      storage.setItem('refresh_token', tokenData.refresh_token)
    }
    if (tokenData?.token_type) {
      tokenType.value = tokenData.token_type
      storage.setItem('token_type', tokenData.token_type)
    }
    
    // 更新过期时间
    if (tokenData?.access_expires_in) {
      const expiresAt = now + (tokenData.access_expires_in * 1000)
      accessTokenExpiresAt.value = expiresAt
      storage.setItem('access_token_expires_at', expiresAt.toString())
    } else if (tokenData?.access_token) {
      const expMs = inferExpiresAtFromJwt(tokenData.access_token)
      if (expMs) {
        accessTokenExpiresAt.value = expMs
        storage.setItem('access_token_expires_at', expMs.toString())
      }
    }
    if (tokenData?.refresh_expires_in) {
      const expiresAt = now + (tokenData.refresh_expires_in * 1000)
      refreshTokenExpiresAt.value = expiresAt
      storage.setItem('refresh_token_expires_at', expiresAt.toString())
    } else if (tokenData?.refresh_token) {
      const expMs = inferExpiresAtFromJwt(tokenData.refresh_token)
      if (expMs) {
        refreshTokenExpiresAt.value = expMs
        storage.setItem('refresh_token_expires_at', expMs.toString())
      }
    }

    scheduleTokenRefresh()
  }

  // 初始化：从存储中恢复状态
  async function init() {
    const storage = getStorage()
    accessToken.value = storage.getItem('access_token') || ''
    refreshToken.value = storage.getItem('refresh_token') || ''
    tokenType.value = storage.getItem('token_type') || 'bearer'
    username.value = storage.getItem('username') || ''
    createdAt.value = storage.getItem('created_at') || ''
    updatedAt.value = storage.getItem('updated_at') || ''
    displayName.value = storage.getItem('display_name') || ''
    phone.value = storage.getItem('phone') || ''
    email.value = storage.getItem('email') || ''
    birthday.value = storage.getItem('birthday') || ''
    photo.value = storage.getItem('photo') || ''
    accessTokenExpiresAt.value = parseInt(storage.getItem('access_token_expires_at') || '0')
    refreshTokenExpiresAt.value = parseInt(storage.getItem('refresh_token_expires_at') || '0')
    
    // 如果 token 已过期，清除它
    const now = Date.now()
    if (accessTokenExpiresAt.value && now >= accessTokenExpiresAt.value) {
      // Try refresh if possible; otherwise clear access token
      if (refreshToken.value && !isRefreshTokenExpired.value) {
        // Wait before mounting so a valid session never flashes to the login view.
        await refreshAccessToken()
      } else {
        accessToken.value = ''
        storage.removeItem('access_token')
        accessTokenExpiresAt.value = 0
        storage.removeItem('access_token_expires_at')
      }
    }
    if (refreshTokenExpiresAt.value && now >= refreshTokenExpiresAt.value) {
      refreshToken.value = ''
      storage.removeItem('refresh_token')
      refreshTokenExpiresAt.value = 0
      storage.removeItem('refresh_token_expires_at')
    }

    scheduleTokenRefresh()
  }

  setAuthSessionHandlers({
    onTokenRefresh: (data) => updateToken(data),
    onRefreshFailure: (error) => {
      if (error?.status === 401) logout()
    },
  })

  // 更新用户资料（并写回当前存储：localStorage 或 sessionStorage）
  function setProfileFields(patch = {}) {
    const storage = getStorage()

    if (patch.displayName != null) {
      displayName.value = String(patch.displayName || '')
      storage.setItem('display_name', displayName.value)
    }
    if (patch.phone != null) {
      phone.value = String(patch.phone || '')
      storage.setItem('phone', phone.value)
    }
    if (patch.email != null) {
      email.value = String(patch.email || '')
      storage.setItem('email', email.value)
    }
    if (patch.birthday != null) {
      birthday.value = String(patch.birthday || '')
      storage.setItem('birthday', birthday.value)
    }
    if (patch.photo != null) {
      photo.value = String(patch.photo || '')
      storage.setItem('photo', photo.value)
    }
    if (patch.updatedAt != null) {
      updatedAt.value = String(patch.updatedAt || '')
      storage.setItem('updated_at', updatedAt.value)
    }
  }

  return {
    // 状态
    accessToken,
    refreshToken,
    tokenType,
    username,
    createdAt,
    updatedAt,
    displayName,
    phone,
    email,
    birthday,
    photo,
    rememberMe,
    accessTokenExpiresAt,
    refreshTokenExpiresAt,
    isRefreshing,
    // 计算属性
    isLoggedIn,
    displayNameText,
    isAccessTokenExpired,
    isRefreshTokenExpired,
    // 方法
    login,
    logout,
    updateToken,
    init,
    getStorage,
    setProfileFields,
    refreshAccessToken,
  }
})
