import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  ArrowRight, Star, Waves, Utensils, Trees, Briefcase,
  Users, MapPin, Phone, Mail, MessageCircle, CheckCircle,
} from 'lucide-react'
import { roomsApi } from '@/services/api/rooms'
import { contentApi } from '@/services/api/content'
import RoomCard from '@/features/accommodation/RoomCard'
import { RoomCardSkeleton } from '@/components/ui/Skeleton'
import SectionReveal from '@/components/common/SectionReveal'
import BookingSearchBar from '@/components/common/BookingSearchBar'
import { whatsAppLink } from '@/utils'

// ─── Hero ─────────────────────────────────────────────────────────────────────
function Hero() {
  return (
    <section
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
      aria-label="Hero"
    >
      {/* Background image */}
      <div className="absolute inset-0 z-0">
        <img
          src="/media/gallery/18_-_Illuminated_Glass_Pavilion_Night.jpg"
          alt="Jubilee Chalets resort exterior"
          className="w-full h-full object-cover"
          fetchPriority="high"
        />
        <div className="absolute inset-0 bg-hero-overlay" />
      </div>

      <div className="relative z-10 container-xl px-4 sm:px-6 lg:px-8 text-center text-white pt-20 pb-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
        >
          <span className="inline-block bg-white/20 backdrop-blur-sm text-white/90 text-xs font-semibold uppercase tracking-widest px-4 py-2 rounded-full mb-6 border border-white/30">
            Welcome to Jubilee Chalets · Epe, Lagos
          </span>
          <h1 className="font-display text-4xl sm:text-6xl lg:text-7xl font-bold leading-tight text-shadow-lg mb-6">
            Escape the Ordinary.<br />
            <span className="text-green-300">Experience Serenity.</span>
          </h1>
          <p className="text-white/85 text-lg sm:text-xl max-w-2xl mx-auto leading-relaxed mb-10 text-shadow">
            Discover a refreshing destination for relaxation, memorable stays, and exceptional hospitality in Epe, Lagos.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link to="/accommodation" className="btn-white text-base px-8 py-4">
              Explore Our Accommodation
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link to="/accommodation" className="btn-outline-white text-base px-8 py-4">
              Book Your Stay
            </Link>
          </div>
        </motion.div>

        {/* Booking search bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="max-w-4xl mx-auto"
        >
          <BookingSearchBar />
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 1.5, repeat: Infinity }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10"
        aria-hidden
      >
        <div className="w-6 h-10 rounded-full border-2 border-white/50 flex items-start justify-center pt-2">
          <div className="w-1 h-2 rounded-full bg-white/60" />
        </div>
      </motion.div>
    </section>
  )
}

// ─── Welcome ──────────────────────────────────────────────────────────────────
function Welcome() {
  return (
    <section className="section-padding bg-white" aria-labelledby="welcome-heading">
      <div className="container-xl">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <SectionReveal>
            <div className="relative">
              <img
                src="/media/gallery/21_-_Swimming_Pool_and_Chalets.jpg"
                alt="Jubilee Chalets swimming pool and resort grounds"
                className="w-full rounded-2xl object-cover aspect-[4/3]"
                loading="lazy"
              />
              <div className="absolute -bottom-6 -right-6 bg-brand-dark-green text-white rounded-2xl p-5 shadow-xl hidden sm:block">
                <div className="font-display text-3xl font-bold">Premium</div>
                <div className="text-green-300 text-sm">Hospitality</div>
              </div>
            </div>
          </SectionReveal>

          <SectionReveal delay={0.15}>
            <span className="section-label">Welcome to Jubilee Chalets</span>
            <h2 id="welcome-heading" className="section-title mt-2 mb-5">
              A Sanctuary of<br />Comfort and Nature
            </h2>
            <p className="section-subtitle mb-5">
              Nestled in the serene surroundings of Epe, Lagos State, Jubilee Chalets offers a unique blend of modern comfort and natural beauty. Whether you're seeking a peaceful retreat, a family getaway, or a venue for your next corporate event, we have everything you need.
            </p>
            <p className="text-gray-600 leading-relaxed mb-8">
              From our well-appointed chalets to our refreshing swimming facilities, every aspect of Jubilee Chalets is designed to provide you with an unforgettable experience in one of Lagos's most tranquil destinations.
            </p>
            <div className="grid grid-cols-2 gap-4 mb-8">
              {[
                'Comfortable Accommodation',
                'Swimming & Recreation',
                'Restaurant & Dining',
                'Events & Conferences',
              ].map((f) => (
                <div key={f} className="flex items-center gap-2 text-sm text-gray-700">
                  <CheckCircle className="w-4 h-4 text-brand-dark-green shrink-0" />
                  {f}
                </div>
              ))}
            </div>
            <Link to="/about" className="btn-primary">
              Learn More About Us
              <ArrowRight className="w-4 h-4" />
            </Link>
          </SectionReveal>
        </div>
      </div>
    </section>
  )
}

// ─── Room Preview ─────────────────────────────────────────────────────────────
function RoomsPreview() {
  const { data, isLoading } = useQuery({
    queryKey: ['rooms', { featured: true }],
    queryFn: () => roomsApi.getRooms({ page_size: 3 }),
  })

  return (
    <section className="section-padding bg-brand-light-grey" aria-labelledby="rooms-heading">
      <div className="container-xl">
        <SectionReveal className="text-center max-w-2xl mx-auto mb-12">
          <span className="section-label">Our Accommodation</span>
          <h2 id="rooms-heading" className="section-title mt-2 mb-4">
            Rooms & Chalets
          </h2>
          <p className="section-subtitle">
            Choose from our selection of well-appointed rooms and chalets, each designed for your comfort and relaxation.
          </p>
        </SectionReveal>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {isLoading
            ? Array.from({ length: 3 }).map((_, i) => <RoomCardSkeleton key={i} />)
            : data?.results.map((room) => <RoomCard key={room.id} room={room} />)
          }
        </div>

        {!isLoading && (!data?.results.length) && (
          <div className="text-center py-16 text-gray-500">
            <p>Accommodation details will be available soon.</p>
          </div>
        )}

        <div className="text-center mt-12">
          <Link to="/accommodation" className="btn-primary text-base px-8 py-4">
            View All Accommodation
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </section>
  )
}

// ─── Experiences ─────────────────────────────────────────────────────────────
const experienceItems = [
  { icon: Waves,    title: 'Swimming & Recreation',  desc: 'Relax and unwind in our refreshing swimming facilities, perfect for the whole family.',        image: '/media/gallery/21_-_Swimming_Pool_and_Chalets.jpg' },
  { icon: Utensils, title: 'Dining Experience',       desc: 'Savour delicious meals prepared with fresh ingredients in our on-site restaurant.',             image: '/media/gallery/15_-_Buffet_Kitchen_Food_Service.jpg' },
  { icon: Trees,    title: 'Nature & Relaxation',     desc: 'Enjoy the natural beauty of Epe, surrounded by lush greenery and peaceful scenery.',            image: '/media/gallery/10_-_Sunny_Modern_Neighborhood_Street.jpg' },
  { icon: Briefcase,title: 'Corporate Retreats',      desc: 'A perfect setting for team-building, workshops, conferences, and corporate events.',             image: '/media/gallery/14_-_Banquet_Hall_Dining_Setup.jpg' },
  { icon: Users,    title: 'Family Outings',          desc: 'Create lasting memories with your family in our spacious, welcoming environment.',               image: '/media/gallery/11_-_Family_Group_Seating.jpg' },
  { icon: Star,     title: 'Special Events',          desc: 'Host your celebrations, anniversaries, and special occasions with us.',                          image: '/media/gallery/25_-_Celebration_Group_in_White.jpg' },
]

function Experiences() {
  return (
    <section className="section-padding bg-white" aria-labelledby="experiences-heading">
      <div className="container-xl">
        <SectionReveal className="text-center max-w-2xl mx-auto mb-12">
          <span className="section-label">Experiences</span>
          <h2 id="experiences-heading" className="section-title mt-2 mb-4">
            More Than Just a Stay
          </h2>
          <p className="section-subtitle">
            Jubilee Chalets is your gateway to a variety of experiences designed for relaxation, recreation, and making memories.
          </p>
        </SectionReveal>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {experienceItems.map((item, i) => (
            <SectionReveal key={item.title} delay={i * 0.08}>
              <article className="card group overflow-hidden">
                <div className="relative overflow-hidden aspect-video">
                  <img
                    src={item.image}
                    alt={item.title}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    loading="lazy"
                  />
                  <div className="absolute inset-0 bg-brand-forest-green/40 group-hover:bg-brand-forest-green/20 transition-colors" />
                  <div className="absolute bottom-4 left-4">
                    <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center text-white">
                      <item.icon className="w-5 h-5" />
                    </div>
                  </div>
                </div>
                <div className="p-5">
                  <h3 className="font-display font-bold text-base text-brand-black mb-2">{item.title}</h3>
                  <p className="text-gray-600 text-sm leading-relaxed">{item.desc}</p>
                </div>
              </article>
            </SectionReveal>
          ))}
        </div>

        <div className="text-center mt-12">
          <Link to="/experiences" className="btn-secondary text-base px-8 py-4">
            Explore All Experiences
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </div>
    </section>
  )
}

// ─── Why Us ───────────────────────────────────────────────────────────────────
const whyUs = [
  { title: 'Comfortable Chalets', desc: 'Well-appointed rooms and chalets with modern amenities for a comfortable stay.' },
  { title: 'Natural Setting', desc: 'Set amidst the natural beauty of Epe, offering a peaceful escape from city life.' },
  { title: 'Warm Hospitality', desc: 'Our team is dedicated to ensuring your stay is comfortable and memorable.' },
  { title: 'Versatile Venue', desc: 'From family vacations to corporate retreats, we cater to all your needs.' },
  { title: 'Easy Booking', desc: 'Our simple online booking system makes reserving your stay quick and convenient.' },
  { title: 'Prime Location', desc: 'Conveniently located in Epe, Lagos State, easily accessible from Lagos Island.' },
]

function WhyUs() {
  return (
    <section className="section-padding bg-brand-forest-green text-white" aria-labelledby="whyus-heading">
      <div className="container-xl">
        <SectionReveal className="text-center max-w-2xl mx-auto mb-12">
          <span className="text-green-300 text-sm font-semibold uppercase tracking-widest">Why Choose Us</span>
          <h2 id="whyus-heading" className="font-display text-3xl sm:text-4xl font-bold mt-2 mb-4">
            The Jubilee Chalets Experience
          </h2>
          <p className="text-white/75 text-lg leading-relaxed">
            We're committed to providing an exceptional hospitality experience that keeps our guests coming back.
          </p>
        </SectionReveal>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {whyUs.map((item, i) => (
            <SectionReveal key={item.title} delay={i * 0.08}>
              <div className="bg-white/10 hover:bg-white/15 transition-colors rounded-2xl p-6 border border-white/10">
                <div className="w-10 h-10 rounded-xl bg-green-300/20 flex items-center justify-center mb-4">
                  <CheckCircle className="w-5 h-5 text-green-300" />
                </div>
                <h3 className="font-display font-bold text-base mb-2">{item.title}</h3>
                <p className="text-white/70 text-sm leading-relaxed">{item.desc}</p>
              </div>
            </SectionReveal>
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── Testimonials ────────────────────────────────────────────────────────────
function Testimonials() {
  const { data: testimonials } = useQuery({
    queryKey: ['testimonials'],
    queryFn: contentApi.getTestimonials,
  })

  if (!testimonials?.length) return null

  return (
    <section className="section-padding bg-brand-light-grey" aria-labelledby="testimonials-heading">
      <div className="container-xl">
        <SectionReveal className="text-center max-w-2xl mx-auto mb-12">
          <span className="section-label">Guest Reviews</span>
          <h2 id="testimonials-heading" className="section-title mt-2 mb-4">
            What Our Guests Say
          </h2>
        </SectionReveal>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <SectionReveal key={t.id} delay={i * 0.08}>
              <article className="card p-6">
                <div className="flex items-center gap-1 mb-4">
                  {Array.from({ length: 5 }).map((_, j) => (
                    <Star
                      key={j}
                      className={`w-4 h-4 ${j < t.rating ? 'text-amber-400 fill-amber-400' : 'text-gray-200'}`}
                    />
                  ))}
                </div>
                <p className="text-gray-700 text-sm leading-relaxed mb-4 italic">"{t.review_text}"</p>
                <div className="flex items-center gap-3 pt-3 border-t border-gray-100">
                  <div className="w-9 h-9 rounded-full bg-brand-light-green flex items-center justify-center font-bold text-brand-dark-green text-sm">
                    {t.guest_name[0].toUpperCase()}
                  </div>
                  <div>
                    <div className="font-semibold text-sm text-brand-black">{t.guest_name}</div>
                    {t.visit_date && (
                      <div className="text-xs text-gray-500">{new Date(t.visit_date).toLocaleDateString('en-NG', { month: 'long', year: 'numeric' })}</div>
                    )}
                  </div>
                </div>
              </article>
            </SectionReveal>
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── Location ────────────────────────────────────────────────────────────────
function Location() {
  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: contentApi.getSettings,
    staleTime: 10 * 60 * 1000,
  })

  return (
    <section className="section-padding bg-white" aria-labelledby="location-heading">
      <div className="container-xl">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          <SectionReveal>
            <span className="section-label">Our Location</span>
            <h2 id="location-heading" className="section-title mt-2 mb-5">
              Find Us in the Heart of Epe
            </h2>
            <p className="section-subtitle mb-8">
              Jubilee Chalets is situated in the scenic town of Epe, Lagos State, offering easy access from Lagos while providing the tranquillity of a nature retreat.
            </p>

            <div className="space-y-4 mb-8">
              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-brand-dark-green mt-0.5 shrink-0" />
                <div>
                  <div className="font-semibold text-sm text-brand-black mb-0.5">Address</div>
                  <div className="text-gray-600 text-sm">{settings?.address ?? 'Epe, Lagos State, Nigeria'}</div>
                </div>
              </div>
              {settings?.phone_primary && (
                <div className="flex items-center gap-3">
                  <Phone className="w-5 h-5 text-brand-dark-green shrink-0" />
                  <a href={`tel:${settings.phone_primary}`} className="text-gray-600 text-sm hover:text-brand-dark-green transition-colors">
                    {settings.phone_primary}
                  </a>
                </div>
              )}
              {settings?.email_primary && (
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-brand-dark-green shrink-0" />
                  <a href={`mailto:${settings.email_primary}`} className="text-gray-600 text-sm hover:text-brand-dark-green transition-colors">
                    {settings.email_primary}
                  </a>
                </div>
              )}
            </div>

            <div className="flex flex-wrap gap-3">
              <a
                href={`https://maps.google.com/?q=Jubilee+Chalets+Epe+Lagos`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary"
              >
                <MapPin className="w-4 h-4" />
                Get Directions
              </a>
              {settings?.whatsapp_number && (
                <a
                  href={whatsAppLink(settings.whatsapp_number, 'Hello! I would like to enquire about Jubilee Chalets.')}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-secondary"
                >
                  <MessageCircle className="w-4 h-4" />
                  WhatsApp Us
                </a>
              )}
            </div>
          </SectionReveal>

          <SectionReveal delay={0.15}>
            <div className="rounded-2xl overflow-hidden shadow-lg border border-gray-100 aspect-[4/3]">
              {settings?.google_maps_embed_url ? (
                <iframe
                  src={settings.google_maps_embed_url}
                  width="100%"
                  height="100%"
                  style={{ border: 0 }}
                  allowFullScreen
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                  title="Jubilee Chalets location on Google Maps"
                />
              ) : (
                <div className="w-full h-full bg-brand-light-green flex items-center justify-center">
                  <div className="text-center">
                    <MapPin className="w-12 h-12 text-brand-dark-green mx-auto mb-3" />
                    <p className="text-brand-dark-green font-medium">Epe, Lagos State</p>
                    <p className="text-gray-500 text-sm mt-1">Map will be available soon</p>
                  </div>
                </div>
              )}
            </div>
          </SectionReveal>
        </div>
      </div>
    </section>
  )
}

// ─── Newsletter ───────────────────────────────────────────────────────────────
function Newsletter() {
  return (
    <section className="py-16 bg-brand-light-green" aria-labelledby="newsletter-heading">
      <div className="container-xl px-4 sm:px-6 lg:px-8">
        <SectionReveal className="max-w-xl mx-auto text-center">
          <h2 id="newsletter-heading" className="section-title mb-3">
            Stay in the Loop
          </h2>
          <p className="text-gray-600 mb-6">
            Subscribe to our newsletter for updates on special offers, events, and news from Jubilee Chalets.
          </p>
          <form
            className="flex flex-col sm:flex-row gap-3"
            onSubmit={(e) => { e.preventDefault(); }}
            aria-label="Newsletter subscription"
          >
            <input
              type="email"
              placeholder="Enter your email address"
              required
              className="flex-1 input-field"
              aria-label="Email address"
            />
            <button type="submit" className="btn-primary shrink-0">
              Subscribe
            </button>
          </form>
          <p className="text-xs text-gray-500 mt-3">
            We respect your privacy. Unsubscribe at any time.
          </p>
        </SectionReveal>
      </div>
    </section>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────
export default function HomePage() {
  return (
    <>
      <Hero />
      <Welcome />
      <RoomsPreview />
      <Experiences />
      <WhyUs />
      <Testimonials />
      <Location />
      <Newsletter />
    </>
  )
}
