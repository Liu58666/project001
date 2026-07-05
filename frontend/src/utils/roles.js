// src/utils/roles.js
// 全局角色定义

export const ROLES = {
  GUEST: 0,
  INTERN: 1,
  STAFF: 2,
  MANAGER: 3,
  ADMIN: 4
}

export const ROLE_NAMES = {
  zh: {
    [ROLES.GUEST]: '游客',
    [ROLES.INTERN]: '实习生',
    [ROLES.STAFF]: '职员',
    [ROLES.MANAGER]: '管理',
    [ROLES.ADMIN]: '管理员'
  },
  en: {
    [ROLES.GUEST]: 'Guest',
    [ROLES.INTERN]: 'Intern',
    [ROLES.STAFF]: 'Staff',
    [ROLES.MANAGER]: 'Manager',
    [ROLES.ADMIN]: 'Admin'
  }
}

/**
 * 获取角色名称
 * @param {number} role - 角色值 (0-4)
 * @param {string} locale - 语言 ('zh' | 'en')
 * @returns {string} 角色名称
 */
export function getRoleName(role, locale = 'en') {
  const names = ROLE_NAMES[locale] || ROLE_NAMES.en
  return names[role] || `Role ${role}`
}

/**
 * 获取角色选项列表（用于下拉框/选择器）
 * @param {string} locale - 语言 ('zh' | 'en')
 * @returns {Array<{value: number, label: string}>}
 */
export function getRoleOptions(locale = 'en') {
  const names = ROLE_NAMES[locale] || ROLE_NAMES.en
  return Object.entries(names).map(([value, name]) => ({
    value: Number(value),
    label: `${name} (${value})`
  }))
}
