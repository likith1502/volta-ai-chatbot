import { apiClient } from './client'

export async function getPromptTemplates() {
  const res = await apiClient.get('/prompt/templates')
  return res.data
}

export async function getPromptProfiles() {
  const res = await apiClient.get('/prompt/profiles')
  return res.data
}

export async function renderPromptTemplate(template_id: string, variables: Record<string, any>) {
  const res = await apiClient.post('/prompt/render', { template_id, variables })
  return res.data
}

export async function getPromptStatistics() {
  const res = await apiClient.get('/prompt/statistics')
  return res.data
}
