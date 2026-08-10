import { describe, expect, it } from 'vitest'
import { ErrorBoundary } from './ErrorBoundary'

describe('ErrorBoundary Component', () => {
  it('instantiates state correctly without error', () => {
    const eb = new ErrorBoundary({ children: null })
    expect(eb.state.hasError).toBe(false)
  })

  it('updates state on error caught via getDerivedStateFromError', () => {
    const testError = new Error('Subsystem API Failure')
    const state = ErrorBoundary.getDerivedStateFromError(testError)
    expect(state.hasError).toBe(true)
    expect(state.error?.message).toBe('Subsystem API Failure')
  })
})
