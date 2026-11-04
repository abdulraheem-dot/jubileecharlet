import apiClient from './client'
import type { User, AuthTokens, LoginPayload, RegisterPayload } from '@/types'

export const authApi = {
  register: async (payload: RegisterPayload) => {
    const { data } = await apiClient.post<{ user: User; tokens: AuthTokens }>(
      '/auth/register/',
      payload,
    )
    return data
  },

  login: async (payload: LoginPayload) => {
    const { data } = await apiClient.post<{ user: User; tokens: AuthTokens }>(
      '/auth/login/',
      payload,
    )
    return data
  },

  logout: async (refresh: string) => {
    await apiClient.post('/auth/logout/', { refresh })
  },

  refreshToken: async (refresh: string) => {
    const { data } = await apiClient.post<{ access: string }>('/auth/token/refresh/', { refresh })
    return data
  },

  getProfile: async () => {
    const { data } = await apiClient.get<User>('/auth/profile/')
    return data
  },

  updateProfile: async (payload: Partial<User>) => {
    const { data } = await apiClient.patch<User>('/auth/profile/', payload)
    return data
  },

  requestPasswordReset: async (email: string) => {
    const { data } = await apiClient.post('/auth/password-reset/', { email })
    return data
  },

  confirmPasswordReset: async (uid: string, token: string, password: string, passwordConfirm: string) => {
    const { data } = await apiClient.post('/auth/password-reset/confirm/', {
      uid,
      token,
      new_password: password,
      new_password_confirm: passwordConfirm,
    })
    return data
  },

  changePassword: async (currentPassword: string, newPassword: string, newPasswordConfirm: string) => {
    const { data } = await apiClient.post('/auth/password-change/', {
      current_password: currentPassword,
      new_password: newPassword,
      new_password_confirm: newPasswordConfirm,
    })
    return data
  },
}
