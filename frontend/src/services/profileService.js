// src/services/profileService.js
import { apiRequest } from './apiClient'

export async function getMyProfile() {
  return await apiRequest('GET', '/api/me/profile')
}

export async function patchMyProfile(patch) {
  return await apiRequest('PATCH', '/api/me/profile', { body: patch })
}

/**
 * 上传用户头像
 * POST /api/me/photo
 * @param {File} file - 头像图片文件
 * @returns {Promise<object>} - 返回更新后的用户信息
 */
export async function uploadMyPhoto(file) {
  if (!(file instanceof File)) throw new Error('Missing file')
  const formData = new FormData()
  formData.append('file', file)
  formData.append('filename', file.name || 'avatar')
  return await apiRequest('POST', '/api/me/photo', { formData })
}


