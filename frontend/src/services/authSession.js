let refreshPromise = null
let tokenRefreshHandler = null
let refreshFailureHandler = null

export function getStoredToken() {
  return localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || ''
}

export function getStoredRefreshToken() {
  return localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token') || ''
}

export function getActiveStorage() {
  return localStorage.getItem('remember_me') === 'true' ? localStorage : sessionStorage
}

export function setAuthSessionHandlers({ onTokenRefresh, onRefreshFailure } = {}) {
  tokenRefreshHandler = onTokenRefresh || null
  refreshFailureHandler = onRefreshFailure || null
}

function persistTokenPair(data) {
  const storage = getActiveStorage()
  const now = Date.now()
  if (data?.access_token) storage.setItem('access_token', data.access_token)
  if (data?.refresh_token) storage.setItem('refresh_token', data.refresh_token)
  if (data?.token_type) storage.setItem('token_type', data.token_type)
  if (data?.access_expires_in) {
    storage.setItem('access_token_expires_at', String(now + Number(data.access_expires_in) * 1000))
  }
  if (data?.refresh_expires_in) {
    storage.setItem('refresh_token_expires_at', String(now + Number(data.refresh_expires_in) * 1000))
  }
}

export async function refreshAccessToken() {
  if (refreshPromise) return refreshPromise

  refreshPromise = (async () => {
    const refreshToken = String(getStoredRefreshToken() || '').trim()
    if (!refreshToken) return null

    const response = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    const data = await response.json().catch(() => null)
    if (!response.ok || !data?.access_token || !data?.refresh_token) {
      const error = new Error(data?.detail || `Refresh failed (${response.status})`)
      error.status = response.status
      throw error
    }

    persistTokenPair(data)
    tokenRefreshHandler?.(data)
    return data
  })()

  try {
    return await refreshPromise
  } catch (error) {
    refreshFailureHandler?.(error)
    return null
  } finally {
    refreshPromise = null
  }
}
