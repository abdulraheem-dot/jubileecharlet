import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Users, CheckCircle } from 'lucide-react'
import { contentApi } from '@/services/api/content'
import { getImageUrl } from '@/utils'
import Input from '@/components/ui/Input'
import Textarea from '@/components/ui/Textarea'
import Button from '@/components/ui/Button'
import SectionReveal from '@/components/common/SectionReveal'

const schema = z.object({
  full_name: z.string().min(2, 'Name is required'),
  email: z.string().email('Valid email required'),
  phone_number: z.string().min(7, 'Phone number is required'),
  event_type: z.string().min(2, 'Event type is required'),
  event_date: z.string().min(1, 'Preferred date is required'),
  expected_attendees: z.number({ coerce: true }).min(1, 'At least 1 attendee required'),
  message: z.string().min(10, 'Please provide some details about your event'),
  catering_required: z.boolean(),
})
type FormData = z.infer<typeof schema>

export default function EventsPage() {
  const [submitted, setSubmitted] = useState(false)
  const { data: venues } = useQuery({ queryKey: ['event-venues'], queryFn: contentApi.getEventVenues })

  const { register, handleSubmit, formState: { errors }, reset } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { catering_required: false },
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) => contentApi.submitEventEnquiry({ ...data }),
    onSuccess: () => { setSubmitted(true); reset() },
    onError: () => toast.error('Failed to submit enquiry. Please try again.'),
  })

  return (
    <div className="pt-18 min-h-screen bg-white">
      {/* Hero */}
      <section className="bg-brand-forest-green text-white py-20 px-4 sm:px-6 lg:px-8">
        <div className="container-xl text-center">
          <span className="text-green-300 text-sm font-semibold uppercase tracking-widest block mb-3">Events & Conferences</span>
          <h1 className="font-display text-4xl sm:text-5xl font-bold mb-4">Host Your Event Here</h1>
          <p className="text-white/75 text-lg max-w-2xl mx-auto">
            From intimate gatherings to corporate conferences, Jubilee Chalets provides the perfect setting for your event.
          </p>
        </div>
      </section>

      {/* Venue cards */}
      {venues && venues.length > 0 && (
        <section className="section-padding bg-brand-light-grey">
          <div className="container-xl">
            <SectionReveal className="text-center mb-10">
              <span className="section-label">Our Venues</span>
              <h2 className="section-title mt-2">Event Spaces</h2>
            </SectionReveal>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {venues.map((venue, i) => (
                <SectionReveal key={venue.id} delay={i * 0.08}>
                  <article className="card overflow-hidden">
                    <div className="aspect-video overflow-hidden">
                      <img
                        src={getImageUrl(venue.images?.[0] ?? null)}
                        alt={venue.name}
                        className="w-full h-full object-cover"
                        loading="lazy"
                        onError={(e) => { (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=600&q=60' }}
                      />
                    </div>
                    <div className="p-5">
                      <h3 className="font-display font-bold text-lg mb-2">{venue.name}</h3>
                      <p className="text-gray-600 text-sm leading-relaxed mb-3">{venue.description}</p>
                      {venue.capacity && (
                        <div className="flex items-center gap-1.5 text-sm text-brand-dark-green">
                          <Users className="w-4 h-4" />
                          Up to {venue.capacity} attendees
                        </div>
                      )}
                    </div>
                  </article>
                </SectionReveal>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Enquiry form */}
      <section className="section-padding">
        <div className="container-xl">
          <div className="max-w-2xl mx-auto">
            <SectionReveal>
              <h2 className="section-title mb-2">Submit an Enquiry</h2>
              <p className="text-gray-600 mb-8">
                Tell us about your event and our team will get back to you with availability and a tailored quote.
              </p>

              {submitted ? (
                <div className="bg-brand-light-green rounded-2xl p-8 text-center">
                  <CheckCircle className="w-12 h-12 text-brand-dark-green mx-auto mb-3" />
                  <h3 className="font-display font-bold text-xl text-brand-black mb-2">Enquiry Received!</h3>
                  <p className="text-gray-600 mb-5">
                    Thank you for your interest. Our events team will contact you shortly to discuss your requirements.
                  </p>
                  <Button onClick={() => setSubmitted(false)} variant="secondary">Submit Another Enquiry</Button>
                </div>
              ) : (
                <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-5" noValidate>
                  <div className="grid sm:grid-cols-2 gap-4">
                    <Input label="Full name" required error={errors.full_name?.message} {...register('full_name')} />
                    <Input label="Email address" type="email" required error={errors.email?.message} {...register('email')} />
                  </div>
                  <div className="grid sm:grid-cols-2 gap-4">
                    <Input label="Phone number" required error={errors.phone_number?.message} {...register('phone_number')} />
                    <Input label="Event type" placeholder="Conference, wedding, retreat…" required error={errors.event_type?.message} {...register('event_type')} />
                  </div>
                  <div className="grid sm:grid-cols-2 gap-4">
                    <Input label="Preferred date" type="date" required error={errors.event_date?.message} {...register('event_date')} />
                    <Input label="Expected attendees" type="number" min={1} required error={errors.expected_attendees?.message} {...register('expected_attendees')} />
                  </div>
                  <Textarea label="Event details & requirements" rows={4} required error={errors.message?.message} placeholder="Please describe your event, any special requirements, equipment needed, etc." {...register('message')} />
                  <div className="flex items-center gap-3">
                    <input type="checkbox" id="catering" className="w-4 h-4 accent-brand-dark-green" {...register('catering_required')} />
                    <label htmlFor="catering" className="text-sm text-gray-700">Catering required</label>
                  </div>
                  <Button type="submit" isLoading={mutation.isPending} fullWidth size="lg">
                    Submit Enquiry
                  </Button>
                  <p className="text-xs text-gray-500 text-center">
                    Submitting this form does not confirm a booking. Our team will contact you to confirm availability.
                  </p>
                </form>
              )}
            </SectionReveal>
          </div>
        </div>
      </section>
    </div>
  )
}
