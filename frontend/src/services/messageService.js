// src/services/messageService.js
import { apiRequest } from './apiClient'

/**
 * 获取当前用户的系统消息
 * GET /api/messages/me?limit=50&offset=0&unread_only=false
 * @param {object} options - { limit, offset, unreadOnly }
 */
export async function getMyMessages({ limit = 50, offset = 0, unreadOnly = false } = {}) {
  return await apiRequest('GET', '/api/messages/me', {
    params: { limit, offset, unread_only: unreadOnly }
  })
}

/**
 * 标记消息为已读
 * POST /api/messages/{message_id}/read
 * @param {number|string} messageId
 */
export async function markMessageRead(messageId) {
  const id = String(messageId ?? '').trim()
  if (!id) throw new Error('Missing message_id')
  return await apiRequest('POST', `/api/messages/${encodeURIComponent(id)}/read`)
}

/**
 * 删除一条消息
 * DELETE /api/messages/{message_id}
 * @param {number|string} messageId
 */
export async function deleteMessage(messageId) {
  const id = String(messageId ?? '').trim()
  if (!id) throw new Error('Missing message_id')
  return await apiRequest('DELETE', `/api/messages/${encodeURIComponent(id)}`)
}
