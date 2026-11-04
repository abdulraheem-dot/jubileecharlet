import { useAuth } from '@/features/authentication/AuthContext'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import { authApi } from '@/services/api/auth'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'

const schema = z.object({
  first_name: z.string().min(2, 'Required'),
  last_name: z.string().min(2, 'Required'),
  phone_number: z.string().optional(),
})
type FormData = z.infer<typeof schema>

export default function ProfilePage() {
  const { user, refreshUser } = useAuth()

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      first_name: user?.first_name ?? '',
      last_name: user?.last_name ?? '',
      phone_number: user?.phone_number ?? '',
    },
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) => authApi.updateProfile(data),
    onSuccess: async () => {
      await refreshUser()
      toast.success('Profile updated')
    },
    onError: () => toast.error('Failed to update profile'),
  })

  return (
    <div>
      <h1 className="font-display text-2xl font-bold text-brand-black mb-6">My Profile</h1>
      <div className="bg-white rounded-2xl border border-gray-100 p-6 max-w-lg">
        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-5" noValidate>
          <div className="grid grid-cols-2 gap-4">
            <Input label="First name" required error={errors.first_name?.message} {...register('first_name')} />
            <Input label="Last name" required error={errors.last_name?.message} {...register('last_name')} />
          </div>
          <Input label="Email address" type="email" value={user?.email ?? ''} disabled hint="Email cannot be changed" />
          <Input label="Phone number" type="tel" error={errors.phone_number?.message} {...register('phone_number')} />
          <Button type="submit" isLoading={mutation.isPending}>Save Changes</Button>
        </form>
      </div>
    </div>
  )
}
