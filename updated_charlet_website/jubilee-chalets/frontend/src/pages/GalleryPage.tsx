import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { X, ChevronLeft, ChevronRight, ZoomIn } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { contentApi } from '@/services/api/content'
import { getImageUrl } from '@/utils'
import SectionReveal from '@/components/common/SectionReveal'

const CATEGORIES = [
  { value: '', label: 'All' },
  { value: 'rooms', label: 'Rooms' },
  { value: 'dining', label: 'Dining' },
  { value: 'outdoor', label: 'Outdoor' },
  { value: 'recreation', label: 'Recreation' },
  { value: 'events', label: 'Events' },
]

export default function GalleryPage() {
  const [category, setCategory] = useState('')
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null)

  const { data: images, isLoading } = useQuery({
    queryKey: ['gallery', category],
    queryFn: () => contentApi.getGalleryImages(category || undefined),
  })

  const openLightbox = (i: number) => { setLightboxIndex(i); document.body.style.overflow = 'hidden' }
  const closeLightbox = () => { setLightboxIndex(null); document.body.style.overflow = '' }
  const prev = () => setLightboxIndex((i) => (i !== null && images ? (i - 1 + images.length) % images.length : null))
  const next = () => setLightboxIndex((i) => (i !== null && images ? (i + 1) % images.length : null))

  // Keyboard navigation for lightbox
  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') closeLightbox()
    if (e.key === 'ArrowLeft') prev()
    if (e.key === 'ArrowRight') next()
  }

  return (
    <div className="pt-18 min-h-screen bg-white">
      {/* Hero */}
      <section className="bg-brand-forest-green text-white py-20 px-4 sm:px-6 lg:px-8">
        <div className="container-xl text-center">
          <span className="text-green-300 text-sm font-semibold uppercase tracking-widest block mb-3">Gallery</span>
          <h1 className="font-display text-4xl sm:text-5xl font-bold mb-4">Photo Gallery</h1>
          <p className="text-white/75 text-lg max-w-xl mx-auto">
            A glimpse into life at Jubilee Chalets Epe — rooms, dining, recreation, and memorable moments.
          </p>
        </div>
      </section>

      {/* Gallery */}
      <section className="section-padding">
        <div className="container-xl">
          {/* Category filters */}
          <div className="flex gap-2 overflow-x-auto pb-2 mb-8 justify-center scrollbar-hide">
            {CATEGORIES.map((c) => (
              <button
                key={c.value}
                onClick={() => setCategory(c.value)}
                className={`shrink-0 px-5 py-2 rounded-full text-sm font-medium transition-colors ${category === c.value ? 'bg-brand-dark-green text-white' : 'bg-white border border-gray-200 text-gray-600 hover:border-brand-dark-green'}`}
              >
                {c.label}
              </button>
            ))}
          </div>

          {isLoading ? (
            <div className="columns-2 sm:columns-3 lg:columns-4 gap-3 space-y-3">
              {Array.from({ length: 12 }).map((_, i) => (
                <div key={i} className="skeleton rounded-xl" style={{ height: `${160 + (i % 3) * 60}px`, breakInside: 'avoid' }} />
              ))}
            </div>
          ) : !images?.length ? (
            <div className="text-center py-20">
              <p className="text-gray-500">Gallery images will be available soon.</p>
            </div>
          ) : (
            <div className="columns-2 sm:columns-3 lg:columns-4 gap-3">
              {images.map((img, i) => (
                <SectionReveal key={img.id} className="break-inside-avoid mb-3">
                  <button
                    className="relative group w-full rounded-xl overflow-hidden cursor-zoom-in focus-visible:outline-2 focus-visible:outline-brand-dark-green"
                    onClick={() => openLightbox(i)}
                    aria-label={`View ${img.alt_text || 'gallery image'}`}
                  >
                    <img
                      src={getImageUrl(img.image)}
                      alt={img.alt_text || ''}
                      className="w-full object-cover transition-transform duration-500 group-hover:scale-105"
                      loading="lazy"
                    />
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center">
                      <ZoomIn className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                    {img.caption && (
                      <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 translate-y-full group-hover:translate-y-0 transition-transform">
                        <p className="text-white text-xs">{img.caption}</p>
                      </div>
                    )}
                  </button>
                </SectionReveal>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* Lightbox */}
      <AnimatePresence>
        {lightboxIndex !== null && images && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center"
            onClick={closeLightbox}
            onKeyDown={handleKey}
            tabIndex={0}
            role="dialog"
            aria-modal="true"
            aria-label="Image gallery"
          >
            {/* Close */}
            <button
              className="absolute top-4 right-4 w-10 h-10 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center text-white transition-colors z-10"
              onClick={(e) => { e.stopPropagation(); closeLightbox() }}
              aria-label="Close"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Counter */}
            <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-black/50 text-white text-sm px-4 py-1.5 rounded-full">
              {lightboxIndex + 1} / {images.length}
            </div>

            {/* Prev */}
            <button
              className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center text-white transition-colors"
              onClick={(e) => { e.stopPropagation(); prev() }}
              aria-label="Previous image"
            >
              <ChevronLeft className="w-6 h-6" />
            </button>

            {/* Image */}
            <motion.img
              key={lightboxIndex}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.2 }}
              src={getImageUrl(images[lightboxIndex].image)}
              alt={images[lightboxIndex].alt_text || ''}
              className="max-w-[90vw] max-h-[90vh] object-contain"
              onClick={(e) => e.stopPropagation()}
            />

            {/* Next */}
            <button
              className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center text-white transition-colors"
              onClick={(e) => { e.stopPropagation(); next() }}
              aria-label="Next image"
            >
              <ChevronRight className="w-6 h-6" />
            </button>

            {/* Caption */}
            {images[lightboxIndex].caption && (
              <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-black/60 text-white text-sm px-4 py-2 rounded-full max-w-lg text-center">
                {images[lightboxIndex].caption}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
