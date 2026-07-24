// src/services/newsService.js
// Real API (proxied in dev by vite.config.js: /api -> http://127.0.0.1:8000)
import { apiRequest } from './apiClient'

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

  return await apiRequest('GET', `/api/news/by-slug/${encodeURIComponent(target)}`)
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


