import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { AppHeader } from './AppHeader'
import { LoadingScreen } from './LoadingScreen'
import { useAuthStore } from '../store/useAuthStore'


export function ProtectedRoute() {
  const location = useLocation()
  const token = useAuthStore((state) => state.token)
  const isBootstrapping = useAuthStore((state) => state.isBootstrapping)

  if (isBootstrapping) {
    return <LoadingScreen />
  }

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return (
    <>
      <AppHeader />
      <Outlet />
    </>
  )
}
