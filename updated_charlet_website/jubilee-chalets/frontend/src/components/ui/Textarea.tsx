import React from 'react'
import { cn } from '@/utils'

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  hint?: string
}

// forwardRef so react-hook-form's register({ ref }) reaches the real <textarea>.
const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { label, error, hint, className, id, ...props },
  ref,
) {
  const taId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined)
  return (
    <div className="w-full">
      {label && (
        <label htmlFor={taId} className="block text-sm font-medium text-brand-black mb-1.5">
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <textarea
        ref={ref}
        id={taId}
        className={cn('input-field min-h-[120px] resize-y', error && 'input-error', className)}
        aria-invalid={!!error}
        {...props}
      />
      {error && (
        <p className="mt-1.5 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
      {hint && !error && <p className="mt-1.5 text-sm text-gray-500">{hint}</p>}
    </div>
  )
})

export default Textarea
