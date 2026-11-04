import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Calendar, ArrowRight } from 'lucide-react'
import { bookingsApi } from '@/services/api/bookings'
import { formatDate, formatCurrency, getBookingStatusLabel } from '@/utils'
import { Skeleton } from '@/components/ui/Skeleton'
import Badge from '@/components/ui/Badge'

const statusVariantMap: Record<string, 'green' | 'yellow' | 'red' | 'blue' | 'gray'> = {
  confirmed: 'green',
  awaiting_payment: 'yellow',
  pending: 'yellow',
  checked_in: 'blue',
  checked_out: 'gray',
  cancelled: 'red',
  cancellation_requested: 'yellow',
}

export default function DashboardBookingsPage() {
  const [filter, setFilter] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['my-bookings', { status: filter }],
    queryFn: () => bookingsApi.getMyBookings({ status: filter || undefined }),
  })

  const filterOptions = [
    { value: '', label: 'All Bookings' },
    { value: 'confirmed', label: 'Confirmed' },
    { value: 'pending', label: 'Pending' },
    { value: 'awaiting_payment', label: 'Awaiting Payment' },
    { value: 'checked_in', label: 'Checked In' },
    { value: 'checked_out', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' },
  ]

  return (
    <div>
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <h1 className="font-display text-2xl font-bold text-brand-black">My Bookings</h1>
        <Link to="/accommodation" className="btn-primary text-sm">Book a Room</Link>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-6 scrollbar-hide">
        {filterOptions.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setFilter(opt.value)}
            className={`shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              filter === opt.value
                ? 'bg-brand-dark-green text-white'
                : 'bg-white text-gray-600 border border-gray-200 hover:border-brand-dark-green'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Bookings list */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-32 w-full rounded-2xl" />)}
        </div>
      ) : !data?.results.length ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
          <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <h3 className="font-medium text-gray-600 mb-2">No bookings found</h3>
          <p className="text-gray-500 text-sm mb-5">
            {filter ? 'No bookings with this status.' : 'You haven\'t made any bookings yet.'}
          </p>
          <Link to="/accommodation" className="btn-primary">Browse Accommodation</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {data.results.map((booking) => (
            <Link
              key={booking.id}
              to={`/dashboard/bookings/${booking.id}`}
              className="block bg-white rounded-2xl border border-gray-100 p-5 hover:border-brand-dark-green transition-colors group"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <h3 className="font-display font-bold text-base text-brand-black">
                      {booking.rooms?.[0]?.room.name ?? 'Room Booking'}
                    </h3>
                    <Badge variant={statusVariantMap[booking.status] ?? 'gray'}>
                      {getBookingStatusLabel(booking.status)}
                    </Badge>
                    {booking.payment_status === 'paid' && (
                      <Badge variant="green">Paid</Badge>
                    )}
                  </div>
                  <p className="text-gray-500 text-sm">
                    Ref: <span className="font-mono font-medium text-brand-black">{booking.booking_reference}</span>
                  </p>
                  <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-600">
                    <span>Check-in: {formatDate(booking.check_in_date)}</span>
                    <span>Check-out: {formatDate(booking.check_out_date)}</span>
                    <span>{booking.num_nights} night{booking.num_nights !== 1 ? 's' : ''}</span>
                    <span>{booking.num_adults} adult{booking.num_adults !== 1 ? 's' : ''}</span>
                  </div>
                </div>
                <div className="flex items-center gap-4 shrink-0">
                  <div className="text-right">
                    <div className="font-display font-bold text-lg text-brand-dark-green">
                      {formatCurrency(booking.total_amount)}
                    </div>
                    <div className="text-xs text-gray-500">Total</div>
                  </div>
                  <ArrowRight className="w-5 h-5 text-gray-400 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
