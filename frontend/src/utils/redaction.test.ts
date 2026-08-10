import { describe, expect, it } from 'vitest'
import { redactSecrets } from './redaction'

describe('Recursive Secret Redaction Utility', () => {
  it('redacts sensitive keys in flat objects', () => {
    const input = {
      user: 'admin',
      password: 'supersecretpassword123',
      api_key: 'sk-1234567890abcdef',
      connection_string: 'postgresql://user:pass@localhost:5432/db',
    }
    const output = redactSecrets(input)

    expect(output.user).toBe('admin')
    expect(output.password).toBe('***[REDACTED]')
    expect(output.api_key).toBe('***[REDACTED]')
    expect(output.connection_string).toBe('***[REDACTED]')
  })

  it('redacts sensitive keys recursively in deeply nested objects and arrays', () => {
    const input = {
      level1: {
        normalField: 'hello',
        secret_token: 'bearer_token_xyz',
        nestedArray: [
          { name: 'provider1', openai_api_key: 'sk-proj-99999' },
          { name: 'provider2', private_key: '-----BEGIN RSA PRIVATE KEY-----' },
        ],
      },
    }
    const output = redactSecrets(input)

    expect(output.level1.normalField).toBe('hello')
    expect(output.level1.secret_token).toBe('***[REDACTED]')
    expect(output.level1.nestedArray[0].openai_api_key).toBe('***[REDACTED]')
    expect(output.level1.nestedArray[1].private_key).toBe('***[REDACTED]')
  })

  it('redacts raw secret key patterns in strings (sk-***, ak-***)', () => {
    expect(redactSecrets('sk-123456789')).toBe('sk-***[REDACTED]')
    expect(redactSecrets('ak-987654321')).toBe('ak-***[REDACTED]')
    expect(redactSecrets('regular_string')).toBe('regular_string')
  })

  it('handles null, undefined, numbers, and booleans safely', () => {
    expect(redactSecrets(null)).toBeNull()
    expect(redactSecrets(undefined)).toBeUndefined()
    expect(redactSecrets(42)).toBe(42)
    expect(redactSecrets(true)).toBe(true)
  })
})
