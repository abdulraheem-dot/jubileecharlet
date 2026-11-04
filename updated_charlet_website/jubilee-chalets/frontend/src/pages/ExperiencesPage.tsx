import { useQuery } from '@tanstack/react-query'
import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { contentApi } from '@/services/api/content'
import { getImageUrl } from '@/utils'
import SectionReveal from '@/components/common/SectionReveal'
import { Skeleton } from '@/components/ui/Skeleton'

export default function ExperiencesPage() {
  const { data: experiences, isLoading } = useQuery({
    queryKey: ['experiences'],
    queryFn: contentApi.getExperiences,
  })

  return (
    <div className="pt-18 min-h-screen bg-white">
      {/* Hero */}
      <section className="bg-brand-forest-green text-white py-20 px-4 sm:px-6 lg:px-8">
        <div className="container-xl text-center">
          <span className="text-green-300 text-sm font-semibold uppercase tracking-widest block mb-3">Experiences</span>
          <h1 className="font-display text-4xl sm:text-5xl font-bold mb-4">More Than Just a Stay</h1>
          <p className="text-white/75 text-lg max-w-2xl mx-auto">
            Discover the range of activities, amenities, and experiences waiting for you at Jubilee Chalets Epe.
          </p>
        </div>
      </section>

      {/* Experiences grid */}
      <section className="section-padding">
        <div className="container-xl">
          {isLoading ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="card">
                  <Skeleton className="aspect-video w-full" />
                  <div className="p-5 space-y-3">
                    <Skeleton className="h-5 w-2/3" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                  </div>
                </div>
              ))}
            </div>
          ) : !experiences?.length ? (
            <div className="text-center py-20">
              <p className="text-gray-500 mb-4">Experiences information will be available soon.</p>
              <Link to="/contact" className="btn-primary">Contact Us for More Info</Link>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {experiences.map((exp, i) => (
                <SectionReveal key={exp.id} delay={i * 0.07}>
                  <article className="card group overflow-hidden h-full flex flex-col">
                    <div className="relative overflow-hidden aspect-video">
                      <img
                        src={getImageUrl(exp.image)}
                        alt={exp.title}
                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                        loading="lazy"
                        onError={(e) => { (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=600&q=60' }}
                      />
                      <div className="absolute inset-0 bg-brand-forest-green/30 group-hover:bg-brand-forest-green/10 transition-colors" />
                      <div className="absolute top-3 left-3">
                        <span className="bg-white/90 text-brand-dark-green text-xs font-semibold px-3 py-1 rounded-full capitalize">
                          {exp.category}
                        </span>
                      </div>
                    </div>
                    <div className="flex flex-col flex-1 p-5">
                      <h2 className="font-display font-bold text-lg text-brand-black mb-2">{exp.title}</h2>
                      <p className="text-gray-600 text-sm leading-relaxed flex-1">{exp.description}</p>
                      {exp.price && !exp.is_free && (
                        <p className="text-brand-dark-green font-semibold text-sm mt-3">
                          From ₦{parseFloat(exp.price).toLocaleString()}
                        </p>
                      )}
                      {exp.is_free && (
                        <p className="text-green-600 font-semibold text-sm mt-3">Complimentary</p>
                      )}
                      <Link to="/contact" className="btn-secondary text-sm mt-4 justify-center">
                        Enquire <ArrowRight className="w-4 h-4" />
                      </Link>
                    </div>
                  </article>
                </SectionReveal>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-brand-light-green py-16 px-4 sm:px-6 lg:px-8">
        <div className="container-xl text-center">
          <h2 className="font-display text-3xl font-bold text-brand-black mb-3">
            Ready for Your Experience?
          </h2>
          <p className="text-gray-600 mb-8 max-w-xl mx-auto">
            Book your stay at Jubilee Chalets and enjoy all the experiences our resort has to offer.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link to="/accommodation" className="btn-primary">Book Your Stay</Link>
            <Link to="/events" className="btn-secondary">Plan an Event</Link>
          </div>
        </div>
      </section>
    </div>
  )
}
