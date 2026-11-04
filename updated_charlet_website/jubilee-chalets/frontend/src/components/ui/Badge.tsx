import { cn } from '@/utils'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'green' | 'yellow' | 'red' | 'blue' | 'gray' | 'purple'
  className?: string
}

const variants = {
  green: 'bg-green-100 text-green-800',
  yellow: 'bg-yellow-100 text-yellow-800',
  red: 'bg-red-100 text-red-800',
  blue: 'bg-blue-100 text-blue-800',
  gray: 'bg-gray-100 text-gray-700',
  purple: 'bg-purple-100 text-purple-800',
}

export default function Badge({ children, variant = 'gray', className }: BadgeProps) {
  return (
    <span className={cn('badge', variants[variant], className)}>
      {children}
    </span>
  )
}
