// src/services/imageService.js
// 图片上传服务
import { apiRequest } from './apiClient'

/**
 * 上传图片
 * @param {File} file - 图片文件
 * @param {string} position - 图片位置: cover, content, thumbnail, banner, gallery
 * @param {number|null} newsId - 关联的新闻ID（可选）
 * @returns {Promise<Object>} 上传结果
 */
export async function uploadImage(file, position = 'content', newsId = null) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('position', position)
  formData.append('filename', file.name)
  if (newsId) {
    formData.append('news_id', String(newsId))
  }

  return await apiRequest('POST', '/api/images/upload', { formData })
}

/**
 * 查询图片列表
 * @param {Object} params - 查询参数
 * @returns {Promise<Array>} 图片列表
 */
export async function listImages({ position, newsId, limit = 50, offset = 0 } = {}) {
  return await apiRequest('GET', '/api/images', { params: { position, news_id: newsId, limit, offset } })
}

/**
 * 删除图片
 * @param {number} imageId - 图片ID
 * @returns {Promise<void>}
 */
export async function deleteImage(imageId) {
  return await apiRequest('DELETE', `/api/images/${encodeURIComponent(imageId)}`)
}

/**
 * 将图片关联到新闻
 * @param {number} imageId - 图片ID
 * @param {number} newsId - 新闻ID
 * @returns {Promise<Object>} 更新后的图片信息
 */
export async function linkImageToNews(imageId, newsId) {
  const formData = new FormData()
  formData.append('news_id', String(newsId))
  return await apiRequest('PUT', `/api/images/${encodeURIComponent(imageId)}/link-news`, { formData })
}
