import React from 'react'
import { cn } from '@/utils'
import { Loader2 } from 'lucide-react'

type Variant = 'primary' | 'secondary' | 'white' | 'outline-white' | 'ghost' | 'danger'
type Size = 'sm' | 'md' | 'lg' | 'xl'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  isLoading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  fullWidth?: boolean
}

const variantClasses: Record<Variant, string> = {
  primary: 'btn-primary',
  secondary: 'btn-secondary',
  white: 'btn-white',
  'outline-white': 'btn-outline-white',
  ghost: 'inline-flex items-center justify-center gap-2 px-4 py-2 text-brand-dark-green font-medium text-sm rounded-lg transition-all duration-200 hover:bg-brand-light-green',
  danger: 'inline-flex items-center justify-center gap-2 px-6 py-3 bg-red-600 text-white font-semibold text-sm rounded-lg transition-all duration-200 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed',
}

const sizeClasses: Record<Size, string> = {
  sm: '!px-4 !py-2 !text-xs',
  md: '',
  lg: '!px-8 !py-4 !text-base',
  xl: '!px-10 !py-5 !text-lg',
}

export default function Button({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  children,
  className,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        variantClasses[variant],
        sizeClasses[size],
        fullWidth && 'w-full',
        className,
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        leftIcon
      )}
      {children}
      {!isLoading && rightIcon}
    </button>
  )
}
