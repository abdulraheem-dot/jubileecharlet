import React from 'react'
import { cn } from '@/utils'
import { ChevronDown } from 'lucide-react'

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  options: { value: string | number; label: string }[]
  placeholder?: string
}

// forwardRef so react-hook-form's register({ ref }) reaches the real <select>.
const Select = React.forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { label, error, options, placeholder, className, id, ...props },
  ref,
) {
  const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined)
  return (
    <div className="w-full">
      {label && (
        <label htmlFor={selectId} className="block text-sm font-medium text-brand-black mb-1.5">
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <div className="relative">
        <select
          ref={ref}
          id={selectId}
          className={cn(
            'input-field appearance-none pr-10',
            error && 'input-error',
            className,
          )}
          aria-invalid={!!error}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-gray-400">
          <ChevronDown className="w-4 h-4" />
        </div>
      </div>
      {error && (
        <p className="mt-1.5 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  )
})

export default Select
