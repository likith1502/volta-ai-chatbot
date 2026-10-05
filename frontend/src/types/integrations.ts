export interface ProviderInfo {
  provider_id: string
  name: string
  category: 'storage' | 'vector' | 'llm' | 'auth' | 'database' | 'observability' | 'messaging' | 'search'
  status: string
  health: string
  is_healthy: boolean
  priority?: number
  latency_ms?: number
  details?: Record<string, any>
  dependency_available?: boolean
  credentials_present?: boolean
}

export interface CapabilityInfo {
  name: string
  category: string
  capabilities: string[]
  supports_async: boolean
  fail_fast_timeout: boolean
  dependency?: string
}

export type CapabilityMatrix = Record<string, CapabilityInfo>

export interface IntegrationAuditRecord {
  timestamp: string
  action: string
  provider_id: string
  details?: Record<string, any>
}
