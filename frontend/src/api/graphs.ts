import { apiClient } from './client'

export async function getGraphs() {
  const res = await apiClient.get('/graph_runtime/graphs')
  return res.data
}

export async function executeGraph(graph_id: string, initial_state: Record<string, any>) {
  const res = await apiClient.post('/graph_runtime/execute', { graph_id, initial_state })
  return res.data
}

export async function getGraphMetrics() {
  const res = await apiClient.get('/graph_runtime/metrics')
  return res.data
}
