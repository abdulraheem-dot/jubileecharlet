import apiClient from './client'
import type { Room, RoomCategory, PaginatedResponse } from '@/types'

export interface RoomFilters {
  category?: string
  min_price?: number
  max_price?: number
  max_occupancy?: number
  amenities?: string[]
  check_in?: string
  check_out?: string
  num_adults?: number
  num_children?: number
  page?: number
  page_size?: number
  ordering?: string
}

export const roomsApi = {
  getRooms: async (filters?: RoomFilters) => {
    const { data } = await apiClient.get<PaginatedResponse<Room>>('/rooms/', { params: filters })
    return data
  },

  getRoom: async (idOrSlug: string | number) => {
    const { data } = await apiClient.get<Room>(`/rooms/${idOrSlug}/`)
    return data
  },

  getCategories: async () => {
    const { data } = await apiClient.get<RoomCategory[]>('/rooms/categories/')
    return data
  },

  checkAvailability: async (params: {
    check_in: string
    check_out: string
    num_adults: number
    num_children?: number
  }) => {
    const { data } = await apiClient.get<Room[]>('/rooms/availability/', { params })
    return data
  },
}
