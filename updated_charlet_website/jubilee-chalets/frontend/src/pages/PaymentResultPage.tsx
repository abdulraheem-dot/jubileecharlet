import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { paymentsApi } from '@/services/api/payments'

export default function PaymentResultPage() {
  const [searchParams] = useSearchParams()
  const reference = searchParams.get('reference') ?? searchParams.get('trxref')
  const [status, setStatus] = useState<'verifying' | 'success' | 'failed'>('verifying')

  const verify = useMutation({
    mutationFn: () => paymentsApi.verifyPayment(reference!),
    onSuccess: (data) => {
      setStatus(data.status === 'success' ? 'success' : 'failed')
    },
    onError: () => setStatus('failed'),
  })

  useEffect(() => {
    if (reference) verify.mutate()
    else setStatus('failed')
  }, [reference])

  if (status === 'verifying') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-brand-dark-green animate-spin mx-auto mb-4" />
          <h2 className="font-display text-2xl font-bold mb-2">Verifying Payment…</h2>
          <p className="text-gray-600">Please wait while we confirm your payment.</p>
        </div>
      </div>
    )
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-5">
            <CheckCircle className="w-10 h-10 text-brand-dark-green" />
          </div>
          <h1 className="font-display text-3xl font-bold text-brand-black mb-3">Payment Successful!</h1>
          <p className="text-gray-600 mb-2">Your booking has been confirmed.</p>
          <p className="text-gray-500 text-sm mb-8">Reference: <span className="font-mono font-medium text-brand-black">{reference}</span></p>
          <div className="flex gap-3 justify-center flex-wrap">
            <Link to="/dashboard/bookings" className="btn-primary">View My Bookings</Link>
            <Link to="/" className="btn-secondary">Back to Home</Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-5">
          <XCircle className="w-10 h-10 text-red-600" />
        </div>
        <h1 className="font-display text-3xl font-bold text-brand-black mb-3">Payment Not Confirmed</h1>
        <p className="text-gray-600 mb-8">
          We could not verify your payment. If you were charged, please contact us with your reference number and we'll resolve it promptly.
        </p>
        <div className="flex gap-3 justify-center flex-wrap">
          <Link to="/dashboard/bookings" className="btn-primary">My Bookings</Link>
          <Link to="/contact" className="btn-secondary">Contact Support</Link>
        </div>
      </div>
    </div>
  )
}
