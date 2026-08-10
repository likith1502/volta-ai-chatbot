import { useState } from 'react'

export type UserRole = 'admin' | 'operator' | 'viewer'

export function usePermission() {
  const [role] = useState<UserRole>('admin') // Default admin role for platform management

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
