import apiClient from './client'
import type {
  Experience,
  MenuCategory,
  MenuItem,
  GalleryImage,
  EventVenue,
  EventEnquiryPayload,
  Testimonial,
  FAQ,
  ContactPayload,
  NewsletterPayload,
  WebsiteSettings,
} from '@/types'

export const contentApi = {
  // Experiences
  getExperiences: async () => {
    const { data } = await apiClient.get<Experience[]>('/experiences/')
    return data
  },

  // Dining
  getMenuCategories: async () => {
    const { data } = await apiClient.get<MenuCategory[]>('/menu/categories/')
    return data
  },
  getMenuItems: async (categoryId?: number) => {
    const params = categoryId ? { category: categoryId } : {}
    const { data } = await apiClient.get<MenuItem[]>('/menu/', { params })
    return data
  },

  // Gallery
  getGalleryImages: async (category?: string) => {
    const params = category ? { category } : {}
    const { data } = await apiClient.get<GalleryImage[]>('/gallery/', { params })
    return data
  },

  // Events
  getEventVenues: async () => {
    const { data } = await apiClient.get<EventVenue[]>('/events/venues/')
    return data
  },
  submitEventEnquiry: async (payload: EventEnquiryPayload) => {
    const { data } = await apiClient.post('/events/enquiries/', payload)
    return data
  },

  // Testimonials
  getTestimonials: async () => {
    const { data } = await apiClient.get<Testimonial[]>('/testimonials/')
    return data
  },

  // FAQs
  getFAQs: async (category?: string) => {
    const params = category ? { category } : {}
    const { data } = await apiClient.get<FAQ[]>('/faqs/', { params })
    return data
  },

  // Contact
  submitContactForm: async (payload: ContactPayload) => {
    const { data } = await apiClient.post('/contact/', payload)
    return data
  },

  // Newsletter
  subscribeNewsletter: async (payload: NewsletterPayload) => {
    const { data } = await apiClient.post('/newsletter/subscribe/', payload)
    return data
  },

  // Website settings
  getSettings: async () => {
    const { data } = await apiClient.get<WebsiteSettings>('/website/settings/')
    return data
  },
}
