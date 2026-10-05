import { apiClient } from './client'

export async function getIntegrationProviders() {
  const res = await apiClient.get('/integrations/providers')
  return res.data
}

export async function getIntegrationHealth() {
  const res = await apiClient.get('/integrations/health')
  return res.data
}

export async function getIntegrationStatistics() {
  const res = await apiClient.get('/integrations/statistics')
  return res.data
}

export async function getIntegrationAnalytics() {
  const res = await apiClient.get('/integrations/analytics')
  return res.data
}
