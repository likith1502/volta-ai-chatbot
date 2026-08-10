import { apiClient } from './client'

export async function getRuntimeHealth() {
  const res = await apiClient.get('/runtime/health')
  return res.data
}

export async function getRuntimeMetrics() {
  const res = await apiClient.get('/runtime/metrics')
  return res.data
}

export async function getRuntimeProviders() {
  const res = await apiClient.get('/runtime/providers')
  return res.data
}

export async function getRuntimeModels() {
  const res = await apiClient.get('/runtime/models')
  return res.data
}

export async function getExecutionHistory() {
  const res = await apiClient.get('/runtime/executions')
  return res.data
}
