import { describe, expect, it } from 'vitest'
import { checkPermissions } from './usePermission'

describe('usePermission Role Checker', () => {
  it('evaluates admin role permissions correctly', () => {
    const perm = checkPermissions('admin')
    expect(perm.role).toBe('admin')
    expect(perm.canExecute).toBe(true)
    expect(perm.canDelete).toBe(true)
    expect(perm.isViewerOnly).toBe(false)
    expect(perm.hasRole('admin')).toBe(true)
  })

  it('evaluates operator role permissions correctly', () => {
    const perm = checkPermissions('operator')
    expect(perm.role).toBe('operator')
    expect(perm.canExecute).toBe(true)
    expect(perm.canDelete).toBe(false)
    expect(perm.isViewerOnly).toBe(false)
  })

  it('evaluates viewer role permissions correctly', () => {
    const perm = checkPermissions('viewer')
    expect(perm.role).toBe('viewer')
    expect(perm.canExecute).toBe(false)
    expect(perm.canDelete).toBe(false)
    expect(perm.isViewerOnly).toBe(true)
  })
})
