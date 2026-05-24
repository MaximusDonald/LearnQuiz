import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

import { getAccessToken } from './tokenStorage'


let onUnauthorized: (() => Promise<string | null>) | null = null
let isRefreshing = false
const authBypassPaths = new Set([
  '/api/auth/login',
  '/api/auth/register',
  '/api/auth/refresh',
])


export function registerUnauthorizedHandler(handler: () => Promise<string | null>) {
  onUnauthorized = handler
}


export function setupApiInterceptors(apiClient: AxiosInstance): void {
  apiClient.interceptors.request.use((config) => {
    const token = getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
      const status = error.response?.status as number | undefined
      const originalRequest = error.config as InternalAxiosRequestConfig & {
        _retry?: boolean
      }
      const requestUrl = originalRequest.url ?? ''
      const shouldBypass = authBypassPaths.has(requestUrl)

      if (
        status === 401 &&
        onUnauthorized &&
        !originalRequest._retry &&
        !isRefreshing &&
        !shouldBypass
      ) {
        originalRequest._retry = true
        isRefreshing = true

        try {
          const newToken = await onUnauthorized()
          if (newToken) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`
            return apiClient(originalRequest)
          }
        } finally {
          isRefreshing = false
        }
      }

      return Promise.reject(error)
    },
  )
}
