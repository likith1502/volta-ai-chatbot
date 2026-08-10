import { apiClient } from './client'

export async function getMemoryRecords(user_id?: string) {
  const params = user_id ? { user_id } : {}
  const res = await apiClient.get('/memory/records', { params })
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
