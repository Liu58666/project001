// src/services/newsService.js
// Real API (proxied in dev by vite.config.js: /api -> http://127.0.0.1:8000)

function getStoredToken() {
  // Keep service decoupled from Pinia store: read from storage directly
  return (
    localStorage.getItem('access_token') ||
    sessionStorage.getItem('access_token') ||
    ''
  )
}

function getStoredRefreshToken() {
  return (
    localStorage.getItem('refresh_token') ||
    sessionStorage.getItem('refresh_token') ||
    ''
  )
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

  const storage =
    localStorage.getItem('remember_me') === 'true' ? localStorage : sessionStorage

  if (access) storage.setItem('access_token', access)
  if (refresh) storage.setItem('refresh_token', refresh)
  if (tokenType) storage.setItem('token_type', tokenType)

  const now = Date.now()
  if (accessExpIn) storage.setItem('access_token_expires_at', String(now + Number(accessExpIn) * 1000))
  if (refreshExpIn) storage.setItem('refresh_token_expires_at', String(now + Number(refreshExpIn) * 1000))

  return true
}

async function apiRequest(method, path, { params, body } = {}) {
  const url = new URL(path, window.location.origin)
  if (params && method.toUpperCase() === 'GET') {
    for (const [k, v] of Object.entries(params)) {
      if (v === undefined || v === null || v === '') continue
      url.searchParams.set(k, String(v))
    }
  }

  const token = getStoredToken()

  const doFetch = async () =>
    await fetch(url.toString(), {
    method,
    headers: {
      Accept: 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
    })

  let res = await doFetch()

  // Auto refresh once on 401/403 and retry.
  if ((res.status === 401 || res.status === 403) && token) {
    const ok = await tryRefreshAccessToken()
    if (ok) {
      const token2 = getStoredToken()
      res = await fetch(url.toString(), {
        method,
        headers: {
          Accept: 'application/json',
          ...(token2 ? { Authorization: `Bearer ${token2}` } : {}),
          ...(body ? { 'Content-Type': 'application/json' } : {}),
        },
        ...(body ? { body: JSON.stringify(body) } : {}),
      })
    }
  }

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Request failed (${res.status})`)
  }

  // 204/205 means "No Content" by definition
  if (res.status === 204 || res.status === 205) return null

  // Some endpoints may still return empty body with 200/201
  const contentLength = res.headers.get('content-length')
  if (contentLength === '0') return null

  const contentType = String(res.headers.get('content-type') || '').toLowerCase()
  if (!contentType.includes('application/json')) {
    // keep behavior predictable: return text for non-json success responses
    const text = await res.text().catch(() => '')
    return text || null
  }

  // JSON success response
  const text = await res.text().catch(() => '')
  if (!text) return null
  return JSON.parse(text)
}

function normalizeNewsList(data) {
  if (Array.isArray(data)) return data
  // Some backends return a single object for "latest" or when filtered by slug
  if (data && typeof data === 'object' && (data.slug || data.id)) return [data]
  if (Array.isArray(data?.items)) return data.items
  if (Array.isArray(data?.results)) return data.results
  if (Array.isArray(data?.data)) return data.data
  return []
}

export async function listNews({ limit = 50, offset = 0, slug } = {}) {
  const data = await apiRequest('GET', '/api/news', { params: { limit, offset, slug } })
  return normalizeNewsList(data)
}

export async function getNewsBySlug(slug) {
  const target = String(slug || '').trim()
  if (!target) return null

  // 1) Prefer server-side filter (if backend supports ?slug=)
  const filtered = await listNews({ slug: target, limit: 50, offset: 0 })
  const hit =
    Array.isArray(filtered) ? filtered.find((x) => String(x?.slug || '') === target) : null
  if (hit) return hit

  // 2) Fallback: backend might ignore slug param and always return "latest" object
  const all = await listNews({ limit: 200, offset: 0 })
  const hit2 = Array.isArray(all) ? all.find((x) => String(x?.slug || '') === target) : null
  return hit2 || null
}

export async function createNews(payload) {
  return await apiRequest('POST', '/api/news', { body: payload })
}

export async function deleteNews(id) {
  const newsId = String(id ?? '').trim()
  if (!newsId) throw new Error('Missing id')
  return await apiRequest('DELETE', `/api/news/${encodeURIComponent(newsId)}`)
}

export function formatDateLong(dateString, locale = 'en') {
  // Expecting YYYY-MM-DD
  const d = new Date(`${dateString}T00:00:00`)
  if (Number.isNaN(d.getTime())) return dateString
  return new Intl.DateTimeFormat(locale === 'zh' ? 'zh-CN' : 'en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(d)
}


