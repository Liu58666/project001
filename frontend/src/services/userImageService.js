// src/services/userImageService.js
import { apiRequest } from './apiClient'

export async function uploadUserImage({
  file,
  imageType,
  filename,
  caption,
  displayOrder,
} = {}) {
  if (!(file instanceof File)) throw new Error('Missing file')
  const type = String(imageType || '').trim()
  if (!type) throw new Error('Missing image_type')

  const formData = new FormData()
  formData.append('file', file)
  formData.append('image_type', type)
  formData.append('filename', filename || file.name || 'upload')
  if (caption != null && String(caption).trim() !== '') formData.append('caption', String(caption))
  if (displayOrder != null && String(displayOrder).trim() !== '') formData.append('display_order', String(displayOrder))

  return await apiRequest('POST', '/api/user-images/upload', { formData })
}

export async function listUserImages({ userId, imageType, limit = 50, offset = 0 } = {}) {
  const params = {
    user_id: userId,
    image_type: imageType,
    limit,
    offset,
  }
  return await apiRequest('GET', '/api/user-images', { params })
}

export async function deleteUserImage(imageId) {
  const id = String(imageId ?? '').trim()
  if (!id) throw new Error('Missing image_id')
  return await apiRequest('DELETE', `/api/user-images/${encodeURIComponent(id)}`)
}

export async function updateUserImageCaption(imageId, caption) {
  const id = String(imageId ?? '').trim()
  if (!id) throw new Error('Missing image_id')
  const formData = new FormData()
  formData.append('caption', String(caption ?? ''))
  return await apiRequest('PATCH', `/api/user-images/${encodeURIComponent(id)}/caption`, { formData })
}

export async function updateUserImageOrder(imageId, displayOrder) {
  const id = String(imageId ?? '').trim()
  if (!id) throw new Error('Missing image_id')
  const formData = new FormData()
  formData.append('display_order', String(displayOrder ?? '0'))
  return await apiRequest('PATCH', `/api/user-images/${encodeURIComponent(id)}/order`, { formData })
}


