import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: string | number): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return new Intl.NumberFormat('en-NG', {
    style: 'currency',
    currency: 'NGN',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num)
}

export function formatDate(dateStr: string): string {
  return new Intl.DateTimeFormat('en-NG', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date(dateStr))
}

export function formatShortDate(dateStr: string): string {
  return new Intl.DateTimeFormat('en-NG', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(dateStr))
}

export function calculateNights(checkIn: string, checkOut: string): number {
  const a = new Date(checkIn)
  const b = new Date(checkOut)
  return Math.round((b.getTime() - a.getTime()) / (1000 * 60 * 60 * 24))
}

export function getBookingStatusColor(status: string): string {
  const map: Record<string, string> = {
    pending: 'badge-yellow',
    awaiting_payment: 'badge-yellow',
    confirmed: 'badge-green',
    checked_in: 'badge-blue',
    checked_out: 'badge-gray',
    cancellation_requested: 'badge-yellow',
    cancelled: 'badge-red',
  }
  return map[status] ?? 'badge-gray'
}

export function getBookingStatusLabel(status: string): string {
  const map: Record<string, string> = {
    pending: 'Pending',
    awaiting_payment: 'Awaiting Payment',
    confirmed: 'Confirmed',
    checked_in: 'Checked In',
    checked_out: 'Checked Out',
    cancellation_requested: 'Cancellation Requested',
    cancelled: 'Cancelled',
  }
  return map[status] ?? status
}

export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength).trim() + '…'
}

export function getImageUrl(path: string | null | undefined): string {
  if (!path) return '/placeholder-room.jpg'
  if (path.startsWith('http')) return path
  const base = import.meta.env.VITE_MEDIA_URL || 'http://localhost:8000'
  return `${base}${path}`
}

export function whatsAppLink(number: string, message?: string): string {
  const clean = number.replace(/\D/g, '')
  const encoded = message ? `?text=${encodeURIComponent(message)}` : ''
  return `https://wa.me/${clean}${encoded}`
}
