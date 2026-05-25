import { forwardRef, type InputHTMLAttributes } from 'react'
import { cn } from '@lib/utils'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input({ className, ...props }, ref) {
  return <input ref={ref} className={cn('glass-input h-11 w-full rounded-2xl px-4 text-sm outline-none', className)} {...props} />
})

Input.displayName = 'Input'