import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authApi } from '@/services/api/auth'
import type { User, LoginPayload, RegisterPayload } from '@/types'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (payload: LoginPayload) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setUser(null)
      setIsLoading(false)
      return
    }
    try {
      const profile = await authApi.getProfile()
      setUser(profile)
    } catch {
      setUser(null)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshUser()
  }, [refreshUser])

  const login = async (payload: LoginPayload) => {
    const { user: u, tokens } = await authApi.login(payload)
    localStorage.setItem('access_token', tokens.access)
    localStorage.setItem('refresh_token', tokens.refresh)
    setUser(u)
  }

  const register = async (payload: RegisterPayload) => {
    const { user: u, tokens } = await authApi.register(payload)
    localStorage.setItem('access_token', tokens.access)
    localStorage.setItem('refresh_token', tokens.refresh)
    setUser(u)
  }

  const logout = async () => {
    const refresh = localStorage.getItem('refresh_token')
    if (refresh) {
      try { await authApi.logout(refresh) } catch { /* ignore */ }
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
