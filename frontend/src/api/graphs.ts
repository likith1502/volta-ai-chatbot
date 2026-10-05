import { apiClient } from './client'

export async function getGraphHealth() {
  const res = await apiClient.get('/graph-runtime/health')
  return res.data
}

export async function executeGraph(graph_id: string, initial_state: Record<string, any>) {
  const res = await apiClient.post('/graph-runtime/execute', { graph_id, initial_state })
  return res.data
}

export async function getGraphStatistics() {
  const res = await apiClient.get('/graph-runtime/statistics')
  return res.data
}

export async function getGraphAnalytics() {
  const res = await apiClient.get('/graph-runtime/analytics')
  return res.data
}
