import { Link } from 'react-router-dom'
import { Phone, Mail, MapPin, Facebook, Instagram, Twitter, MessageCircle } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { contentApi } from '@/services/api/content'
import { whatsAppLink } from '@/utils'

export default function Footer() {
  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: contentApi.getSettings,
    staleTime: 10 * 60 * 1000,
  })

  const phone = settings?.phone_primary ?? '+234 000 000 0000'
  const email = settings?.email_primary ?? 'info@jubileechalets.com'
  const address = settings?.address ?? 'Epe, Lagos State, Nigeria'
  const whatsapp = settings?.whatsapp_number

  return (
    <footer className="bg-brand-forest-green text-white">
      {/* Main footer */}
      <div className="container-xl px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
          {/* Brand column */}
          <div className="lg:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center font-display font-bold text-lg">
                JC
              </div>
              <div>
                <div className="font-display font-bold text-lg leading-tight">Jubilee Chalets</div>
                <div className="text-white/60 text-xs tracking-wider">EPE · LAGOS</div>
              </div>
            </div>
            <p className="text-white/70 text-sm leading-relaxed mb-6">
              A premium destination for relaxation, memorable stays, and exceptional hospitality in the heart of Epe, Lagos State.
            </p>
            <div className="flex items-center gap-3">
              {settings?.facebook_url && (
                <a href={settings.facebook_url} target="_blank" rel="noopener noreferrer"
                  className="w-9 h-9 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                  aria-label="Facebook">
                  <Facebook className="w-4 h-4" />
                </a>
              )}
              {settings?.instagram_url && (
                <a href={settings.instagram_url} target="_blank" rel="noopener noreferrer"
                  className="w-9 h-9 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                  aria-label="Instagram">
                  <Instagram className="w-4 h-4" />
                </a>
              )}
              {settings?.twitter_url && (
                <a href={settings.twitter_url} target="_blank" rel="noopener noreferrer"
                  className="w-9 h-9 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                  aria-label="Twitter / X">
                  <Twitter className="w-4 h-4" />
                </a>
              )}
              {whatsapp && (
                <a href={whatsAppLink(whatsapp, 'Hello, I would like to enquire about Jubilee Chalets.')}
                  target="_blank" rel="noopener noreferrer"
                  className="w-9 h-9 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                  aria-label="WhatsApp">
                  <MessageCircle className="w-4 h-4" />
                </a>
              )}
            </div>
          </div>

          {/* Quick links */}
          <div>
            <h3 className="font-display font-semibold text-base mb-5">Quick Links</h3>
            <ul className="space-y-3">
              {[
                { label: 'Home', to: '/' },
                { label: 'Accommodation', to: '/accommodation' },
                { label: 'Experiences', to: '/experiences' },
                { label: 'Dining', to: '/dining' },
                { label: 'Gallery', to: '/gallery' },
                { label: 'About Us', to: '/about' },
                { label: 'Contact', to: '/contact' },
              ].map((link) => (
                <li key={link.to}>
                  <Link to={link.to}
                    className="text-white/70 hover:text-white text-sm transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Accommodation */}
          <div>
            <h3 className="font-display font-semibold text-base mb-5">Accommodation</h3>
            <ul className="space-y-3">
              {[
                { label: 'All Rooms', to: '/accommodation' },
                { label: 'Book a Room', to: '/accommodation' },
                { label: 'Events & Conferences', to: '/events' },
                { label: 'Special Packages', to: '/accommodation' },
              ].map((link) => (
                <li key={link.label}>
                  <Link to={link.to}
                    className="text-white/70 hover:text-white text-sm transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
              <li>
                <Link to="/dashboard" className="text-white/70 hover:text-white text-sm transition-colors">
                  My Bookings
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-display font-semibold text-base mb-5">Contact Us</h3>
            <ul className="space-y-4">
              <li>
                <a href={`tel:${phone}`}
                  className="flex items-start gap-3 text-white/70 hover:text-white text-sm transition-colors">
                  <Phone className="w-4 h-4 mt-0.5 shrink-0" />
                  <span>{phone}</span>
                </a>
              </li>
              <li>
                <a href={`mailto:${email}`}
                  className="flex items-start gap-3 text-white/70 hover:text-white text-sm transition-colors">
                  <Mail className="w-4 h-4 mt-0.5 shrink-0" />
                  <span>{email}</span>
                </a>
              </li>
              <li>
                <div className="flex items-start gap-3 text-white/70 text-sm">
                  <MapPin className="w-4 h-4 mt-0.5 shrink-0" />
                  <span>{address}</span>
                </div>
              </li>
              {settings?.check_in_time && (
                <li className="text-white/60 text-xs pt-2">
                  <div>Check-in: {settings.check_in_time}</div>
                  <div>Check-out: {settings.check_out_time}</div>
                </li>
              )}
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-white/10">
        <div className="container-xl px-4 sm:px-6 lg:px-8 py-5">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
            <p className="text-white/50 text-xs">
              © {new Date().getFullYear()} Jubilee Chalets Epe. All rights reserved.
            </p>
            <div className="flex items-center gap-4 flex-wrap justify-center">
              <Link to="/privacy-policy" className="text-white/50 hover:text-white/80 text-xs transition-colors">
                Privacy Policy
              </Link>
              <Link to="/terms" className="text-white/50 hover:text-white/80 text-xs transition-colors">
                Terms & Conditions
              </Link>
              <Link to="/cancellation-policy" className="text-white/50 hover:text-white/80 text-xs transition-colors">
                Cancellation Policy
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
