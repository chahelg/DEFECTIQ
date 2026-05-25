import { useQuery } from '@tanstack/react-query'
import { Activity, ArrowDownUp, GitBranch, PauseCircle, Timer } from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/services/api'

interface WorkflowSnapshot {
  generated_at: string
  summary: {
    active_items: number
    inflow_7d: number
    throughput_7d: number
    flow_efficiency: number
    avg_cycle_time_days: number
    blocked_items: number
    stale_items: number
  }
  status_pipeline: {
    status: string
    count: number
    avg_age_days: number
    stale_ratio: number
    critical_ratio: number
    bottleneck_score: number
  }[]
  stale_work_items: {
    defect_number: string
    title: string
    status: string
    priority: string
    assignee: string
    age_days: number
    days_since_update: number
    intervention: string
  }[]
  recommended_actions: string[]
}

async function fetchWorkflowSnapshot() {
  const response = await api.get<WorkflowSnapshot>('/workflow-intelligence/snapshot')
  return response.data
}

export function WorkflowIntelligencePage() {
  const query = useQuery({
    queryKey: ['workflow-intelligence', 'snapshot'],
    queryFn: fetchWorkflowSnapshot,
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
        <CardContent className="py-12 text-center text-slate-300">Failed to load workflow intelligence snapshot.</CardContent>
      </Card>
    )
  }

  const { summary, status_pipeline, stale_work_items, recommended_actions } = query.data

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-2">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-300">Workflow Intelligence</p>
        <h1 className="text-3xl font-semibold text-white">Flow Stability and Bottleneck Control</h1>
        <p className="text-sm text-slate-200">Track pipeline friction, stale items, and blocked stages before throughput degrades.</p>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <WorkflowMetric icon={GitBranch} label="Active Flow Items" value={String(summary.active_items)} tone="cyan" />
        <WorkflowMetric icon={ArrowDownUp} label="Flow Efficiency" value={`${summary.flow_efficiency.toFixed(1)}%`} tone="violet" />
        <WorkflowMetric icon={Timer} label="Avg Cycle Time" value={`${summary.avg_cycle_time_days.toFixed(1)} days`} tone="amber" />
        <WorkflowMetric icon={PauseCircle} label="Blocked + Stale" value={`${summary.blocked_items + summary.stale_items}`} tone="rose" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Pipeline Stage Health</CardTitle>
            <CardDescription>Prioritize high bottleneck scores and high stale ratios first.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {status_pipeline.map((row) => (
              <div key={row.status} className="grid gap-2 rounded-2xl border border-white/10 bg-white/5 p-4 md:grid-cols-[1.1fr_repeat(4,minmax(0,1fr))]">
                <p className="text-sm font-medium text-white">{row.status}</p>
                <p className="text-xs text-slate-200">Items {row.count}</p>
                <p className="text-xs text-slate-200">Avg age {row.avg_age_days.toFixed(1)}d</p>
                <p className="text-xs text-slate-200">Stale {row.stale_ratio.toFixed(1)}%</p>
                <p className="text-xs text-amber-200">Bottleneck {row.bottleneck_score.toFixed(1)}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Manager Interventions</CardTitle>
            <CardDescription>Apply focused actions to unblock flow and increase weekly throughput.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {recommended_actions.map((action) => (
              <div key={action} className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-sm text-cyan-100">
                {action}
              </div>
            ))}
            <Button className="w-full">Open Workflow Action Queue</Button>
          </CardContent>
        </Card>
      </section>

      <Card className="border-white/10 bg-slate-950/70">
        <CardHeader>
          <CardTitle>Stale Work Items</CardTitle>
          <CardDescription>Items idle for 3+ days need explicit intervention or reassignment.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {stale_work_items.length === 0 ? (
            <p className="text-sm text-slate-300">No stale workflow items currently detected.</p>
          ) : (
            stale_work_items.slice(0, 12).map((item) => (
              <div key={item.defect_number} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-white">{item.defect_number} - {item.title}</p>
                  <span className="rounded-full bg-amber-500/20 px-3 py-1 text-xs font-medium text-amber-200">{item.days_since_update}d idle</span>
                </div>
                <p className="mt-2 text-xs text-slate-200">
                  {item.priority} | {item.status} | {item.assignee} | Age {item.age_days}d
                </p>
                <p className="mt-2 text-sm text-cyan-100">{item.intervention}</p>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}

interface WorkflowMetricProps {
  icon: typeof Activity
  label: string
  value: string
  tone: 'cyan' | 'amber' | 'rose' | 'violet'
}

function WorkflowMetric({ icon: Icon, label, value, tone }: WorkflowMetricProps) {
  const tones: Record<WorkflowMetricProps['tone'], string> = {
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
