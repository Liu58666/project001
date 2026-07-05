// src/services/imageService.js
// 图片上传服务

function getStoredToken() {
  return (
    localStorage.getItem('access_token') ||
    sessionStorage.getItem('access_token') ||
    ''
  )
}

/**
 * 上传图片
 * @param {File} file - 图片文件
 * @param {string} position - 图片位置: cover, content, thumbnail, banner, gallery
 * @param {number|null} newsId - 关联的新闻ID（可选）
 * @returns {Promise<Object>} 上传结果
 */
export async function uploadImage(file, position = 'content', newsId = null) {
  const token = getStoredToken()
  if (!token) {
    throw new Error('未登录，请先登录')
  }

  const formData = new FormData()
  formData.append('file', file)
  formData.append('position', position)
  formData.append('filename', file.name)
  if (newsId) {
    formData.append('news_id', String(newsId))
  }

  const res = await fetch('/api/images/upload', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  })

  let data = null
  try {
    data = await res.json()
  } catch {
    data = null
  }

  if (!res.ok) {
    // 422 错误通常包含详细的验证信息
    let msg = `上传失败 (${res.status})`
    if (data?.detail) {
      if (typeof data.detail === 'string') {
        msg = data.detail
      } else if (Array.isArray(data.detail)) {
        // FastAPI 验证错误格式: [{loc: [...], msg: "...", type: "..."}]
        msg = data.detail.map(e => `${e.loc?.join('.')}: ${e.msg}`).join('; ')
      } else {
        msg = JSON.stringify(data.detail)
      }
    }
    console.error('Image upload error:', data)
    throw new Error(msg)
  }

  return data
}

/**
 * 查询图片列表
 * @param {Object} params - 查询参数
 * @returns {Promise<Array>} 图片列表
 */
export async function listImages({ position, newsId, limit = 50, offset = 0 } = {}) {
  const url = new URL('/api/images', window.location.origin)
  if (position) url.searchParams.set('position', position)
  if (newsId) url.searchParams.set('news_id', String(newsId))
  url.searchParams.set('limit', String(limit))
  url.searchParams.set('offset', String(offset))

  const res = await fetch(url.toString(), {
    headers: { Accept: 'application/json' },
  })

  if (!res.ok) {
    throw new Error(`获取图片列表失败 (${res.status})`)
  }

  return await res.json()
}

/**
 * 删除图片
 * @param {number} imageId - 图片ID
 * @returns {Promise<void>}
 */
export async function deleteImage(imageId) {
  const token = getStoredToken()
  if (!token) {
    throw new Error('未登录，请先登录')
  }

  const res = await fetch(`/api/images/${imageId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!res.ok && res.status !== 204) {
    let data = null
    try {
      data = await res.json()
    } catch {
      data = null
    }
    const msg = data?.detail || `删除失败 (${res.status})`
    throw new Error(msg)
  }
}

/**
 * 将图片关联到新闻
 * @param {number} imageId - 图片ID
 * @param {number} newsId - 新闻ID
 * @returns {Promise<Object>} 更新后的图片信息
 */
export async function linkImageToNews(imageId, newsId) {
  const token = getStoredToken()
  if (!token) {
    throw new Error('未登录，请先登录')
  }

  const formData = new FormData()
  formData.append('news_id', String(newsId))

  const res = await fetch(`/api/images/${imageId}/link-news`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  })

  let data = null
  try {
    data = await res.json()
  } catch {
    data = null
  }

  if (!res.ok) {
    const msg = data?.detail || `关联失败 (${res.status})`
    throw new Error(msg)
  }

  return data
}
