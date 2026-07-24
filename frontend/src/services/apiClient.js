// src/services/apiClient.js
// Shared API client with:
// - Bearer auth from storage
// - single-flight refresh on 401 only, then retry once
// - JSON + multipart(FormData) support

import { getStoredToken, refreshAccessToken } from './authSession'

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

  // A 403 is a valid authorization decision and must never trigger refresh.
  if (res.status === 401 && token) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
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


