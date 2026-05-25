import { useQuery } from '@tanstack/react-query'
import { ArrowRightLeft, Gauge, Layers, Scale, Users } from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/services/api'

interface WorkloadSnapshot {
  generated_at: string
  summary: {
    active_assignees: number
    open_defects: number
    overloaded_assignees: number
    underutilized_assignees: number
    workload_imbalance_score: number
    assignment_efficiency: number
  }
  assignee_workload: {
    assignee: string
    open_count: number
    critical_count: number
    high_count: number
    breached_count: number
    reopen_count: number
    workload_score: number
    capacity_index: number
    load_band: string
  }[]
  reassignment_candidates: {
    from_assignee: string
    to_assignee: string
    suggested_defect_moves: number
    reason: string
  }[]
  recommended_actions: string[]
}

async function fetchWorkloadSnapshot() {
  const response = await api.get<WorkloadSnapshot>('/workload-intelligence/snapshot')
  return response.data
}

export function WorkloadIntelligencePage() {
  const query = useQuery({
    queryKey: ['workload-intelligence', 'snapshot'],
    queryFn: fetchWorkloadSnapshot,
    refetchInterval: 30000,
  })

  if (query.isPending) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="h-28 animate-pulse rounded-3xl border border-white/10 bg-white/5" />
        ))}
      </div>
    )
  }

  if (query.isError || !query.data) {
    return (
      <Card className="border-white/10 bg-slate-950/70">
        <CardContent className="py-12 text-center text-slate-300">Failed to load workload intelligence snapshot.</CardContent>
      </Card>
    )
  }

  const { summary, assignee_workload, reassignment_candidates, recommended_actions } = query.data

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-2">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-300">Workload Intelligence</p>
        <h1 className="text-3xl font-semibold text-white">Capacity and Rebalancing Control Plane</h1>
        <p className="text-sm text-slate-300">Detect overload conditions and execute guided reassignment before SLA and quality degrade.</p>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <WorkloadMetric icon={Users} label="Active Assignees" value={String(summary.active_assignees)} tone="cyan" />
        <WorkloadMetric icon={Layers} label="Open Defects" value={String(summary.open_defects)} tone="amber" />
        <WorkloadMetric icon={Scale} label="Imbalance Score" value={`${summary.workload_imbalance_score.toFixed(1)}%`} tone="rose" />
        <WorkloadMetric icon={Gauge} label="Assignment Efficiency" value={`${summary.assignment_efficiency.toFixed(1)}%`} tone="violet" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Consultant Capacity Map</CardTitle>
            <CardDescription>Use load band and capacity index to balance assignment distribution.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {assignee_workload.map((row) => (
              <div key={row.assignee} className="grid gap-2 rounded-2xl border border-white/10 bg-white/5 p-4 md:grid-cols-[1.2fr_repeat(5,minmax(0,1fr))]">
                <p className="text-sm font-medium text-white">{row.assignee}</p>
                <p className="text-xs text-slate-300">Open {row.open_count}</p>
                <p className="text-xs text-slate-300">Critical {row.critical_count}</p>
                <p className="text-xs text-slate-300">Breached {row.breached_count}</p>
                <p className="text-xs text-slate-300">Load {row.workload_score.toFixed(1)}</p>
                <p className="text-xs text-cyan-100">Capacity {row.capacity_index.toFixed(1)}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Immediate Actions</CardTitle>
            <CardDescription>Operational interventions to stabilize workload and improve throughput.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {recommended_actions.map((action) => (
              <div key={action} className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-sm text-cyan-100">
                {action}
              </div>
            ))}
            <Button className="w-full">Open Workload Action Queue</Button>
          </CardContent>
        </Card>
      </section>

      <Card className="border-white/10 bg-slate-950/70">
        <CardHeader>
          <CardTitle>Reassignment Recommendations</CardTitle>
          <CardDescription>Suggested moves reduce concentrated risk and unblock overloaded owners.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {reassignment_candidates.length === 0 ? (
            <p className="text-sm text-slate-400">No immediate reassignment needed based on current distribution.</p>
          ) : (
            reassignment_candidates.map((candidate, index) => (
              <div key={`${candidate.from_assignee}-${candidate.to_assignee}-${index}`} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex flex-wrap items-center gap-2 text-sm text-white">
                  <span className="font-medium">{candidate.from_assignee}</span>
                  <ArrowRightLeft className="h-4 w-4 text-cyan-300" />
                  <span className="font-medium">{candidate.to_assignee}</span>
                </div>
                <p className="mt-2 text-xs text-slate-300">Suggested moves: {candidate.suggested_defect_moves}</p>
                <p className="mt-2 text-sm text-cyan-100">{candidate.reason}</p>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}

interface WorkloadMetricProps {
  icon: typeof Users
  label: string
  value: string
  tone: 'cyan' | 'amber' | 'rose' | 'violet'
}

function WorkloadMetric({ icon: Icon, label, value, tone }: WorkloadMetricProps) {
  const tones: Record<WorkloadMetricProps['tone'], string> = {
    cyan: 'from-cyan-500/35 via-cyan-500/20 to-slate-950/90',
    amber: 'from-amber-500/35 via-amber-500/20 to-slate-950/90',
    rose: 'from-rose-500/35 via-rose-500/20 to-slate-950/90',
    violet: 'from-violet-500/35 via-violet-500/20 to-slate-950/90',
  }

  return (
    <Card className={`kpi-card ${tones[tone]}`}>
      <CardContent className="flex items-start justify-between gap-3 p-5">
        <div>
          <p className="kpi-label">{label}</p>
          <p className="kpi-value text-2xl">{value}</p>
        </div>
        <div className="kpi-icon-shell">
          <Icon className="h-5 w-5" />
        </div>
      </CardContent>
    </Card>
  )
}
