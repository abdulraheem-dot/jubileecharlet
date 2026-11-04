import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Eye, EyeOff, Mail, Lock } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '@/features/authentication/AuthContext'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import { extractApiError } from '@/services/api/errors'

const schema = z.object({
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(1, 'Password is required'),
})
type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as any)?.from?.pathname ?? '/dashboard'
  const [showPassword, setShowPassword] = useState(false)

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    try {
      await login(data)
      toast.success('Welcome back!')
      navigate(from, { replace: true })
    } catch (err) {
      toast.error(extractApiError(err, 'Invalid email or password'))
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl font-bold text-brand-black mb-2">Welcome back</h1>
      <p className="text-gray-600 mb-8">Sign in to your Jubilee Chalets account</p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
        <Input
          label="Email address"
          type="email"
          placeholder="you@example.com"
          autoComplete="email"
          leftIcon={<Mail className="w-4 h-4" />}
          error={errors.email?.message}
          required
          {...register('email')}
        />

        <div>
          <Input
            label="Password"
            type={showPassword ? 'text' : 'password'}
            placeholder="••••••••"
            autoComplete="current-password"
            leftIcon={<Lock className="w-4 h-4" />}
            rightIcon={
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-gray-400 hover:text-gray-600 pointer-events-auto"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            }
            error={errors.password?.message}
            required
            {...register('password')}
          />
          <div className="flex justify-end mt-1.5">
            <Link to="/forgot-password" className="text-sm text-brand-dark-green hover:underline">
              Forgot password?
            </Link>
          </div>
        </div>

        <Button type="submit" isLoading={isSubmitting} fullWidth size="lg">
          Sign In
        </Button>
      </form>

      <p className="text-center text-sm text-gray-600 mt-6">
        Don't have an account?{' '}
        <Link to="/register" className="text-brand-dark-green font-semibold hover:underline">
          Create one
        </Link>
      </p>
    </div>
  )
}
