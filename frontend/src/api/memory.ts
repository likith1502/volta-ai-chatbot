import { apiClient } from './client'

export async function storeMemoryRecord(record: Record<string, any> = {}) {
  const res = await apiClient.post('/memory', record)
  return res.data
}

export async function searchMemory(query: string, user_id?: string) {
  const res = await apiClient.post('/memory/search', { query, user_id })
  return res.data
}

export async function getMemoryStatistics() {
  const res = await apiClient.get('/memory/statistics')
  return res.data
}

export async function getMemoryMetrics() {
  const res = await apiClient.get('/memory/metrics')
  return res.data
}
