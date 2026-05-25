import { type InputHTMLAttributes } from 'react'
import { cn } from '@lib/utils'

export interface SwitchProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {}

export function Switch({ className, checked, ...props }: SwitchProps) {
  return (
    <label className={cn('relative inline-flex h-6 w-11 cursor-pointer items-center', className)}>
      <input type="checkbox" className="peer sr-only" checked={checked} {...props} />
      <span className="h-6 w-11 rounded-full bg-slate-600/60 transition peer-checked:bg-cyan-500/80" />
      <span className="absolute left-1 h-4 w-4 rounded-full bg-white transition peer-checked:translate-x-5" />
    </label>
  )
}