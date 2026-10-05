import { apiClient } from './client'

export async function getAgents() {
  const res = await apiClient.get('/agents')
  return res.data
}

export async function getAgentHealth() {
  const res = await apiClient.get('/agents/health')
  return res.data
}

export async function getAgentStatistics() {
  const res = await apiClient.get('/agents/statistics')
  return res.data
}

export async function getAgentAnalytics() {
  const res = await apiClient.get('/agents/analytics')
  return res.data
}
