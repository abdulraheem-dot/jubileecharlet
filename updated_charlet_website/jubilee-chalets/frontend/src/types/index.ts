// ─── Auth ────────────────────────────────────────────────────────────────────

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  phone_number: string | null
  profile_picture: string | null
  is_staff: boolean
  date_joined: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
  phone_number?: string
}

// ─── Rooms ───────────────────────────────────────────────────────────────────

export interface RoomCategory {
  id: number
  name: string
  slug: string
  description: string
}

export interface Amenity {
  id: number
  name: string
  icon: string
}

export interface RoomImage {
  id: number
  image: string
  alt_text: string
  is_primary: boolean
}

export interface Room {
  id: number
  name: string
  slug: string
  category: RoomCategory
  description: string
  short_description: string
  max_adults: number
  max_children: number
  max_occupancy: number
  bed_configuration: string
  size_sqm: number | null
  floor: number | null
  price_per_night: string
  is_available: boolean
  is_active: boolean
  images: RoomImage[]
  amenities: Amenity[]
  primary_image: string | null
}

export interface RoomAvailability {
  room_id: number
  available: boolean
  unavailable_dates: string[]
}

// ─── Bookings ─────────────────────────────────────────────────────────────────

export type BookingStatus =
  | 'pending'
  | 'awaiting_payment'
  | 'confirmed'
  | 'checked_in'
  | 'checked_out'
  | 'cancellation_requested'
  | 'cancelled'

export type PaymentStatus = 'unpaid' | 'partial' | 'paid' | 'refunded' | 'failed'

export interface BookingRoom {
  id: number
  room: Room
  price_per_night: string
  total_price: string
}

export interface Booking {
  id: number
  booking_reference: string
  status: BookingStatus
  payment_status: PaymentStatus
  guest: User
  check_in_date: string
  check_out_date: string
  num_adults: number
  num_children: number
  num_nights: number
  rooms: BookingRoom[]
  subtotal: string
  taxes_fees: string
  total_amount: string
  special_requests: string
  created_at: string
  updated_at: string
  confirmed_at: string | null
  checked_in_at: string | null
  checked_out_at: string | null
}

export interface CreateBookingPayload {
  room_ids: number[]
  check_in_date: string
  check_out_date: string
  num_adults: number
  num_children: number
  special_requests?: string
}

// ─── Payments ─────────────────────────────────────────────────────────────────

export interface PaymentInitResponse {
  authorization_url: string
  access_code: string
  reference: string
}

export interface Payment {
  id: number
  booking: number
  reference: string
  amount: string
  status: string
  channel: string | null
  paid_at: string | null
  created_at: string
}

// ─── Experiences ─────────────────────────────────────────────────────────────

export interface Experience {
  id: number
  title: string
  slug: string
  description: string
  short_description: string
  image: string | null
  category: string
  price: string | null
  is_free: boolean
  is_active: boolean
  display_order: number
}

// ─── Dining ──────────────────────────────────────────────────────────────────

export interface MenuCategory {
  id: number
  name: string
  description: string
  display_order: number
}

export interface MenuItem {
  id: number
  category: MenuCategory
  name: string
  description: string
  price: string
  image: string | null
  is_available: boolean
  is_vegetarian: boolean
  is_vegan: boolean
  is_gluten_free: boolean
  allergens: string
  display_order: number
}

// ─── Gallery ─────────────────────────────────────────────────────────────────

export interface GalleryImage {
  id: number
  image: string
  alt_text: string
  caption: string
  category: string
  display_order: number
}

// ─── Events ──────────────────────────────────────────────────────────────────

export interface EventVenue {
  id: number
  name: string
  description: string
  capacity: number | null
  images: string[]
  amenities: string
  is_active: boolean
}

export interface EventEnquiryPayload {
  full_name: string
  email: string
  phone_number: string
  event_type: string
  event_date: string
  expected_attendees: number
  venue_id?: number
  message: string
  catering_required: boolean
}

// ─── Testimonials ─────────────────────────────────────────────────────────────

export interface Testimonial {
  id: number
  guest_name: string
  review_text: string
  rating: number
  visit_date: string | null
  is_approved: boolean
}

// ─── FAQ ─────────────────────────────────────────────────────────────────────

export interface FAQ {
  id: number
  question: string
  answer: string
  category: string
  display_order: number
}

// ─── Contact ─────────────────────────────────────────────────────────────────

export interface ContactPayload {
  full_name: string
  email: string
  phone_number?: string
  subject: string
  message: string
}

// ─── Newsletter ───────────────────────────────────────────────────────────────

export interface NewsletterPayload {
  email: string
  consent: boolean
}

// ─── Website Settings ─────────────────────────────────────────────────────────

export interface WebsiteSettings {
  site_name: string
  tagline: string
  phone_primary: string
  phone_secondary: string | null
  email_primary: string
  email_bookings: string | null
  address: string
  city: string
  state: string
  country: string
  whatsapp_number: string | null
  facebook_url: string | null
  instagram_url: string | null
  twitter_url: string | null
  check_in_time: string
  check_out_time: string
  google_maps_embed_url: string | null
  cancellation_policy: string
  privacy_policy: string
  terms_conditions: string
}

// ─── API response wrappers ───────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiError {
  message?: string
  detail?: string
  [key: string]: unknown
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

export interface DashboardSummary {
  total_bookings: number
  upcoming_bookings: number
  past_bookings: number
  pending_bookings: number
  cancelled_bookings: number
}
