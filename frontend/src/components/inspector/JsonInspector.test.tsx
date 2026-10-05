import { describe, expect, it } from 'vitest'
import { redactSecrets } from '../../utils/redaction'

describe('JsonInspector Data Formatting & Redaction Engine', () => {
  it('formats JSON string correctly', () => {
    const rawData = { status: 'healthy', count: 42 }
    const jsonStr = JSON.stringify(rawData, null, 2)

    expect(jsonStr).toContain('"status": "healthy"')
    expect(jsonStr).toContain('"count": 42')
  })

  it('redacts sensitive payload data before inspection display', () => {
    const rawPayload = {
      provider: 'openai',
      api_key: 'sk-abcdef123456',
      nested: { token: 'secret_jwt' },
    }
    const safeData = redactSecrets(rawPayload)

    expect(safeData.api_key).toBe('***[REDACTED]')
    expect(safeData.nested.token).toBe('***[REDACTED]')
  })
})
