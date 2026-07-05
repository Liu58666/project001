// src/services/taskService.js
import { apiRequest } from './apiClient'

// ============================================
// 管理端接口 (role >= 3)
// ============================================

/**
 * 管理员发布任务
 * POST /api/admin/tasks
 * 权限：role >= 3
 * @param {object} params - { title, content, roles, user_ids }
 * @returns {Promise<TaskOut>}
 */
export async function createTask({ title, content, roles, user_ids }) {
  if (!content) throw new Error('Missing content')
  if ((!roles || roles.length === 0) && (!user_ids || user_ids.length === 0)) {
    throw new Error('Must provide roles or user_ids')
  }
  return await apiRequest('POST', '/api/admin/tasks', {
    body: { title, content, roles, user_ids }
  })
}

/**
 * 管理端：任务列表
 * GET /api/admin/tasks
 * 权限：role >= 3
 * @param {object} params - { limit, offset }
 * @returns {Promise<TaskOut[]>}
 */
export async function listTasks({ limit = 50, offset = 0 } = {}) {
  return await apiRequest('GET', '/api/admin/tasks', {
    params: { limit, offset }
  })
}

/**
 * 管理端：查看任务提交列表（含图片+提交人信息）
 * GET /api/admin/tasks/{task_id}/submissions
 * 权限：role >= 3
 * @param {number|string} taskId
 * @param {object} params - { limit, offset }
 * @returns {Promise<TaskSubmissionAdminOut[]>}
 */
export async function listTaskSubmissions(taskId, { limit = 200, offset = 0 } = {}) {
  const id = String(taskId ?? '').trim()
  if (!id) throw new Error('Missing task_id')
  return await apiRequest('GET', `/api/admin/tasks/${encodeURIComponent(id)}/submissions`, {
    params: { limit, offset }
  })
}

/**
 * 管理端：对提交评分（覆盖）
 * POST /api/admin/tasks/{task_id}/submissions/{submission_id}/score
 * 权限：role >= 3
 * @param {number|string} taskId
 * @param {number|string} submissionId
 * @param {number} score - 0-100
 * @returns {Promise<TaskSubmissionOut>}
 */
export async function scoreSubmission(taskId, submissionId, score) {
  const tid = String(taskId ?? '').trim()
  const sid = String(submissionId ?? '').trim()
  if (!tid) throw new Error('Missing task_id')
  if (!sid) throw new Error('Missing submission_id')
  if (score === undefined || score === null) throw new Error('Missing score')
  return await apiRequest('POST', `/api/admin/tasks/${encodeURIComponent(tid)}/submissions/${encodeURIComponent(sid)}/score`, {
    body: { score }
  })
}

// ============================================
// 用户端接口 (登录用户)
// ============================================

/**
 * 用户端：我被指派的任务列表（含我的提交）
 * GET /api/tasks/me
 * 权限：登录用户
 * @param {object} params - { limit, offset }
 * @returns {Promise<TaskAssignedOut[]>}
 */
export async function getMyTasks({ limit = 50, offset = 0 } = {}) {
  return await apiRequest('GET', '/api/tasks/me', {
    params: { limit, offset }
  })
}

/**
 * 用户端：任务详情（接收者或管理员可查）
 * GET /api/tasks/{task_id}
 * 权限：接收者本人或 role >= 3
 * @param {number|string} taskId
 * @returns {Promise<TaskAssignedOut>}
 */
export async function getTaskDetail(taskId) {
  const id = String(taskId ?? '').trim()
  if (!id) throw new Error('Missing task_id')
  return await apiRequest('GET', `/api/tasks/${encodeURIComponent(id)}`)
}

/**
 * 用户端：提交/更新提交（纯文本+建议，覆盖）
 * PUT /api/tasks/{task_id}/submission
 * 权限：必须是该任务接收者
 * @param {number|string} taskId
 * @param {object} data - { text_content?, suggestion? }
 * @returns {Promise<TaskSubmissionOut>}
 */
export async function upsertSubmission(taskId, { text_content, suggestion } = {}) {
  const id = String(taskId ?? '').trim()
  if (!id) throw new Error('Missing task_id')
  const body = {}
  if (text_content !== undefined) body.text_content = text_content
  if (suggestion !== undefined) body.suggestion = suggestion
  return await apiRequest('PUT', `/api/tasks/${encodeURIComponent(id)}/submission`, {
    body
  })
}

/**
 * 用户端：上传提交图片（单张）
 * POST /api/tasks/{task_id}/submission/images
 * 权限：必须是该任务接收者
 * Content-Type: multipart/form-data
 * @param {number|string} taskId
 * @param {File} file - 图片文件
 * @param {string} filename - 原始文件名
 * @returns {Promise<TaskSubmissionImageUploadResponse>}
 */
export async function uploadSubmissionImage(taskId, file, filename) {
  const id = String(taskId ?? '').trim()
  if (!id) throw new Error('Missing task_id')
  if (!file) throw new Error('Missing file')
  
  const formData = new FormData()
  formData.append('file', file)
  formData.append('filename', filename || file.name || 'image.png')
  
  return await apiRequest('POST', `/api/tasks/${encodeURIComponent(id)}/submission/images`, {
    formData
  })
}

/**
 * 用户端：删除提交图片
 * DELETE /api/tasks/{task_id}/submission/images/{image_id}
 * 权限：图片所属提交的提交者本人或 role >= 3
 * @param {number|string} taskId
 * @param {number|string} imageId
 * @returns {Promise<void>}
 */
export async function deleteSubmissionImage(taskId, imageId) {
  const tid = String(taskId ?? '').trim()
  const iid = String(imageId ?? '').trim()
  if (!tid) throw new Error('Missing task_id')
  if (!iid) throw new Error('Missing image_id')
  return await apiRequest('DELETE', `/api/tasks/${encodeURIComponent(tid)}/submission/images/${encodeURIComponent(iid)}`)
}

/**
 * 管理端：删除任务（含提交/图片等关联数据）
 * DELETE /api/admin/tasks/{task_id}
 * 权限：role >= 3
 * @param {number|string} taskId
 * @returns {Promise<void>}
 */
export async function deleteTask(taskId) {
  const id = String(taskId ?? '').trim()
  if (!id) throw new Error('Missing task_id')
  return await apiRequest('DELETE', `/api/admin/tasks/${encodeURIComponent(id)}`)
}
