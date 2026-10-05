import { useState } from 'react'

export type UserRole = 'admin' | 'operator' | 'viewer'

export function usePermission(initialRole: UserRole = 'admin') {
  const [role] = useState<UserRole>(initialRole)

  const canExecute = role === 'admin' || role === 'operator'
  const canDelete = role === 'admin'
  const isViewerOnly = role === 'viewer'

  return {
    role,
    canExecute,
    canDelete,
    isViewerOnly,
    hasRole: (requiredRole: UserRole) => role === requiredRole,
  }
}

export function checkPermissions(role: UserRole) {
  return {
    role,
    canExecute: role === 'admin' || role === 'operator',
    canDelete: role === 'admin',
    isViewerOnly: role === 'viewer',
    hasRole: (requiredRole: UserRole) => role === requiredRole,
  }
}
