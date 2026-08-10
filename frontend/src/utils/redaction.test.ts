import { describe, expect, it } from 'vitest'
import { redactSecrets } from './redaction'

describe('redactSecrets', () => {
  it('redacts sensitive object keys automatically', () => {
    const raw = {
      username: 'admin',
      password: 'super_secret_password',
      api_key: 'sk-1234567890',
      nested: {
        access_token: 'jwt.token.secret',
        connection_string: 'postgres://user:pass@host:5432/db',
      },
    }

    const cleaned = redactSecrets(raw)

    expect(cleaned.username).toBe('admin')
    expect(cleaned.password).toBe('***[REDACTED]')
    expect(cleaned.api_key).toBe('***[REDACTED]')
    expect(cleaned.nested.access_token).toBe('***[REDACTED]')
    expect(cleaned.nested.connection_string).toBe('***[REDACTED]')
  })

  it('redacts sk- API key patterns in raw strings', () => {
    expect(redactSecrets('sk-secretkey123')).toBe('sk-***[REDACTED]')
  })
})
