import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/features/authentication/AuthContext'

interface Props {
  children: React.ReactNode
  requireAdmin?: boolean
}

export default function ProtectedRoute({ children, requireAdmin = false }: Props) {
  const { isAuthenticated, isLoading, user } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-brand-dark-green border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (requireAdmin && !user?.is_staff) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}
