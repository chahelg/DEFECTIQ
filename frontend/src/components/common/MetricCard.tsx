import { Card, CardContent } from '@components/ui/card'
import { cn } from '@lib/utils'
import { ArrowUpRight, LucideIcon } from 'lucide-react'

interface MetricCardProps {
  label: string
  value: string
  delta?: string
  icon: LucideIcon
  tone?: 'cyan' | 'emerald' | 'amber' | 'rose' | 'violet'
}

const toneMap = {
  cyan: 'from-cyan-500/20 to-cyan-400/5 text-cyan-300',
  emerald: 'from-emerald-500/20 to-emerald-400/5 text-emerald-300',
  amber: 'from-amber-500/20 to-amber-400/5 text-amber-300',
  rose: 'from-rose-500/20 to-rose-400/5 text-rose-300',
  violet: 'from-violet-500/20 to-violet-400/5 text-violet-300',
}

export function MetricCard({ label, value, delta, icon: Icon, tone = 'cyan' }: MetricCardProps) {
  return (
    <Card className="relative overflow-hidden">
      <div className={cn('absolute inset-0 bg-gradient-to-br opacity-90', toneMap[tone])} />
      <CardContent className="relative flex items-start justify-between gap-4 p-6">
        <div>
          <p className="text-sm text-muted-foreground">{label}</p>
          <h3 className="mt-2 text-3xl font-semibold tracking-tight text-foreground">{value}</h3>
          {delta ? <p className="mt-2 inline-flex items-center gap-1 text-sm text-emerald-300"><ArrowUpRight className="h-4 w-4" />{delta}</p> : null}
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/10 p-3 text-cyan-300 shadow-glow">
          <Icon className="h-6 w-6" />
        </div>
      </CardContent>
    </Card>
  )
}