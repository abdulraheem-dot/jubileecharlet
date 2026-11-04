import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Users, Bed, Maximize2, CheckCircle, ArrowLeft, ChevronLeft, ChevronRight, X } from 'lucide-react'
import { roomsApi } from '@/services/api/rooms'
import { formatCurrency, getImageUrl } from '@/utils'
import { Skeleton } from '@/components/ui/Skeleton'
import BookingForm from '@/features/bookings/BookingForm'

export default function RoomDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const [activeImg, setActiveImg] = useState(0)
  const [lightboxOpen, setLightboxOpen] = useState(false)

  const { data: room, isLoading, error } = useQuery({
    queryKey: ['room', slug],
    queryFn: () => roomsApi.getRoom(slug!),
    enabled: !!slug,
  })

  if (isLoading) {
    return (
      <div className="pt-18 min-h-screen bg-white">
        <div className="container-xl px-4 sm:px-6 lg:px-8 py-12">
          <Skeleton className="h-96 w-full rounded-2xl mb-8" />
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-4">
              <Skeleton className="h-8 w-2/3" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
            <Skeleton className="h-80 rounded-2xl" />
          </div>
        </div>
      </div>
    )
  }

  if (error || !room) {
    return (
      <div className="pt-18 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="font-display text-2xl font-bold mb-3">Room Not Found</h1>
          <p className="text-gray-600 mb-6">This room doesn't exist or is no longer available.</p>
          <Link to="/accommodation" className="btn-primary">Browse All Rooms</Link>
        </div>
      </div>
    )
  }

  const images = room.images.length > 0
    ? room.images.map(i => ({ url: getImageUrl(i.image), alt: i.alt_text || room.name }))
    : [{ url: '/placeholder-room.jpg', alt: room.name }]

  return (
    <div className="pt-18 min-h-screen bg-white">
      {/* Breadcrumb */}
      <div className="bg-brand-light-grey border-b border-gray-200">
        <div className="container-xl px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Link to="/" className="hover:text-brand-dark-green transition-colors">Home</Link>
            <span>/</span>
            <Link to="/accommodation" className="hover:text-brand-dark-green transition-colors">Accommodation</Link>
            <span>/</span>
            <span className="text-brand-black font-medium">{room.name}</span>
          </div>
        </div>
      </div>

      <div className="container-xl px-4 sm:px-6 lg:px-8 py-10">
        {/* Back button */}
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-gray-600 hover:text-brand-dark-green transition-colors mb-6">
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>

        {/* Gallery */}
        <div className="mb-10">
          {/* Main image */}
          <div
            className="relative rounded-2xl overflow-hidden aspect-[16/7] cursor-zoom-in mb-3"
            onClick={() => setLightboxOpen(true)}
          >
            <img
              src={images[activeImg].url}
              alt={images[activeImg].alt}
              className="w-full h-full object-cover"
            />
            {images.length > 1 && (
              <>
                <button
                  onClick={(e) => { e.stopPropagation(); setActiveImg((activeImg - 1 + images.length) % images.length) }}
                  className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/40 hover:bg-black/60 rounded-full flex items-center justify-center text-white transition-colors"
                  aria-label="Previous image"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); setActiveImg((activeImg + 1) % images.length) }}
                  className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/40 hover:bg-black/60 rounded-full flex items-center justify-center text-white transition-colors"
                  aria-label="Next image"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/50 text-white text-xs px-3 py-1 rounded-full">
                  {activeImg + 1} / {images.length}
                </div>
              </>
            )}
          </div>

          {/* Thumbnails */}
          {images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
              {images.map((img, i) => (
                <button
                  key={i}
                  onClick={() => setActiveImg(i)}
                  className={`shrink-0 rounded-xl overflow-hidden w-20 h-14 border-2 transition-all ${i === activeImg ? 'border-brand-dark-green' : 'border-transparent opacity-70 hover:opacity-100'}`}
                  aria-label={`View image ${i + 1}`}
                >
                  <img src={img.url} alt={img.alt} className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Content grid */}
        <div className="grid lg:grid-cols-3 gap-10">
          {/* Room details */}
          <div className="lg:col-span-2">
            <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
              <div>
                <span className="bg-brand-light-green text-brand-dark-green text-xs font-semibold px-3 py-1 rounded-full mb-2 inline-block">
                  {room.category.name}
                </span>
                <h1 className="font-display text-3xl sm:text-4xl font-bold text-brand-black">{room.name}</h1>
              </div>
              <div className="text-right">
                <div className="text-gray-500 text-sm">From</div>
                <div className="font-display text-3xl font-bold text-brand-dark-green">{formatCurrency(room.price_per_night)}</div>
                <div className="text-gray-500 text-sm">per night</div>
              </div>
            </div>

            {/* Quick stats */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-8">
              <div className="bg-brand-light-grey rounded-xl p-4 flex items-center gap-3">
                <Users className="w-5 h-5 text-brand-dark-green shrink-0" />
                <div>
                  <div className="text-xs text-gray-500">Occupancy</div>
                  <div className="font-semibold text-sm">Up to {room.max_occupancy} guests</div>
                </div>
              </div>
              <div className="bg-brand-light-grey rounded-xl p-4 flex items-center gap-3">
                <Bed className="w-5 h-5 text-brand-dark-green shrink-0" />
                <div>
                  <div className="text-xs text-gray-500">Beds</div>
                  <div className="font-semibold text-sm">{room.bed_configuration}</div>
                </div>
              </div>
              {room.size_sqm && (
                <div className="bg-brand-light-grey rounded-xl p-4 flex items-center gap-3">
                  <Maximize2 className="w-5 h-5 text-brand-dark-green shrink-0" />
                  <div>
                    <div className="text-xs text-gray-500">Size</div>
                    <div className="font-semibold text-sm">{room.size_sqm} m²</div>
                  </div>
                </div>
              )}
            </div>

            {/* Description */}
            <div className="mb-8">
              <h2 className="font-display font-bold text-xl mb-3">About This Room</h2>
              <p className="text-gray-700 leading-relaxed">{room.description}</p>
            </div>

            {/* Amenities */}
            {room.amenities.length > 0 && (
              <div className="mb-8">
                <h2 className="font-display font-bold text-xl mb-4">Amenities</h2>
                <div className="grid sm:grid-cols-2 gap-3">
                  {room.amenities.map((a) => (
                    <div key={a.id} className="flex items-center gap-2.5 text-sm text-gray-700">
                      <CheckCircle className="w-4 h-4 text-brand-dark-green shrink-0" />
                      {a.name}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Policies */}
            <div className="bg-brand-light-grey rounded-2xl p-5">
              <h2 className="font-display font-bold text-base mb-3">Policies</h2>
              <div className="grid sm:grid-cols-2 gap-3 text-sm text-gray-600">
                <div><span className="font-medium text-brand-black">Check-in:</span> From 2:00 PM</div>
                <div><span className="font-medium text-brand-black">Check-out:</span> By 12:00 PM</div>
                <div><span className="font-medium text-brand-black">Cancellation:</span> See policy</div>
                <div><span className="font-medium text-brand-black">Payment:</span> Due at booking</div>
              </div>
            </div>
          </div>

          {/* Booking panel */}
          <div id="book">
            <div className="bg-white border border-gray-100 rounded-2xl shadow-sm p-6 sticky top-24">
              <div className="mb-4 pb-4 border-b border-gray-100">
                <div className="font-display text-2xl font-bold text-brand-dark-green">{formatCurrency(room.price_per_night)}</div>
                <div className="text-gray-500 text-sm">per night</div>
              </div>

              {room.is_available ? (
                <BookingForm room={room} />
              ) : (
                <div className="text-center py-6">
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <X className="w-6 h-6 text-gray-400" />
                  </div>
                  <p className="font-medium text-gray-700 mb-1">Not Available</p>
                  <p className="text-gray-500 text-sm mb-4">This room is currently not available for booking.</p>
                  <Link to="/accommodation" className="btn-secondary w-full justify-center">
                    Browse Other Rooms
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Lightbox */}
      {lightboxOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center"
          onClick={() => setLightboxOpen(false)}
          role="dialog"
          aria-modal="true"
          aria-label="Image gallery"
        >
          <button
            className="absolute top-4 right-4 w-10 h-10 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center text-white transition-colors"
            onClick={() => setLightboxOpen(false)}
            aria-label="Close gallery"
          >
            <X className="w-5 h-5" />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); setActiveImg((activeImg - 1 + images.length) % images.length) }}
            className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center text-white transition-colors"
            aria-label="Previous image"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
          <img
            src={images[activeImg].url}
            alt={images[activeImg].alt}
            className="max-w-[90vw] max-h-[90vh] object-contain"
            onClick={(e) => e.stopPropagation()}
          />
          <button
            onClick={(e) => { e.stopPropagation(); setActiveImg((activeImg + 1) % images.length) }}
            className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center text-white transition-colors"
            aria-label="Next image"
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        </div>
      )}
    </div>
  )
}
