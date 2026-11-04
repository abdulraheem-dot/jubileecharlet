import { Link } from 'react-router-dom'
import { Users, Bed, ArrowRight } from 'lucide-react'
import { motion } from 'framer-motion'
import type { Room } from '@/types'
import { formatCurrency, getImageUrl } from '@/utils'

interface Props {
  room: Room
  compact?: boolean
}

export default function RoomCard({ room, compact = false }: Props) {
  const image = room.primary_image ?? room.images?.[0]?.image
  const imageUrl = getImageUrl(image)

  return (
    <motion.article
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
      className="card group flex flex-col h-full"
    >
      {/* Image */}
      <div className="relative overflow-hidden aspect-[4/3]">
        <img
          src={imageUrl}
          alt={room.images?.[0]?.alt_text || room.name}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          loading="lazy"
          onError={(e) => { (e.target as HTMLImageElement).src = '/placeholder-room.jpg' }}
        />
        {!room.is_available && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
            <span className="bg-white text-brand-black px-4 py-1.5 rounded-full text-sm font-semibold">
              Not Available
            </span>
          </div>
        )}
        <div className="absolute top-3 left-3">
          <span className="bg-white/90 backdrop-blur-sm text-brand-dark-green text-xs font-semibold px-3 py-1 rounded-full">
            {room.category.name}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="flex flex-col flex-1 p-5">
        <h3 className="font-display font-bold text-lg text-brand-black mb-1 leading-tight">
          {room.name}
        </h3>
        <p className="text-gray-600 text-sm leading-relaxed mb-4 flex-1 line-clamp-2">
          {room.short_description}
        </p>

        {/* Details */}
        <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
          <div className="flex items-center gap-1.5">
            <Users className="w-4 h-4 text-brand-dark-green" />
            <span>Up to {room.max_occupancy}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Bed className="w-4 h-4 text-brand-dark-green" />
            <span>{room.bed_configuration}</span>
          </div>
        </div>

        {!compact && room.amenities.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {room.amenities.slice(0, 4).map((a) => (
              <span key={a.id} className="bg-brand-light-green text-brand-dark-green text-xs px-2 py-0.5 rounded-full">
                {a.name}
              </span>
            ))}
            {room.amenities.length > 4 && (
              <span className="bg-gray-100 text-gray-500 text-xs px-2 py-0.5 rounded-full">
                +{room.amenities.length - 4} more
              </span>
            )}
          </div>
        )}

        {/* Price & CTAs */}
        <div className="flex items-end justify-between mt-auto pt-3 border-t border-gray-100">
          <div>
            <div className="text-xs text-gray-500 mb-0.5">From</div>
            <div className="font-display font-bold text-xl text-brand-dark-green">
              {formatCurrency(room.price_per_night)}
            </div>
            <div className="text-xs text-gray-500">per night</div>
          </div>
          <div className="flex gap-2">
            <Link
              to={`/accommodation/${room.slug}`}
              className="btn-secondary text-xs px-4 py-2"
              aria-label={`View details for ${room.name}`}
            >
              Details
            </Link>
            {room.is_available && (
              <Link
                to={`/accommodation/${room.slug}#book`}
                className="btn-primary text-xs px-4 py-2"
                aria-label={`Book ${room.name}`}
              >
                Book
                <ArrowRight className="w-3 h-3" />
              </Link>
            )}
          </div>
        </div>
      </div>
    </motion.article>
  )
}
