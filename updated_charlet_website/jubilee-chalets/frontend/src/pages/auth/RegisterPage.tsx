import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Eye, EyeOff, Mail, Lock, User, Phone } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '@/features/authentication/AuthContext'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import { extractApiError } from '@/services/api/errors'

const schema = z.object({
  first_name: z.string().min(2, 'First name must be at least 2 characters'),
  last_name: z.string().min(2, 'Last name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email'),
  phone_number: z.string().optional(),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  password_confirm: z.string(),
}).refine((d) => d.password === d.password_confirm, {
  message: 'Passwords do not match',
  path: ['password_confirm'],
})

type FormData = z.infer<typeof schema>

export default function RegisterPage() {
  const { register: authRegister } = useAuth()
  const navigate = useNavigate()
  const [showPwd, setShowPwd] = useState(false)
  const [showPwdConf, setShowPwdConf] = useState(false)

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    try {
      await authRegister(data)
      toast.success('Account created! Welcome to Jubilee Chalets.')
      navigate('/dashboard')
    } catch (err) {
      toast.error(extractApiError(err, 'Registration failed. Please try again.'))
    }
  }

  return (
    <div>
      <h1 className="font-display text-3xl font-bold text-brand-black mb-2">Create account</h1>
      <p className="text-gray-600 mb-8">Join Jubilee Chalets for easy booking management</p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <div className="grid grid-cols-2 gap-3">
          <Input label="First name" leftIcon={<User className="w-4 h-4" />} error={errors.first_name?.message} required {...register('first_name')} />
          <Input label="Last name" leftIcon={<User className="w-4 h-4" />} error={errors.last_name?.message} required {...register('last_name')} />
        </div>

        <Input label="Email address" type="email" placeholder="you@example.com" autoComplete="email" leftIcon={<Mail className="w-4 h-4" />} error={errors.email?.message} required {...register('email')} />

        <Input label="Phone number (optional)" type="tel" placeholder="+234 800 000 0000" leftIcon={<Phone className="w-4 h-4" />} error={errors.phone_number?.message} {...register('phone_number')} />

        <Input
          label="Password"
          type={showPwd ? 'text' : 'password'}
          autoComplete="new-password"
          leftIcon={<Lock className="w-4 h-4" />}
          rightIcon={
            <button type="button" onClick={() => setShowPwd(!showPwd)} className="pointer-events-auto text-gray-400 hover:text-gray-600" aria-label={showPwd ? 'Hide' : 'Show'}>
              {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          }
          hint="Minimum 8 characters"
          error={errors.password?.message}
          required
          {...register('password')}
        />

        <Input
          label="Confirm password"
          type={showPwdConf ? 'text' : 'password'}
          autoComplete="new-password"
          leftIcon={<Lock className="w-4 h-4" />}
          rightIcon={
            <button type="button" onClick={() => setShowPwdConf(!showPwdConf)} className="pointer-events-auto text-gray-400 hover:text-gray-600" aria-label={showPwdConf ? 'Hide' : 'Show'}>
              {showPwdConf ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          }
          error={errors.password_confirm?.message}
          required
          {...register('password_confirm')}
        />

        <Button type="submit" isLoading={isSubmitting} fullWidth size="lg" className="mt-2">
          Create Account
        </Button>
      </form>

      <p className="text-center text-sm text-gray-600 mt-6">
        Already have an account?{' '}
        <Link to="/login" className="text-brand-dark-green font-semibold hover:underline">Sign in</Link>
      </p>
    </div>
  )
}
