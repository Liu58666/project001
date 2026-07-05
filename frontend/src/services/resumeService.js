// src/services/resumeService.js
import { apiRequest } from './apiClient'

export async function createOrUpdateResume(payload) {
  return await apiRequest('POST', '/api/resumes', { body: payload })
}

export async function getMyResume() {
  return await apiRequest('GET', '/api/resumes/me')
}

export async function patchMyResume(patch) {
  return await apiRequest('PATCH', '/api/resumes/me', { body: patch })
}

export async function getPublicResume(userId) {
  const id = String(userId ?? '').trim()
  if (!id) throw new Error('Missing user_id')
  return await apiRequest('GET', `/api/resumes/${encodeURIComponent(id)}`)
}

/**
 * 获取所有用户的简历目录（公开接口）
 * GET /api/resumes?limit=50&offset=0
 */
export async function listAllResumes({ limit = 50, offset = 0 } = {}) {
  return await apiRequest('GET', '/api/resumes', {
    params: { limit, offset }
  })
}

// ============================================
// PDF 简历接口
// ============================================

/**
 * 上传/覆盖我的 PDF 简历
 * POST /api/resumes/me/pdf
 * Content-Type: multipart/form-data
 * @param {File} file - PDF 文件
 * @param {string} filename - 原始文件名（必须以 .pdf 结尾）
 * @returns {Promise<ResumePdfOut>}
 */
export async function uploadMyPdfResume(file, filename) {
  if (!file) throw new Error('Missing file')
  if (!filename || !filename.toLowerCase().endsWith('.pdf')) {
    throw new Error('Filename must end with .pdf')
  }
  const formData = new FormData()
  formData.append('file', file)
  formData.append('filename', filename)
  return await apiRequest('POST', '/api/resumes/me/pdf', { formData })
}

/**
 * 获取我的 PDF 简历信息
 * GET /api/resumes/me/pdf
 * @returns {Promise<ResumePdfOut>}
 */
export async function getMyPdfResume() {
  return await apiRequest('GET', '/api/resumes/me/pdf')
}

/**
 * 管理员查询所有用户 PDF 简历（列表）
 * GET /api/admin/resume-pdfs
 * 权限：role >= 3
 * @param {object} params - { limit, offset, user_id, username }
 * @returns {Promise<AdminResumePdfOut[]>}
 */
export async function listAdminResumePdfs({ limit = 50, offset = 0, user_id, username } = {}) {
  const params = { limit, offset }
  if (user_id !== undefined && user_id !== null && user_id !== '') {
    params.user_id = user_id
  }
  if (username !== undefined && username !== null && username !== '') {
    params.username = username
  }
  return await apiRequest('GET', '/api/admin/resume-pdfs', { params })
}
