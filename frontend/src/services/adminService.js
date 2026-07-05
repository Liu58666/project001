// src/services/adminService.js
import { apiRequest } from './apiClient'

/**
 * 查询所有用户（分页）
 * GET /api/admin/users?limit=50&offset=0
 * 权限：role == 4
 */
export async function listAllUsers({ limit = 50, offset = 0 } = {}) {
  return await apiRequest('GET', '/api/admin/users', {
    params: { limit, offset }
  })
}

/**
 * 管理员修改任意用户字段
 * PATCH /api/admin/users/{user_id}
 * 权限：role == 4
 * @param {number|string} userId
 * @param {object} updates - { username, phone, email, birthday, photo, is_active, role, password }
 */
export async function updateUserByAdmin(userId, updates) {
  const id = String(userId ?? '').trim()
  if (!id) throw new Error('Missing user_id')
  return await apiRequest('PATCH', `/api/admin/users/${encodeURIComponent(id)}`, {
    body: updates
  })
}

/**
 * 管理员通过申请并发送系统消息
 * POST /api/admin/applications/{application_id}/accept
 * 权限：role >= 3
 * @param {number|string} applicationId
 * @param {string} [message] - 可选的确认消息，默认为"你的申请已通过审核，请留意后续通知。"
 */
export async function acceptApplication(applicationId, message) {
  const id = String(applicationId ?? '').trim()
  if (!id) throw new Error('Missing application_id')
  const body = message ? { message } : undefined
  return await apiRequest('POST', `/api/admin/applications/${encodeURIComponent(id)}/accept`, {
    body
  })
}

/**
 * 群发系统消息
 * POST /api/admin/messages/broadcast
 * 权限：role == 4
 * @param {object} params - { title, content, roles, user_ids }
 * @returns {Promise<{sent_count: number, recipient_count: number, batch_id: string}>}
 */
export async function broadcastMessage({ title, content, roles, user_ids }) {
  if (!content) throw new Error('Missing content')
  if ((!roles || roles.length === 0) && (!user_ids || user_ids.length === 0)) {
    throw new Error('Must provide roles or user_ids')
  }
  return await apiRequest('POST', '/api/admin/messages/broadcast', {
    body: { title, content, roles, user_ids }
  })
}

/**
 * 撤回一批群发消息
 * POST /api/admin/messages/broadcast/{batch_id}/revoke
 * 权限：role == 4
 * @param {string} batchId
 * @returns {Promise<{revoked_count: number, batch_id: string}>}
 */
export async function revokeBroadcast(batchId) {
  if (!batchId) throw new Error('Missing batch_id')
  return await apiRequest('POST', `/api/admin/messages/broadcast/${encodeURIComponent(batchId)}/revoke`)
}
