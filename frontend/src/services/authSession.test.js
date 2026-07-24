import { afterEach, describe, expect, it, vi } from 'vitest'
import { refreshAccessToken } from './authSession'
import { apiRequest } from './apiClient'

function createStorage() {
  const values = new Map()
  return {
    clear: () => values.clear(),
    getItem: (key) => values.get(key) ?? null,
    removeItem: (key) => values.delete(key),
    setItem: (key, value) => values.set(key, String(value)),
  }
}

globalThis.localStorage ??= createStorage()
globalThis.sessionStorage ??= createStorage()
globalThis.window ??= { location: { origin: 'http://localhost' } }

afterEach(() => {
  localStorage.clear()
  sessionStorage.clear()
  vi.restoreAllMocks()
})

describe('refreshAccessToken', () => {
  it('shares one request between concurrent callers and rotates stored tokens', async () => {
    sessionStorage.setItem('refresh_token', 'old-refresh')
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({
      access_token: 'new-access',
      refresh_token: 'new-refresh',
      access_expires_in: 60,
      refresh_expires_in: 120,
    }), { status: 200, headers: { 'Content-Type': 'application/json' } }))
    vi.stubGlobal('fetch', fetchMock)

    const [first, second] = await Promise.all([refreshAccessToken(), refreshAccessToken()])

    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(first.access_token).toBe('new-access')
    expect(second.refresh_token).toBe('new-refresh')
    expect(sessionStorage.getItem('access_token')).toBe('new-access')
  })

  it('does not refresh after a 403 response', async () => {
    sessionStorage.setItem('access_token', 'valid-access')
    sessionStorage.setItem('refresh_token', 'refresh-must-not-be-used')
    const fetchMock = vi.fn().mockResolvedValue(new Response('forbidden', { status: 403 }))
    vi.stubGlobal('fetch', fetchMock)

    await expect(apiRequest('GET', '/api/admin/users')).rejects.toMatchObject({ status: 403 })
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })
})
