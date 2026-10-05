import axios, { AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      console.warn(`[API Error ${error.response.status}] ${error.config?.url}:`, error.response.data)
    } else if (error.request) {
      console.warn(`[API Network Error] ${error.config?.url}: No response received`)
    }
    return Promise.reject(error)
  }
)

export async function fetchSafe<T>(requestFn: () => Promise<{ data: T }>): Promise<T | null> {
  try {
    const response = await requestFn()
    return response.data
  } catch (error) {
    return null
  }
}
