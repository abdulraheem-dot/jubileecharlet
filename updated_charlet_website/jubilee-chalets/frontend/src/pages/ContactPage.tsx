import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Phone, Mail, MapPin, MessageCircle, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react'
import { contentApi } from '@/services/api/content'
import { whatsAppLink } from '@/utils'
import Input from '@/components/ui/Input'
import Textarea from '@/components/ui/Textarea'
import Button from '@/components/ui/Button'
import SectionReveal from '@/components/common/SectionReveal'

const schema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email'),
  phone_number: z.string().optional(),
  subject: z.string().min(3, 'Subject is required'),
  message: z.string().min(10, 'Message must be at least 10 characters'),
})
type FormData = z.infer<typeof schema>

function FAQAccordion() {
  const { data: faqs } = useQuery({ queryKey: ['faqs'], queryFn: () => contentApi.getFAQs() })
  const [open, setOpen] = useState<number | null>(null)

  if (!faqs?.length) return null

  return (
    <div className="mt-12">
      <h2 className="font-display text-2xl font-bold text-brand-black mb-6">Frequently Asked Questions</h2>
      <div className="space-y-2">
        {faqs.map((faq) => (
          <div key={faq.id} className="bg-white border border-gray-100 rounded-xl overflow-hidden">
            <button
              onClick={() => setOpen(open === faq.id ? null : faq.id)}
              className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 transition-colors"
              aria-expanded={open === faq.id}
            >
              <span className="font-medium text-brand-black text-sm">{faq.question}</span>
              {open === faq.id ? <ChevronUp className="w-4 h-4 text-brand-dark-green shrink-0 ml-2" /> : <ChevronDown className="w-4 h-4 text-gray-400 shrink-0 ml-2" />}
            </button>
            {open === faq.id && (
              <div className="px-5 pb-4 text-sm text-gray-600 leading-relaxed border-t border-gray-100">
                {faq.answer}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false)
  const { data: settings } = useQuery({ queryKey: ['settings'], queryFn: contentApi.getSettings, staleTime: 10 * 60 * 1000 })

  const { register, handleSubmit, formState: { errors }, reset } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) => contentApi.submitContactForm(data),
    onSuccess: () => { setSubmitted(true); reset() },
    onError: () => toast.error('Failed to send message. Please try again.'),
  })

  return (
    <div className="pt-18 min-h-screen bg-white">
      {/* Hero */}
      <section className="bg-brand-forest-green text-white py-20 px-4 sm:px-6 lg:px-8">
        <div className="container-xl text-center">
          <span className="text-green-300 text-sm font-semibold uppercase tracking-widest block mb-3">Contact</span>
          <h1 className="font-display text-4xl sm:text-5xl font-bold mb-4">Get in Touch</h1>
          <p className="text-white/75 text-lg max-w-xl mx-auto">
            Have a question or ready to plan your visit? Our team is happy to help.
          </p>
        </div>
      </section>

      <section className="section-padding">
        <div className="container-xl">
          <div className="grid lg:grid-cols-2 gap-16">
            {/* Contact info */}
            <SectionReveal>
              <h2 className="font-display text-2xl font-bold text-brand-black mb-6">Contact Information</h2>
              <div className="space-y-5 mb-8">
                {settings?.phone_primary && (
                  <a href={`tel:${settings.phone_primary}`} className="flex items-center gap-4 p-4 bg-brand-light-grey rounded-xl hover:bg-brand-light-green transition-colors group">
                    <div className="w-10 h-10 bg-brand-dark-green rounded-xl flex items-center justify-center text-white shrink-0">
                      <Phone className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 mb-0.5">Phone</div>
                      <div className="font-medium text-brand-black group-hover:text-brand-dark-green transition-colors">{settings.phone_primary}</div>
                    </div>
                  </a>
                )}
                {settings?.email_primary && (
                  <a href={`mailto:${settings.email_primary}`} className="flex items-center gap-4 p-4 bg-brand-light-grey rounded-xl hover:bg-brand-light-green transition-colors group">
                    <div className="w-10 h-10 bg-brand-dark-green rounded-xl flex items-center justify-center text-white shrink-0">
                      <Mail className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 mb-0.5">Email</div>
                      <div className="font-medium text-brand-black group-hover:text-brand-dark-green transition-colors">{settings.email_primary}</div>
                    </div>
                  </a>
                )}
                <div className="flex items-center gap-4 p-4 bg-brand-light-grey rounded-xl">
                  <div className="w-10 h-10 bg-brand-dark-green rounded-xl flex items-center justify-center text-white shrink-0">
                    <MapPin className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-xs text-gray-500 mb-0.5">Address</div>
                    <div className="font-medium text-brand-black">{settings?.address ?? 'Epe, Lagos State, Nigeria'}</div>
                  </div>
                </div>
                {settings?.whatsapp_number && (
                  <a
                    href={whatsAppLink(settings.whatsapp_number, 'Hello, I would like to enquire about Jubilee Chalets.')}
                    target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-4 p-4 bg-green-50 rounded-xl hover:bg-green-100 transition-colors border border-green-200 group"
                  >
                    <div className="w-10 h-10 bg-green-600 rounded-xl flex items-center justify-center text-white shrink-0">
                      <MessageCircle className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="text-xs text-green-600 mb-0.5">WhatsApp</div>
                      <div className="font-medium text-brand-black">Chat with us on WhatsApp</div>
                    </div>
                  </a>
                )}
              </div>

              {/* Map */}
              <div className="rounded-2xl overflow-hidden aspect-video border border-gray-100">
                {settings?.google_maps_embed_url ? (
                  <iframe src={settings.google_maps_embed_url} width="100%" height="100%" style={{ border: 0 }} allowFullScreen loading="lazy" referrerPolicy="no-referrer-when-downgrade" title="Location" />
                ) : (
                  <div className="w-full h-full bg-brand-light-green flex items-center justify-center">
                    <div className="text-center">
                      <MapPin className="w-10 h-10 text-brand-dark-green mx-auto mb-2" />
                      <p className="text-brand-dark-green font-medium text-sm">Epe, Lagos State</p>
                    </div>
                  </div>
                )}
              </div>

              <FAQAccordion />
            </SectionReveal>

            {/* Contact form */}
            <SectionReveal delay={0.15}>
              <h2 className="font-display text-2xl font-bold text-brand-black mb-6">Send a Message</h2>

              {submitted ? (
                <div className="bg-brand-light-green rounded-2xl p-8 text-center">
                  <CheckCircle className="w-12 h-12 text-brand-dark-green mx-auto mb-3" />
                  <h3 className="font-display font-bold text-xl text-brand-black mb-2">Message Sent!</h3>
                  <p className="text-gray-600 mb-5">Thank you for reaching out. Our team will respond within 24 hours.</p>
                  <Button variant="secondary" onClick={() => setSubmitted(false)}>Send Another Message</Button>
                </div>
              ) : (
                <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-5" noValidate>
                  <div className="grid sm:grid-cols-2 gap-4">
                    <Input label="Full name" required error={errors.full_name?.message} {...register('full_name')} />
                    <Input label="Email address" type="email" required error={errors.email?.message} {...register('email')} />
                  </div>
                  <Input label="Phone number (optional)" type="tel" error={errors.phone_number?.message} {...register('phone_number')} />
                  <Input label="Subject" required error={errors.subject?.message} {...register('subject')} />
                  <Textarea label="Message" rows={5} required error={errors.message?.message} placeholder="Tell us how we can help…" {...register('message')} />
                  <Button type="submit" isLoading={mutation.isPending} fullWidth size="lg">
                    Send Message
                  </Button>
                </form>
              )}
            </SectionReveal>
          </div>
        </div>
      </section>
    </div>
  )
}
