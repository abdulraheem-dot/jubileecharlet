import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { toast } from 'sonner'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// ─── Request interceptor: attach JWT ─────────────────────────────────────────
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token')
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ─── Response interceptor: token refresh ─────────────────────────────────────
let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (err: unknown) => void
}> = []

function processQueue(error: unknown, token: string | null) {
  failedQueue.forEach((p) => (token ? p.resolve(token) : p.reject(error)))
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`
          }
          return apiClient(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        processQueue(error, null)
        isRefreshing = false
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        })
        const newToken: string = data.access
        localStorage.setItem('access_token', newToken)
        processQueue(null, newToken)
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`
        }
        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // Display user-friendly error messages for non-auth errors
    if (error.response?.status === 429) {
      toast.error('Too many requests. Please wait a moment.')
    } else if (error.response?.status && error.response.status >= 500) {
      toast.error('A server error occurred. Please try again later.')
    }

    return Promise.reject(error)
  },
)

export default apiClient
