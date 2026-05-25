import type { HTMLAttributes } from 'react'
import { cn } from '@lib/utils'

export function Badge({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return <span className={cn('inline-flex items-center rounded-full border border-slate-600/80 bg-slate-800/90 px-3 py-1 text-xs font-medium text-slate-100', className)} {...props} />
}