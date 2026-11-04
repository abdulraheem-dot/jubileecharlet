import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Calendar, Users, Search } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/utils'

interface Props {
  className?: string
}

export default function BookingSearchBar({ className }: Props) {
  const navigate = useNavigate()
  const today = new Date().toISOString().split('T')[0]
  const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0]

  const [checkIn, setCheckIn] = useState(today)
  const [checkOut, setCheckOut] = useState(tomorrow)
  const [adults, setAdults] = useState(2)
  const [children, setChildren] = useState(0)

  const handleSearch = () => {
    if (checkIn >= checkOut) {
      toast.error('Check-out date must be after check-in date')
      return
    }
    const params = new URLSearchParams({
      check_in: checkIn,
      check_out: checkOut,
      num_adults: String(adults),
      num_children: String(children),
    })
    navigate(`/accommodation?${params.toString()}`)
  }

  return (
    <div className={cn('bg-white rounded-2xl shadow-xl p-2', className)}>
      <div className="flex flex-col sm:flex-row gap-px">
        {/* Check-in */}
        <div className="flex-1 px-4 py-3 rounded-xl hover:bg-gray-50 transition-colors">
          <label className="block text-xs font-semibold uppercase tracking-wider mb-1 text-gray-600">
            <Calendar className="w-3 h-3 inline mr-1" />Check-in
          </label>
          <input
            type="date"
            value={checkIn}
            min={today}
            onChange={(e) => setCheckIn(e.target.value)}
            className="w-full bg-transparent text-sm font-medium text-brand-black focus:outline-none"
            aria-label="Check-in date"
          />
        </div>

        <div className="hidden sm:block w-px bg-gray-200 self-stretch my-2" aria-hidden />

        {/* Check-out */}
        <div className="flex-1 px-4 py-3 rounded-xl hover:bg-gray-50 transition-colors">
          <label className="block text-xs font-semibold uppercase tracking-wider mb-1 text-gray-600">
            <Calendar className="w-3 h-3 inline mr-1" />Check-out
          </label>
          <input
            type="date"
            value={checkOut}
            min={checkIn || today}
            onChange={(e) => setCheckOut(e.target.value)}
            className="w-full bg-transparent text-sm font-medium text-brand-black focus:outline-none"
            aria-label="Check-out date"
          />
        </div>

        <div className="hidden sm:block w-px bg-gray-200 self-stretch my-2" aria-hidden />

        {/* Guests */}
        <div className="flex-1 px-4 py-3 rounded-xl hover:bg-gray-50 transition-colors">
          <label className="block text-xs font-semibold uppercase tracking-wider mb-1 text-gray-600">
            <Users className="w-3 h-3 inline mr-1" />Guests
          </label>
          <div className="flex items-center gap-3 text-sm font-medium text-brand-black">
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setAdults(Math.max(1, adults - 1))}
                className="w-5 h-5 rounded-full bg-gray-200 hover:bg-brand-dark-green hover:text-white transition-colors flex items-center justify-center text-xs"
                aria-label="Decrease adults"
              >−</button>
              <span>{adults}A</span>
              <button
                onClick={() => setAdults(Math.min(10, adults + 1))}
                className="w-5 h-5 rounded-full bg-gray-200 hover:bg-brand-dark-green hover:text-white transition-colors flex items-center justify-center text-xs"
                aria-label="Increase adults"
              >+</button>
            </div>
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setChildren(Math.max(0, children - 1))}
                className="w-5 h-5 rounded-full bg-gray-200 hover:bg-brand-dark-green hover:text-white transition-colors flex items-center justify-center text-xs"
                aria-label="Decrease children"
              >−</button>
              <span>{children}C</span>
              <button
                onClick={() => setChildren(Math.min(10, children + 1))}
                className="w-5 h-5 rounded-full bg-gray-200 hover:bg-brand-dark-green hover:text-white transition-colors flex items-center justify-center text-xs"
                aria-label="Increase children"
              >+</button>
            </div>
          </div>
        </div>

        {/* Search button */}
        <div className="px-2 flex items-center">
          <button
            onClick={handleSearch}
            className="btn-primary w-full sm:w-auto px-6 py-3.5 rounded-xl"
            aria-label="Search availability"
          >
            <Search className="w-4 h-4" />
            <span>Search</span>
          </button>
        </div>
      </div>
    </div>
  )
}
