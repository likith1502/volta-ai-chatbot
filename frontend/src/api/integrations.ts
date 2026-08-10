import { apiClient } from './client'

export async function getIntegrationProviders() {
  const res = await apiClient.get('/integrations/providers')
  return res.data
}

export async function getCapabilityMatrix() {
  const res = await apiClient.get('/integrations/matrix')
  return res.data
}

export async function getIntegrationAuditLog() {
  const res = await apiClient.get('/integrations/audit')
  return res.data
}

export async function getIntegrationHealth() {
  const res = await apiClient.get('/integrations/health')
  return res.data
}
