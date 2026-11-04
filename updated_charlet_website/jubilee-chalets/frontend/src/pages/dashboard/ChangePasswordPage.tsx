import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import { authApi } from '@/services/api/auth'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'

const schema = z.object({
  current_password: z.string().min(1, 'Current password required'),
  new_password: z.string().min(8, 'Minimum 8 characters'),
  new_password_confirm: z.string(),
}).refine(d => d.new_password === d.new_password_confirm, {
  message: 'Passwords do not match',
  path: ['new_password_confirm'],
})
type FormData = z.infer<typeof schema>

export default function ChangePasswordPage() {
  const [showCurrent, setShowCurrent] = useState(false)
  const [showNew, setShowNew] = useState(false)
  const { register, handleSubmit, formState: { errors }, reset } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const mutation = useMutation({
    mutationFn: (d: FormData) => authApi.changePassword(d.current_password, d.new_password, d.new_password_confirm),
    onSuccess: () => { toast.success('Password changed successfully'); reset() },
    onError: (err: any) => {
      const msg = err?.response?.data?.current_password ?? err?.response?.data?.detail ?? 'Failed to change password'
      toast.error(msg)
    },
  })

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-brand-black mb-6">Change Password</h1>
      <div className="bg-white rounded-2xl border border-gray-100 p-6 max-w-lg">
        <form onSubmit={handleSubmit(d => mutation.mutate(d))} className="space-y-5" noValidate>
          <Input
            label="Current password"
            type={showCurrent ? 'text' : 'password'}
            required
            error={errors.current_password?.message}
            rightIcon={<button type="button" onClick={() => setShowCurrent(!showCurrent)} className="pointer-events-auto text-gray-400">{showCurrent ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}</button>}
            {...register('current_password')}
          />
          <Input
            label="New password"
            type={showNew ? 'text' : 'password'}
            required
            hint="Minimum 8 characters"
            error={errors.new_password?.message}
            rightIcon={<button type="button" onClick={() => setShowNew(!showNew)} className="pointer-events-auto text-gray-400">{showNew ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}</button>}
            {...register('new_password')}
          />
          <Input
            label="Confirm new password"
            type="password"
            required
            error={errors.new_password_confirm?.message}
            {...register('new_password_confirm')}
          />
          <Button type="submit" isLoading={mutation.isPending}>Update Password</Button>
        </form>
      </div>
    </div>
  )
}
