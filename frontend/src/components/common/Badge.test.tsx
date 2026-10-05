import { describe, expect, it } from 'vitest'
import { Badge } from './Badge'

describe('Badge Component', () => {
  it('renders badge component with text', () => {
    const element = Badge({ children: 'Unavailable', variant: 'unavailable' })
    expect(element.props.children).toBe('Unavailable')
  })

  it('supports all badge variants', () => {
    const variants = ['success', 'error', 'warning', 'info', 'neutral', 'unavailable'] as const
    variants.forEach((v) => {
      const badge = Badge({ children: v, variant: v })
      expect(badge).toBeDefined()
    })
  })
})
