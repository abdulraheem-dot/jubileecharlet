import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { ArrowLeft, Calendar, Users, CreditCard, AlertCircle } from 'lucide-react'
import { bookingsApi } from '@/services/api/bookings'
import { paymentsApi } from '@/services/api/payments'
import { formatDate, formatCurrency, getBookingStatusLabel } from '@/utils'
import { Skeleton } from '@/components/ui/Skeleton'
import Badge from '@/components/ui/Badge'
import Modal from '@/components/ui/Modal'
import Button from '@/components/ui/Button'

const statusVariantMap: Record<string, 'green' | 'yellow' | 'red' | 'blue' | 'gray'> = {
  confirmed: 'green',
  awaiting_payment: 'yellow',
  pending: 'yellow',
  checked_in: 'blue',
  checked_out: 'gray',
  cancelled: 'red',
  cancellation_requested: 'yellow',
}

export default function BookingDetailPage() {
  const { id } = useParams<{ id: string }>()
  const qc = useQueryClient()
  const [cancelModal, setCancelModal] = useState(false)
  const [cancelReason, setCancelReason] = useState('')

  const { data: booking, isLoading } = useQuery({
    queryKey: ['booking', id],
    queryFn: () => bookingsApi.getBooking(Number(id)),
    enabled: !!id,
  })

  const cancelMutation = useMutation({
    mutationFn: () => bookingsApi.requestCancellation(Number(id), cancelReason),
    onSuccess: () => {
      toast.success('Cancellation request submitted')
      qc.invalidateQueries({ queryKey: ['booking', id] })
      qc.invalidateQueries({ queryKey: ['my-bookings'] })
      setCancelModal(false)
    },
    onError: () => toast.error('Failed to submit cancellation request'),
  })

  const payMutation = useMutation({
    mutationFn: () => paymentsApi.initializePayment(Number(id)),
    onSuccess: (data) => {
      window.location.href = data.authorization_url
    },
    onError: () => toast.error('Could not initialise payment. Please try again.'),
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-48 w-full rounded-2xl" />
        <Skeleton className="h-32 w-full rounded-2xl" />
      </div>
    )
  }

  if (!booking) {
    return (
      <div className="text-center py-16">
        <h2 className="font-display text-xl font-bold text-gray-600 mb-3">Booking not found</h2>
        <Link to="/dashboard/bookings" className="btn-primary">Back to Bookings</Link>
      </div>
    )
  }

  const canPay = booking.status === 'awaiting_payment' && booking.payment_status !== 'paid'
  const canCancel = ['pending', 'awaiting_payment', 'confirmed'].includes(booking.status)

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <Link to="/dashboard/bookings" className="p-2 rounded-xl hover:bg-gray-100 transition-colors" aria-label="Back">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div>
          <h1 className="font-display text-2xl font-bold text-brand-black">Booking Details</h1>
          <p className="text-gray-500 text-sm">Ref: <span className="font-mono font-medium">{booking.booking_reference}</span></p>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main details */}
        <div className="lg:col-span-2 space-y-5">
          {/* Status card */}
          <div className="bg-white rounded-2xl border border-gray-100 p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant={statusVariantMap[booking.status] ?? 'gray'} className="text-sm">
                    {getBookingStatusLabel(booking.status)}
                  </Badge>
                  <Badge variant={booking.payment_status === 'paid' ? 'green' : 'yellow'}>
                    {booking.payment_status === 'paid' ? 'Paid' : 'Payment Pending'}
                  </Badge>
                </div>
                <h2 className="font-display font-bold text-lg text-brand-black mt-2">
                  {booking.rooms?.[0]?.room.name ?? 'Booking'}
                </h2>
                {booking.rooms.length > 1 && (
                  <p className="text-gray-500 text-sm">+{booking.rooms.length - 1} more room{booking.rooms.length > 2 ? 's' : ''}</p>
                )}
              </div>
              <div className="flex gap-2">
                {canPay && (
                  <Button onClick={() => payMutation.mutate()} isLoading={payMutation.isPending} size="sm">
                    <CreditCard className="w-4 h-4" />
                    Pay Now
                  </Button>
                )}
                {canCancel && (
                  <Button variant="secondary" size="sm" onClick={() => setCancelModal(true)}>
                    Request Cancellation
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Dates */}
          <div className="bg-white rounded-2xl border border-gray-100 p-5">
            <h3 className="font-semibold text-brand-black mb-4 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-brand-dark-green" />
              Stay Details
            </h3>
            <div className="grid sm:grid-cols-3 gap-4 text-sm">
              <div>
                <div className="text-gray-500 mb-0.5">Check-in</div>
                <div className="font-semibold">{formatDate(booking.check_in_date)}</div>
                <div className="text-gray-400 text-xs">From 2:00 PM</div>
              </div>
              <div>
                <div className="text-gray-500 mb-0.5">Check-out</div>
                <div className="font-semibold">{formatDate(booking.check_out_date)}</div>
                <div className="text-gray-400 text-xs">By 12:00 PM</div>
              </div>
              <div>
                <div className="text-gray-500 mb-0.5">Duration</div>
                <div className="font-semibold">{booking.num_nights} night{booking.num_nights !== 1 ? 's' : ''}</div>
              </div>
            </div>
          </div>

          {/* Guests */}
          <div className="bg-white rounded-2xl border border-gray-100 p-5">
            <h3 className="font-semibold text-brand-black mb-4 flex items-center gap-2">
              <Users className="w-4 h-4 text-brand-dark-green" />
              Guests
            </h3>
            <div className="flex gap-6 text-sm">
              <div>
                <span className="text-gray-500">Adults: </span>
                <span className="font-semibold">{booking.num_adults}</span>
              </div>
              <div>
                <span className="text-gray-500">Children: </span>
                <span className="font-semibold">{booking.num_children}</span>
              </div>
            </div>
            {booking.special_requests && (
              <div className="mt-3 p-3 bg-brand-light-grey rounded-xl text-sm text-gray-600">
                <span className="font-medium text-brand-black">Special requests: </span>
                {booking.special_requests}
              </div>
            )}
          </div>
        </div>

        {/* Price summary */}
        <div>
          <div className="bg-white rounded-2xl border border-gray-100 p-5 sticky top-24">
            <h3 className="font-semibold text-brand-black mb-4 flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-brand-dark-green" />
              Price Summary
            </h3>
            <div className="space-y-3 text-sm">
              {booking.rooms.map((br) => (
                <div key={br.id} className="flex justify-between text-gray-600">
                  <span>{br.room.name} ({booking.num_nights}n)</span>
                  <span>{formatCurrency(br.total_price)}</span>
                </div>
              ))}
              {parseFloat(booking.taxes_fees) > 0 && (
                <div className="flex justify-between text-gray-600">
                  <span>Taxes & fees</span>
                  <span>{formatCurrency(booking.taxes_fees)}</span>
                </div>
              )}
              <div className="border-t border-gray-100 pt-3 flex justify-between font-bold text-brand-black">
                <span>Total</span>
                <span className="text-brand-dark-green">{formatCurrency(booking.total_amount)}</span>
              </div>
            </div>

            {canPay && (
              <Button onClick={() => payMutation.mutate()} isLoading={payMutation.isPending} fullWidth className="mt-4">
                <CreditCard className="w-4 h-4" />
                Complete Payment
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Cancellation modal */}
      <Modal isOpen={cancelModal} onClose={() => setCancelModal(false)} title="Request Cancellation">
        <div className="p-6">
          <div className="flex items-start gap-3 bg-amber-50 border border-amber-200 rounded-xl p-4 mb-5">
            <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <p className="text-sm text-amber-800">
              Cancellation requests are subject to our cancellation policy. Once submitted, our team will review your request.
            </p>
          </div>
          <div className="mb-5">
            <label className="block text-sm font-medium text-brand-black mb-1.5">
              Reason for cancellation <span className="text-gray-500 font-normal">(optional)</span>
            </label>
            <textarea
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              rows={4}
              placeholder="Please let us know why you'd like to cancel…"
              className="input-field resize-none"
            />
          </div>
          <div className="flex gap-3">
            <Button variant="secondary" onClick={() => setCancelModal(false)} fullWidth>
              Keep Booking
            </Button>
            <Button variant="danger" onClick={() => cancelMutation.mutate()} isLoading={cancelMutation.isPending} fullWidth>
              Submit Request
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
