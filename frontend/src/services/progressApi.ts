import { apiClient } from './authApi'
import type { GlobalProgress } from '../types/progress'


export async function fetchGlobalProgressRequest(): Promise<GlobalProgress> {
  const response = await apiClient.get<GlobalProgress>('/api/progress')
  return response.data
}
