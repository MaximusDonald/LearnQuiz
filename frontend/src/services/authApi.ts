import axios from 'axios'

import type { AuthResponse, LoginPayload, RegisterPayload, TokenResponse } from '../types/auth'


const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  withCredentials: true,
})


export async function registerRequest(payload: RegisterPayload): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/api/auth/register', payload)
  return response.data
}


export async function loginRequest(payload: LoginPayload): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/api/auth/login', payload)
  return response.data
}


export async function refreshRequest(refreshToken: string): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/api/auth/refresh', {
    refresh_token: refreshToken,
  })
  return response.data
}


export async function fetchMeRequest() {
  const response = await apiClient.get<AuthResponse['user']>('/api/auth/me')
  return response.data
}
