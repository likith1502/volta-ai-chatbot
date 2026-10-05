import { apiClient } from './client'

export async function getPromptTemplates() {
  const res = await apiClient.get('/prompts/templates')
  return res.data
}

export async function getPromptProfiles() {
  const res = await apiClient.get('/prompts/profiles')
  return res.data
}

export async function renderPromptTemplate(template_id: string, variables: Record<string, any>) {
  const res = await apiClient.post('/prompts/render', { template_id, variables })
  return res.data
}

export async function getPromptHistory() {
  const res = await apiClient.get('/prompts/history')
  return res.data
}

export async function getPromptHealth() {
  const res = await apiClient.get('/prompts/health')
  return res.data
}
