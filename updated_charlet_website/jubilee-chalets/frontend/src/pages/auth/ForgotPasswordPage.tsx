import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Mail, CheckCircle } from 'lucide-react'
import { authApi } from '@/services/api/auth'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'

const schema = z.object({ email: z.string().email('Please enter a valid email') })
type FormData = z.infer<typeof schema>

export default function ForgotPasswordPage() {
  const [sent, setSent] = useState(false)
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async ({ email }: FormData) => {
    try {
      await authApi.requestPasswordReset(email)
      setSent(true)
    } catch {
      // Always show success to prevent email enumeration
      setSent(true)
    }
  }

  if (sent) {
    return (
      <div className="text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-brand-dark-green" />
        </div>
        <h1 className="font-display text-2xl font-bold text-brand-black mb-2">Check your email</h1>
        <p className="text-gray-600 mb-6">
          If an account with that email exists, we've sent password-reset instructions.
        </p>
        <Link to="/login" className="btn-primary inline-flex">Back to Sign In</Link>
      </div>
    )
  }

  return (
    <div>
      <h1 className="font-display text-3xl font-bold text-brand-black mb-2">Forgot password</h1>
      <p className="text-gray-600 mb-8">Enter your email and we'll send reset instructions.</p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
        <Input
          label="Email address"
          type="email"
          placeholder="you@example.com"
          leftIcon={<Mail className="w-4 h-4" />}
          error={errors.email?.message}
          required
          {...register('email')}
        />
        <Button type="submit" isLoading={isSubmitting} fullWidth size="lg">
          Send Reset Link
        </Button>
      </form>

      <p className="text-center text-sm text-gray-600 mt-6">
        Remember your password?{' '}
        <Link to="/login" className="text-brand-dark-green font-semibold hover:underline">Sign in</Link>
      </p>
    </div>
  )
}
