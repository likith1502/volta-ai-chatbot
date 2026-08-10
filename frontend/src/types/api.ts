export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  error?: string
  details?: Record<string, any>
  timestamp?: string
}

export interface HealthReport {
  status: 'healthy' | 'unhealthy' | 'degraded' | 'green' | 'yellow' | 'red'
  overall_health?: string
  version?: string
  environment?: string
  subsystems?: Record<string, any>
  details?: Record<string, any>
  components?: Record<string, any>
}

export interface NavItem {
  name: string
  href: string
  icon: string
  category: 'overview' | 'ai_platform' | 'platform' | 'observability' | 'settings'
  badge?: string
}
