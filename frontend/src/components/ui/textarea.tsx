import { forwardRef, type TextareaHTMLAttributes } from 'react'
import { cn } from '@lib/utils'

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { className, ...props },
  ref,
) {
  return <textarea ref={ref} className={cn('glass-input min-h-[120px] w-full rounded-2xl px-4 py-3 text-sm outline-none', className)} {...props} />
})

Textarea.displayName = 'Textarea'