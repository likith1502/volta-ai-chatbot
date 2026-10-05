const SENSITIVE_KEYS = [
  'password',
  'secret',
  'api_key',
  'apikey',
  'token',
  'authorization',
  'access_token',
  'refresh_token',
  'private_key',
  'connection_string',
  'database_url',
  'aws_secret_access_key',
  'openai_api_key',
  'anthropic_api_key',
]

export function redactSecrets(obj: any): any {
  if (obj === null || obj === undefined) return obj

  if (typeof obj === 'string') {
    // Redact OpenAI / Anthropic key patterns if present in raw string
    if (obj.startsWith('sk-') || obj.startsWith('ak-')) {
      return `${obj.substring(0, 3)}***[REDACTED]`
    }
    return obj
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => redactSecrets(item))
  }

  if (typeof obj === 'object') {
    const redacted: Record<string, any> = {}
    for (const [key, value] of Object.entries(obj)) {
      const lowerKey = key.toLowerCase()
      if (SENSITIVE_KEYS.some((sk) => lowerKey.includes(sk))) {
        redacted[key] = '***[REDACTED]'
      } else {
        redacted[key] = redactSecrets(value)
      }
    }
    return redacted
  }

  return obj
}
