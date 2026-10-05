import { apiClient } from './client'

export async function createRAGDocument(doc: Record<string, any> = {}) {
  const res = await apiClient.post('/rag/documents', doc)
  return res.data
}

export async function queryRAG(query: string, top_k: number = 5) {
  const res = await apiClient.post('/rag/query', { query, top_k })
  return res.data
}

export async function getRAGStatistics() {
  const res = await apiClient.get('/rag/statistics')
  return res.data
}

export async function getRAGAnalytics() {
  const res = await apiClient.get('/rag/analytics')
  return res.data
}
