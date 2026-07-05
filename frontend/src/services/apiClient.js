// src/services/apiClient.js
// Shared API client with:
// - Bearer auth from storage
// - 401/403 auto refresh once then retry
// - JSON + multipart(FormData) support

function getStoredToken() {
  return localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || ''
}

function getStoredRefreshToken() {
  return localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token') || ''
}

function getActiveStorage() {
  return localStorage.getItem('remember_me') === 'true' ? localStorage : sessionStorage
}

async function tryRefreshAccessToken() {
  const rt = String(getStoredRefreshToken() || '').trim()
  if (!rt) return false

  const res = await fetch('/api/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: rt }),
  })

  let data = null
  try {
    data = await res.json()
  } catch {
    data = null
  }

  if (!res.ok) return false

  const access = data?.access_token
  const refresh = data?.refresh_token
  const tokenType = data?.token_type
  const accessExpIn = data?.access_expires_in
  const refreshExpIn = data?.refresh_expires_in

  const storage = getActiveStorage()
  if (access) storage.setItem('access_token', access)
  if (refresh) storage.setItem('refresh_token', refresh)
  if (tokenType) storage.setItem('token_type', tokenType)

  const now = Date.now()
  if (accessExpIn) storage.setItem('access_token_expires_at', String(now + Number(accessExpIn) * 1000))
  if (refreshExpIn) storage.setItem('refresh_token_expires_at', String(now + Number(refreshExpIn) * 1000))

  return true
}

async function parseResponse(res) {
  if (res.status === 204 || res.status === 205) return null

  const contentLength = res.headers.get('content-length')
  if (contentLength === '0') return null

  const contentType = String(res.headers.get('content-type') || '').toLowerCase()
  const text = await res.text().catch(() => '')
  if (!text) return null

  if (contentType.includes('application/json')) return JSON.parse(text)
  return text
}

async function requestOnce(method, urlString, { token, jsonBody, formData, extraHeaders } = {}) {
  const headers = {
    Accept: 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(jsonBody ? { 'Content-Type': 'application/json' } : {}),
    ...(extraHeaders || {}),
  }

  return await fetch(urlString, {
    method,
    headers,
    ...(jsonBody ? { body: JSON.stringify(jsonBody) } : {}),
    ...(formData ? { body: formData } : {}),
  })
}

/**
 * Unified API request helper.
 * - For JSON: pass { body }
 * - For multipart: pass { formData }
 */
export async function apiRequest(method, path, { params, body, formData, headers } = {}) {
  const m = String(method || 'GET').toUpperCase()

  const url = new URL(path, window.location.origin)
  if (params && m === 'GET') {
    for (const [k, v] of Object.entries(params)) {
      if (v === undefined || v === null || v === '') continue
      url.searchParams.set(k, String(v))
    }
  }

  const token = getStoredToken()
  let res = await requestOnce(m, url.toString(), {
    token,
    jsonBody: body,
    formData,
    extraHeaders: headers,
  })

  // Auto refresh once on 401/403 and retry (only if we had a token to begin with).
  if ((res.status === 401 || res.status === 403) && token) {
    const ok = await tryRefreshAccessToken()
    if (ok) {
      const token2 = getStoredToken()
      res = await requestOnce(m, url.toString(), {
        token: token2,
        jsonBody: body,
        formData,
        extraHeaders: headers,
      })
    }
  }

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    const err = new Error(text || `Request failed (${res.status})`)
    err.status = res.status
    throw err
  }

  return await parseResponse(res)
}


