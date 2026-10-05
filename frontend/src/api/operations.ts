import { apiClient } from './client'

export async function getDeploymentEnvironment() {
  const res = await apiClient.get('/deployment/environment')
  return res.data
}

export async function getDeploymentHealth() {
  const res = await apiClient.get('/deployment/health')
  return res.data
}

export async function getDeploymentAnalytics() {
  const res = await apiClient.get('/deployment/analytics')
  return res.data
}

export async function getDeploymentStatistics() {
  const res = await apiClient.get('/deployment/statistics')
  return res.data
}

export async function getDeploymentStatus() {
  const res = await apiClient.get('/deployment/status')
  return res.data
}
