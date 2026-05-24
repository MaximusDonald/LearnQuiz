import { useEffect } from 'react'
import { create } from 'zustand'

import {
  apiClient,
  fetchMeRequest,
  loginRequest,
  refreshRequest,
} from '../services/authApi'
import { registerUnauthorizedHandler, setupApiInterceptors } from '../services/apiInterceptors'
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from '../services/tokenStorage'
import type { AuthUser } from '../types/auth'


interface AuthState {
  user: AuthUser | null
  token: string | null
  isBootstrapping: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchMe: () => Promise<void>
  completeSession: (accessToken: string, refreshToken: string, user?: AuthUser | null) => Promise<void>
  refreshAccessToken: () => Promise<string | null>
}


let interceptorsInitialized = false


export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: getAccessToken(),
  isBootstrapping: true,

  async login(email, password) {
    const response = await loginRequest({ email, password })
    setTokens(response.access_token, response.refresh_token)
    set({
      token: response.access_token,
      user: response.user,
    })
  },

  logout() {
    clearTokens()
    set({
      token: null,
      user: null,
      isBootstrapping: false,
    })
    window.location.href = '/login'
  },

  async fetchMe() {
    const user = await fetchMeRequest()
    set({
      user,
      isBootstrapping: false,
    })
  },

  async completeSession(accessToken, refreshToken, user) {
    setTokens(accessToken, refreshToken)
    set({
      token: accessToken,
      user: user ?? null,
      isBootstrapping: false,
    })

    if (!user) {
      await get().fetchMe()
    }
  },

  async refreshAccessToken() {
    const refreshToken = getRefreshToken()
    if (!refreshToken) {
      get().logout()
      return null
    }

    try {
      const response = await refreshRequest(refreshToken)
      setTokens(response.access_token, response.refresh_token)
      set({
        token: response.access_token,
      })
      return response.access_token
    } catch {
      get().logout()
      return null
    }
  },
}))


function initializeAuthInfrastructure(): void {
  if (interceptorsInitialized) {
    return
  }

  setupApiInterceptors(apiClient)
  registerUnauthorizedHandler(async () => useAuthStore.getState().refreshAccessToken())
  interceptorsInitialized = true
}


export function useAuthBootstrap(): void {
  const token = useAuthStore((state) => state.token)
  const fetchMe = useAuthStore((state) => state.fetchMe)
  const logout = useAuthStore((state) => state.logout)

  useEffect(() => {
    initializeAuthInfrastructure()
  }, [])

  useEffect(() => {
    let isMounted = true

    async function bootstrap() {
      if (!token) {
        if (isMounted) {
          useAuthStore.setState({ isBootstrapping: false })
        }
        return
      }

      try {
        await fetchMe()
      } catch {
        if (isMounted) {
          logout()
        }
      }
    }

    void bootstrap()

    return () => {
      isMounted = false
    }
  }, [fetchMe, logout, token])
}
