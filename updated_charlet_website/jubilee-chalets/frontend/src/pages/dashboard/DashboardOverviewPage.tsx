import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Calendar, CheckCircle, Clock, XCircle, ArrowRight } from 'lucide-react'
import { bookingsApi } from '@/services/api/bookings'
import { useAuth } from '@/features/authentication/AuthContext'
import { formatDate, formatCurrency, getBookingStatusLabel } from '@/utils'
import { Skeleton } from '@/components/ui/Skeleton'
import Badge from '@/components/ui/Badge'

export default function DashboardOverviewPage() {
  const { user } = useAuth()

  const { data: summary } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: bookingsApi.getDashboardSummary,
  })

  const { data: bookings, isLoading } = useQuery({
    queryKey: ['my-bookings', { page: 1 }],
    queryFn: () => bookingsApi.getMyBookings({ page: 1 }),
  })

  const stats = [
    { label: 'Total Bookings', value: summary?.total_bookings ?? 0, icon: Calendar, color: 'bg-blue-50 text-blue-600' },
    { label: 'Upcoming Stays', value: summary?.upcoming_bookings ?? 0, icon: Clock, color: 'bg-amber-50 text-amber-600' },
    { label: 'Confirmed', value: summary?.past_bookings ?? 0, icon: CheckCircle, color: 'bg-green-50 text-green-600' },
    { label: 'Cancelled', value: summary?.cancelled_bookings ?? 0, icon: XCircle, color: 'bg-red-50 text-red-600' },
  ]

  const statusVariantMap: Record<string, 'green' | 'yellow' | 'red' | 'blue' | 'gray'> = {
    confirmed: 'green',
    awaiting_payment: 'yellow',
    pending: 'yellow',
    checked_in: 'blue',
    checked_out: 'gray',
    cancelled: 'red',
    cancellation_requested: 'yellow',
  }

  return (
    <div>
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="font-display text-2xl sm:text-3xl font-bold text-brand-black">
          Welcome back, {user?.first_name}!
        </h1>
        <p className="text-gray-600 mt-1">Here's an overview of your bookings and account.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-2xl border border-gray-100 p-5">
            <div className={`w-10 h-10 rounded-xl ${color} flex items-center justify-center mb-3`}>
              <Icon className="w-5 h-5" />
            </div>
            <div className="font-display text-2xl font-bold text-brand-black">{value}</div>
            <div className="text-gray-500 text-sm mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      {/* Recent bookings */}
      <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="font-display font-bold text-lg">Recent Bookings</h2>
          <Link to="/dashboard/bookings" className="text-sm text-brand-dark-green hover:underline flex items-center gap-1">
            View all <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        {isLoading ? (
          <div className="p-6 space-y-4">
            {[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full rounded-xl" />)}
          </div>
        ) : !bookings?.results.length ? (
          <div className="text-center py-16 px-6">
            <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <h3 className="font-medium text-gray-600 mb-2">No bookings yet</h3>
            <p className="text-gray-500 text-sm mb-5">Ready for a getaway? Book your first stay with us.</p>
            <Link to="/accommodation" className="btn-primary">Browse Rooms</Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {bookings.results.slice(0, 5).map((booking) => (
              <Link
                key={booking.id}
                to={`/dashboard/bookings/${booking.id}`}
                className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors group"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="font-semibold text-sm text-brand-black">
                      {booking.rooms?.[0]?.room.name ?? 'Booking'}
                    </span>
                    <Badge variant={statusVariantMap[booking.status] ?? 'gray'}>
                      {getBookingStatusLabel(booking.status)}
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-500 truncate">
                    Ref: {booking.booking_reference} · {formatDate(booking.check_in_date)} – {formatDate(booking.check_out_date)}
                  </div>
                </div>
                <div className="text-right ml-4 shrink-0">
                  <div className="font-semibold text-sm text-brand-dark-green">{formatCurrency(booking.total_amount)}</div>
                  <ArrowRight className="w-4 h-4 text-gray-400 ml-auto mt-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
