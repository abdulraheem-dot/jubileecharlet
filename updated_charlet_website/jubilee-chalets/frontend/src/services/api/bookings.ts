import apiClient from './client'
import type { Booking, CreateBookingPayload, PaginatedResponse, DashboardSummary } from '@/types'

export const bookingsApi = {
  createBooking: async (payload: CreateBookingPayload) => {
    const { data } = await apiClient.post<Booking>('/bookings/', payload)
    return data
  },

  getMyBookings: async (params?: { status?: string; page?: number }) => {
    const { data } = await apiClient.get<PaginatedResponse<Booking>>('/bookings/', { params })
    return data
  },

  getBooking: async (id: number) => {
    const { data } = await apiClient.get<Booking>(`/bookings/${id}/`)
    return data
  },

  requestCancellation: async (id: number, reason: string) => {
    const { data } = await apiClient.post(`/bookings/${id}/cancel/`, { reason })
    return data
  },

  getDashboardSummary: async () => {
    const { data } = await apiClient.get<DashboardSummary>('/dashboard/summary/')
    return data
  },
}
