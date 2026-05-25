import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, Clock3, Timer } from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { api } from '@/services/api'
 
interface AgeingSnapshot {
  generated_at: string
  summary: {
    active_defects: number
    stale_defects: number
    critical_stale: number
    high_risk_queue: number
  }
  aging_buckets: {
    bucket: string
    count: number
  }[]
  oldest_active_defects: {
    id: string
    number: string
    title: string
    priority: string
    status: string
    assigned_to: string
    is_sla_breached: boolean
    age_days: number
  }[]
}

async function fetchDefectsForAging() {
  const response = await api.get<AgeingSnapshot>('/ageing-defects/snapshot')
  return response.data
}

export function AgeingDefectsPage() {
  const query = useQuery({
    queryKey: ['ageing-defects', 'snapshot'],
    queryFn: fetchDefectsForAging,
    refetchInterval: 30000,
  })

  const activeDefects = useMemo(() => {
    if (!query.data?.oldest_active_defects) {
      return []
    }

    return query.data.oldest_active_defects
  }, [query.data?.oldest_active_defects])

  const buckets = useMemo(() => {
    const groups: Record<string, number> = {}
    query.data?.aging_buckets.forEach((item) => {
      groups[item.bucket] = item.count
    })
    return groups
  }, [query.data?.aging_buckets])

  const staleCount = query.data?.summary.stale_defects ?? 0
  const criticalStale = query.data?.summary.critical_stale ?? 0
  const highRiskCount = query.data?.summary.high_risk_queue ?? 0

  const topAged = activeDefects.slice(0, 12)

  if (query.isPending) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="h-28 animate-pulse rounded-3xl border border-white/10 bg-white/5" />
        ))}
      </div>
    )
  }

  if (query.isError) {
    return (
      <Card className="border-white/10 bg-slate-950/70">
        <CardContent className="py-12 text-center text-slate-300">Failed to load ageing defects snapshot.</CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-2">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-300">Ageing Defects Intelligence</p>
        <h1 className="text-3xl font-semibold text-white">Stale Backlog and Escalation Risk</h1>
        <p className="text-sm text-slate-200">Track aging backlog by bucket and prioritize old, high-impact defects before they escalate.</p>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card className="kpi-card from-cyan-500/35 via-cyan-500/20 to-slate-950/90">
          <CardContent className="flex items-start justify-between gap-3 p-5">
            <div>
              <p className="kpi-label">Active Defects</p>
              <p className="kpi-value text-2xl">{query.data?.summary.active_defects ?? 0}</p>
            </div>
            <div className="kpi-icon-shell">
              <Timer className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="kpi-card from-amber-500/35 via-amber-500/20 to-slate-950/90">
          <CardContent className="flex items-start justify-between gap-3 p-5">
            <div>
              <p className="kpi-label">Stale {'>'}14d</p>
              <p className="kpi-value text-2xl">{staleCount}</p>
            </div>
            <div className="kpi-icon-shell">
              <Clock3 className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="kpi-card from-rose-500/35 via-rose-500/20 to-slate-950/90">
          <CardContent className="flex items-start justify-between gap-3 p-5">
            <div>
              <p className="kpi-label">Critical Stale</p>
              <p className="kpi-value text-2xl">{criticalStale}</p>
            </div>
            <div className="kpi-icon-shell">
              <AlertTriangle className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="kpi-card from-violet-500/35 via-violet-500/20 to-slate-950/90">
          <CardContent className="flex items-start justify-between gap-3 p-5">
            <div>
              <p className="kpi-label">High Risk Queue</p>
              <p className="kpi-value text-2xl">{highRiskCount}</p>
            </div>
            <div className="kpi-icon-shell">
              <AlertTriangle className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_1.3fr]">
        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Aging Buckets</CardTitle>
            <CardDescription>Backlog distribution by defect age.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(buckets).map(([bucket, count]) => (
              <div key={bucket} className="grid grid-cols-[1fr_auto] items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm font-medium text-white">{bucket}</p>
                <span className="rounded-full bg-cyan-400/15 px-3 py-1 text-xs font-semibold text-cyan-100">{count}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Oldest Active Defects</CardTitle>
            <CardDescription>Prioritize intervention, reassignment, or escalation for these records.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {topAged.map((item) => (
              <div key={item.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-white">{item.number} - {item.title}</p>
                  <span className="rounded-full bg-amber-500/20 px-3 py-1 text-xs font-medium text-amber-200">{item.age_days}d old</span>
                </div>
                <p className="mt-2 text-xs text-slate-200">
                  {item.priority} | {item.status} | {item.assigned_to ?? 'Unassigned'}
                </p>
                <p className="mt-2 text-sm text-cyan-100">{item.is_sla_breached ? 'SLA breached — immediate action required.' : 'Monitor and schedule next action owner.'}</p>
              </div>
            ))}
            {topAged.length === 0 ? <p className="text-sm text-slate-300">No active defects available.</p> : null}
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
