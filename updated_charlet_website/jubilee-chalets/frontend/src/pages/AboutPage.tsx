import { Link } from 'react-router-dom'
import { MapPin, CheckCircle, ArrowRight } from 'lucide-react'
import SectionReveal from '@/components/common/SectionReveal'

export default function AboutPage() {
  return (
    <div className="pt-18 min-h-screen bg-white">
      {/* Hero */}
      <section className="bg-brand-forest-green text-white py-24 px-4 sm:px-6 lg:px-8">
        <div className="container-xl text-center">
          <span className="text-green-300 text-sm font-semibold uppercase tracking-widest block mb-3">About Us</span>
          <h1 className="font-display text-4xl sm:text-5xl font-bold mb-4">Our Story</h1>
          <p className="text-white/75 text-lg max-w-2xl mx-auto">
            Jubilee Chalets Epe — a premium resort destination committed to exceptional hospitality in Lagos State.
          </p>
        </div>
      </section>

      {/* Introduction */}
      <section className="section-padding">
        <div className="container-xl">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <SectionReveal>
              <img
                src="https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80"
                alt="Jubilee Chalets resort"
                className="w-full rounded-2xl object-cover aspect-[4/3]"
                loading="lazy"
              />
            </SectionReveal>
            <SectionReveal delay={0.15}>
              <span className="section-label">Who We Are</span>
              <h2 className="section-title mt-2 mb-5">A Sanctuary in Epe, Lagos</h2>
              <p className="text-gray-600 leading-relaxed mb-4">
                Jubilee Chalets is a premium resort and accommodation destination located in the historic town of Epe, Lagos State, Nigeria. We offer a unique blend of natural beauty, modern comfort, and warm Nigerian hospitality.
              </p>
              <p className="text-gray-600 leading-relaxed mb-6">
                Whether you're planning a romantic getaway, a family vacation, a corporate retreat, or a special event, our resort provides the perfect backdrop for an unforgettable experience.
              </p>
              <div className="space-y-3">
                {['Premium accommodation in well-appointed chalets', 'Refreshing swimming and recreational facilities', 'On-site restaurant with local and continental cuisine', 'Versatile event spaces for all occasions', 'Personalised, attentive hospitality service'].map((f) => (
                  <div key={f} className="flex items-start gap-2.5 text-gray-700 text-sm">
                    <CheckCircle className="w-4 h-4 text-brand-dark-green mt-0.5 shrink-0" />
                    {f}
                  </div>
                ))}
              </div>
            </SectionReveal>
          </div>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="section-padding bg-brand-light-grey">
        <div className="container-xl">
          <div className="grid sm:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <SectionReveal>
              <div className="bg-white rounded-2xl p-8 h-full">
                <div className="w-12 h-12 bg-brand-light-green rounded-xl flex items-center justify-center mb-4">
                  <CheckCircle className="w-6 h-6 text-brand-dark-green" />
                </div>
                <h3 className="font-display font-bold text-xl mb-3">Our Mission</h3>
                <p className="text-gray-600 leading-relaxed">
                  To provide an exceptional resort experience that combines the natural tranquillity of Epe with premium accommodation, outstanding service, and memorable experiences for every guest.
                </p>
              </div>
            </SectionReveal>
            <SectionReveal delay={0.1}>
              <div className="bg-brand-dark-green text-white rounded-2xl p-8 h-full">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4">
                  <CheckCircle className="w-6 h-6 text-green-300" />
                </div>
                <h3 className="font-display font-bold text-xl mb-3">Our Vision</h3>
                <p className="text-white/80 leading-relaxed">
                  To be the foremost resort destination in Epe, Lagos State, known for our hospitality, natural setting, and the quality of experiences we provide to guests from across Nigeria and beyond.
                </p>
              </div>
            </SectionReveal>
          </div>
        </div>
      </section>

      {/* Location */}
      <section className="section-padding bg-white">
        <div className="container-xl">
          <SectionReveal className="text-center max-w-xl mx-auto mb-10">
            <span className="section-label">Location</span>
            <h2 className="section-title mt-2 mb-4">Find Us in Epe</h2>
            <p className="text-gray-600">
              Located in the serene town of Epe, Lagos State, Jubilee Chalets is a convenient escape from the hustle and bustle of Lagos.
            </p>
          </SectionReveal>
          <SectionReveal>
            <div className="bg-brand-light-grey rounded-2xl p-6 max-w-lg mx-auto text-center">
              <MapPin className="w-8 h-8 text-brand-dark-green mx-auto mb-3" />
              <p className="font-medium text-brand-black mb-1">Jubilee Chalets</p>
              <p className="text-gray-600 text-sm mb-4">Epe, Lagos State, Nigeria</p>
              <a
                href="https://maps.google.com/?q=Jubilee+Chalets+Epe+Lagos"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary inline-flex"
              >
                <MapPin className="w-4 h-4" />
                Get Directions
              </a>
            </div>
          </SectionReveal>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-brand-dark-green text-white py-16 px-4 sm:px-6 lg:px-8">
        <div className="container-xl text-center">
          <h2 className="font-display text-3xl font-bold mb-3">Ready to Experience It?</h2>
          <p className="text-white/75 mb-8">Book your stay at Jubilee Chalets and discover everything we have to offer.</p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link to="/accommodation" className="btn-white">
              Book Your Stay <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/contact" className="btn-outline-white">Contact Us</Link>
          </div>
        </div>
      </section>
    </div>
  )
}
