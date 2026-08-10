import { apiClient } from './client'

export async function getRegisteredTools() {
  const res = await apiClient.get('/tools')
  return res.data
}

export async function executeTool(tool_name: string, parameters: Record<string, any>) {
  const res = await apiClient.post('/tools/execute', { tool_name, parameters })
  return res.data
}

export async function getToolStatistics() {
  const res = await apiClient.get('/tools/statistics')
  return res.data
}

export async function getToolHealth() {
  const res = await apiClient.get('/tools/health')
  return res.data
}
