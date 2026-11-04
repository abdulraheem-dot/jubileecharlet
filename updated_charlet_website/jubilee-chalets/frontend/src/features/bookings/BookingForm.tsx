import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Calendar, Users, FileText } from 'lucide-react'
import { bookingsApi } from '@/services/api/bookings'
import { useAuth } from '@/features/authentication/AuthContext'
import { calculateNights, formatCurrency } from '@/utils'
import type { Room } from '@/types'
import Button from '@/components/ui/Button'

interface Props {
  room: Room
}

export default function BookingForm({ room }: Props) {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const today = new Date().toISOString().split('T')[0]
  const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0]

  const [checkIn, setCheckIn] = useState(today)
  const [checkOut, setCheckOut] = useState(tomorrow)
  const [adults, setAdults] = useState(1)
  const [children, setChildren] = useState(0)
  const [requests, setRequests] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})

  const nights = calculateNights(checkIn, checkOut)
  const pricePerNight = parseFloat(room.price_per_night)
  const subtotal = pricePerNight * nights

  const mutation = useMutation({
    mutationFn: () => bookingsApi.createBooking({
      room_ids: [room.id],
      check_in_date: checkIn,
      check_out_date: checkOut,
      num_adults: adults,
      num_children: children,
      special_requests: requests,
    }),
    onSuccess: (booking) => {
      toast.success('Booking created successfully!')
      navigate(`/dashboard/bookings/${booking.id}`)
    },
    onError: (err: any) => {
      const data = err?.response?.data
      if (data && typeof data === 'object') {
        const errs: Record<string, string> = {}
        Object.entries(data).forEach(([k, v]) => {
          errs[k] = Array.isArray(v) ? (v as string[]).join(' ') : String(v)
        })
        setErrors(errs)
        toast.error(errs.non_field_errors ?? errs.detail ?? 'Please check your booking details')
      } else {
        toast.error('Booking failed. Please try again.')
      }
    },
  })

  const validate = (): boolean => {
    const e: Record<string, string> = {}
    if (!checkIn) e.check_in_date = 'Check-in date is required'
    if (!checkOut) e.check_out_date = 'Check-out date is required'
    if (checkIn >= checkOut) e.check_out_date = 'Check-out must be after check-in'
    if (nights < 1) e.check_out_date = 'Minimum stay is 1 night'
    if (adults + children > room.max_occupancy) e.num_adults = `Maximum occupancy is ${room.max_occupancy}`
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = () => {
    if (!isAuthenticated) {
      toast.error('Please sign in to make a booking')
      navigate('/login', { state: { from: { pathname: `/accommodation/${room.slug}` } } })
      return
    }
    if (validate()) mutation.mutate()
  }

  return (
    <div className="space-y-4">
      {/* Dates */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">
            <Calendar className="w-3 h-3 inline mr-1" />Check-in
          </label>
          <input
            type="date"
            value={checkIn}
            min={today}
            onChange={(e) => { setCheckIn(e.target.value); setErrors({}) }}
            className={`input-field text-sm ${errors.check_in_date ? 'input-error' : ''}`}
            aria-label="Check-in date"
          />
          {errors.check_in_date && <p className="text-red-600 text-xs mt-1">{errors.check_in_date}</p>}
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">
            <Calendar className="w-3 h-3 inline mr-1" />Check-out
          </label>
          <input
            type="date"
            value={checkOut}
            min={checkIn || today}
            onChange={(e) => { setCheckOut(e.target.value); setErrors({}) }}
            className={`input-field text-sm ${errors.check_out_date ? 'input-error' : ''}`}
            aria-label="Check-out date"
          />
          {errors.check_out_date && <p className="text-red-600 text-xs mt-1">{errors.check_out_date}</p>}
        </div>
      </div>

      {/* Guests */}
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">
          <Users className="w-3 h-3 inline mr-1" />Guests
        </label>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <div className="text-xs text-gray-500 mb-1">Adults</div>
            <div className="flex items-center gap-2 bg-brand-light-grey rounded-lg px-3 py-2">
              <button onClick={() => setAdults(Math.max(1, adults - 1))} className="w-6 h-6 rounded-full bg-white border border-gray-200 hover:border-brand-dark-green flex items-center justify-center text-sm transition-colors" aria-label="Decrease adults">−</button>
              <span className="flex-1 text-center font-medium text-sm">{adults}</span>
              <button onClick={() => setAdults(Math.min(room.max_adults, adults + 1))} className="w-6 h-6 rounded-full bg-white border border-gray-200 hover:border-brand-dark-green flex items-center justify-center text-sm transition-colors" aria-label="Increase adults">+</button>
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500 mb-1">Children</div>
            <div className="flex items-center gap-2 bg-brand-light-grey rounded-lg px-3 py-2">
              <button onClick={() => setChildren(Math.max(0, children - 1))} className="w-6 h-6 rounded-full bg-white border border-gray-200 hover:border-brand-dark-green flex items-center justify-center text-sm transition-colors" aria-label="Decrease children">−</button>
              <span className="flex-1 text-center font-medium text-sm">{children}</span>
              <button onClick={() => setChildren(Math.min(room.max_children, children + 1))} className="w-6 h-6 rounded-full bg-white border border-gray-200 hover:border-brand-dark-green flex items-center justify-center text-sm transition-colors" aria-label="Increase children">+</button>
            </div>
          </div>
        </div>
        {errors.num_adults && <p className="text-red-600 text-xs mt-1">{errors.num_adults}</p>}
        <p className="text-xs text-gray-500 mt-1.5">Max capacity: {room.max_occupancy} guests</p>
      </div>

      {/* Special requests */}
      <div>
        <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">
          <FileText className="w-3 h-3 inline mr-1" />Special Requests (optional)
        </label>
        <textarea
          value={requests}
          onChange={(e) => setRequests(e.target.value)}
          placeholder="Any special requirements or preferences…"
          rows={3}
          className="input-field text-sm resize-none"
        />
      </div>

      {/* Price breakdown */}
      {nights > 0 && (
        <div className="bg-brand-light-grey rounded-xl p-4 space-y-2 text-sm">
          <div className="flex justify-between text-gray-600">
            <span>{formatCurrency(room.price_per_night)} × {nights} night{nights !== 1 ? 's' : ''}</span>
            <span>{formatCurrency(subtotal)}</span>
          </div>
          <div className="border-t border-gray-200 pt-2 flex justify-between font-semibold text-brand-black">
            <span>Estimated Total</span>
            <span className="text-brand-dark-green">{formatCurrency(subtotal)}</span>
          </div>
          <p className="text-xs text-gray-500">Final price calculated and verified by our server</p>
        </div>
      )}

      <Button
        onClick={handleSubmit}
        isLoading={mutation.isPending}
        fullWidth
        size="lg"
        className="mt-2"
      >
        {isAuthenticated ? 'Request to Book' : 'Sign In to Book'}
      </Button>

      <p className="text-xs text-gray-500 text-center">
        You won't be charged yet. Booking confirmed after verification.
      </p>
    </div>
  )
}
