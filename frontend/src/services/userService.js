// src/services/userService.js

/**
 * 获取所有用户头像（公开接口，无需鉴权）
 * GET /api/users/avatars?limit=200&offset=0
 * @returns {Promise<Array<{id: number, photo: string}>>}
 */
export async function getUserAvatars({ limit = 200, offset = 0 } = {}) {
  const url = new URL('/api/users/avatars', window.location.origin)
  url.searchParams.set('limit', String(limit))
  url.searchParams.set('offset', String(offset))
  
  const res = await fetch(url.toString(), {
    method: 'GET',
    headers: { 'Accept': 'application/json' }
  })
  
  if (!res.ok) {
    throw new Error(`Failed to fetch avatars (${res.status})`)
  }
  
  return await res.json()
}

/**
 * 将头像列表转换为 id -> photo 的映射
 * @param {Array<{id: number, photo: string}>} avatars
 * @returns {Object<number, string>}
 */
export function buildAvatarMap(avatars) {
  const map = {}
  if (Array.isArray(avatars)) {
    avatars.forEach(item => {
      if (item.id && item.photo) {
        map[item.id] = item.photo
      }
    })
  }
  return map
}
