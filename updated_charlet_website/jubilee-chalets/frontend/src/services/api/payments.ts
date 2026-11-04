import apiClient from './client'
import type { PaymentInitResponse, Payment } from '@/types'

export const paymentsApi = {
  initializePayment: async (bookingId: number) => {
    const { data } = await apiClient.post<PaymentInitResponse>('/payments/initialize/', {
      booking_id: bookingId,
    })
    return data
  },

  verifyPayment: async (reference: string) => {
    const { data } = await apiClient.get<Payment>(`/payments/verify/${reference}/`)
    return data
  },
}
