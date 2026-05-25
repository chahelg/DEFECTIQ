import { forwardRef, type SelectHTMLAttributes } from 'react'
import { cn } from '@lib/utils'

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select({ className, ...props }, ref) {
  return (
    <select
      ref={ref}
      className={cn('glass-input h-11 w-full rounded-2xl px-4 text-sm outline-none', className)}
      {...props}
    />
  )
})

Select.displayName = 'Select'