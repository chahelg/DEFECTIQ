import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, ArrowRightLeft, Flame, ShieldAlert, Siren, TrendingUp } from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/services/api'

interface TeamLoad {
  assignee: string
  open_count: number
  critical_count: number
  breached_count: number
  workload_score: number
}

interface AttentionItem {
  defect_number: string
  title: string
  priority: string
  status: string
  assignee: string
  age_days: number
  risk_score: number
}

interface CommandCenterResponse {
  generated_at: string
  executive_kpis: {
    sla_breach_pct: number
    mttr_hours: number
    delivery_risk_score: number
    critical_backlog: number
    service_instability_index: number
    operational_risk_index: number
  }
  operational_kpis: {
    open_defects: number
    breached_open_defects: number
    workload_imbalance: number
    defect_inflow_velocity_7d: number
    workflow_bottleneck_score: number
    reopen_risk: number
  }
  attention_items: AttentionItem[]
  team_load: TeamLoad[]
  recommended_actions: string[]
}

async function fetchCommandCenter() {
  const response = await api.get<CommandCenterResponse>('/manager-decision/command-center')
  return response.data
}

export function ManagerCommandCenterPage() {
  const query = useQuery({
    queryKey: ['manager-decision', 'command-center'],
    queryFn: fetchCommandCenter,
    refetchInterval: 30000,
  })

  if (query.isPending) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="h-28 animate-pulse rounded-3xl border border-white/10 bg-white/5" />
          ))}
        </div>
      </div>
    )
  }

  if (query.isError || !query.data) {
    return (
      <Card className="border-white/10 bg-slate-950/70">
        <CardContent className="py-10 text-center text-slate-300">
          Failed to load manager command center snapshot.
        </CardContent>
      </Card>
    )
  }

  const { executive_kpis: executive, operational_kpis: operational, attention_items, team_load, recommended_actions } = query.data

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-2">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-300">Manager Decision Center</p>
        <h1 className="text-3xl font-semibold text-white">Today&apos;s Operational Priorities</h1>
        <p className="text-sm text-slate-300">
          Risk-first control surface for immediate management actions across SLA risk, capacity imbalance, and high-impact defects.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <MetricCard icon={Siren} label="Delivery Risk Score" value={`${executive.delivery_risk_score.toFixed(1)} / 100`} tone="rose" />
        <MetricCard icon={ShieldAlert} label="SLA Breach % (Open)" value={`${executive.sla_breach_pct.toFixed(1)}%`} tone="amber" />
        <MetricCard icon={Flame} label="Critical Backlog" value={String(executive.critical_backlog)} tone="rose" />
        <MetricCard icon={TrendingUp} label="MTTR" value={`${executive.mttr_hours.toFixed(1)} hrs`} tone="cyan" />
        <MetricCard icon={ArrowRightLeft} label="Workload Imbalance" value={`${operational.workload_imbalance.toFixed(1)}%`} tone="violet" />
        <MetricCard icon={AlertTriangle} label="Bottleneck Score" value={`${operational.workflow_bottleneck_score.toFixed(1)}%`} tone="amber" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Defects Requiring Attention</CardTitle>
            <CardDescription>Ranked by urgency, breach exposure, aging, and criticality.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {attention_items.length === 0 ? (
              <p className="text-sm text-slate-400">No high-risk defects at this time.</p>
            ) : (
              attention_items.map((item) => (
                <div key={item.defect_number} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-white">{item.defect_number} - {item.title}</p>
                    <span className="rounded-full bg-rose-500/20 px-3 py-1 text-xs font-medium text-rose-200">Risk {item.risk_score}</span>
                  </div>
                  <p className="mt-2 text-xs text-slate-300">
                    {item.priority} | {item.status} | {item.assignee} | Aging {item.age_days}d
                  </p>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Recommended Actions</CardTitle>
            <CardDescription>Immediate interventions to reduce delivery and SLA risk.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {recommended_actions.map((action) => (
              <div key={action} className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-sm text-cyan-100">
                {action}
              </div>
            ))}
            <Button className="w-full">Open Action Center</Button>
          </CardContent>
        </Card>
      </section>

      <Card className="border-white/10 bg-slate-950/70">
        <CardHeader>
          <CardTitle>Team Load and Imbalance</CardTitle>
          <CardDescription>Overloaded consultants should be rebalanced before next SLA window.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {team_load.length === 0 ? (
            <p className="text-sm text-slate-400">No active assignment data available.</p>
          ) : (
            team_load.map((row) => (
              <div key={row.assignee} className="grid gap-2 rounded-2xl border border-white/10 bg-white/5 p-4 md:grid-cols-[1.2fr_repeat(4,minmax(0,1fr))]">
                <p className="text-sm font-medium text-white">{row.assignee}</p>
                <p className="text-xs text-slate-300">Open: {row.open_count}</p>
                <p className="text-xs text-slate-300">Critical: {row.critical_count}</p>
                <p className="text-xs text-slate-300">Breached: {row.breached_count}</p>
                <p className="text-xs text-amber-200">Load score: {row.workload_score.toFixed(1)}</p>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}

interface MetricCardProps {
  icon: typeof TrendingUp
  label: string
  value: string
  tone: 'cyan' | 'amber' | 'rose' | 'violet'
}

function MetricCard({ icon: Icon, label, value, tone }: MetricCardProps) {
  const toneMap: Record<MetricCardProps['tone'], string> = {
    cyan: 'from-cyan-500/35 via-cyan-500/20 to-slate-950/90',
    amber: 'from-amber-500/35 via-amber-500/20 to-slate-950/90',
    rose: 'from-rose-500/35 via-rose-500/20 to-slate-950/90',
    violet: 'from-violet-500/35 via-violet-500/20 to-slate-950/90',
  }

  return (
    <Card className={`kpi-card ${toneMap[tone]}`}>
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
