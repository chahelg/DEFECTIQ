import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, ShieldAlert, Siren, Timer } from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/services/api'

interface SLARiskSnapshot {
  generated_at: string
  summary: {
    open_defects: number
    at_risk_defects: number
    critical_risk: number
    avg_breach_probability: number
  }
  risk_heatmap: { priority: string; status: string; count: number }[]
  assignment_group_risk: { assignee: string; open_count: number; breached_count: number; risk_ratio: number }[]
  top_risk_defects: {
    defect_number: string
    title: string
    priority: string
    status: string
    assignee: string
    age_days: number
    hours_to_sla: number | null
    breach_probability: number
    risk_level: string
    recommended_intervention: string
  }[]
  actions: string[]
}

async function fetchSlaRiskSnapshot() {
  const response = await api.get<SLARiskSnapshot>('/sla-risk/snapshot')
  return response.data
}

export function SLARiskCenterPage() {
  const query = useQuery({
    queryKey: ['sla-risk', 'snapshot'],
    queryFn: fetchSlaRiskSnapshot,
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
        <CardContent className="py-12 text-center text-slate-300">Failed to load SLA risk intelligence snapshot.</CardContent>
      </Card>
    )
  }

  const { summary, top_risk_defects, assignment_group_risk, actions } = query.data

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-2">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-300">SLA Risk Intelligence Center</p>
        <h1 className="text-3xl font-semibold text-white">Breach Prevention and Intervention Queue</h1>
        <p className="text-sm text-slate-200">Detect where SLA breaches will occur next and act before escalation windows close.</p>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <RiskCard icon={Timer} label="Open Defects" value={String(summary.open_defects)} tone="cyan" />
        <RiskCard icon={AlertTriangle} label="At Risk" value={String(summary.at_risk_defects)} tone="amber" />
        <RiskCard icon={Siren} label="Critical Risk" value={String(summary.critical_risk)} tone="rose" />
        <RiskCard icon={ShieldAlert} label="Avg Breach Probability" value={`${summary.avg_breach_probability.toFixed(1)}%`} tone="violet" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Top SLA Risk Defects</CardTitle>
            <CardDescription>Prioritized by breach probability and urgency windows.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {top_risk_defects.slice(0, 10).map((item) => (
              <div key={item.defect_number} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-white">{item.defect_number} - {item.title}</p>
                  <span className="rounded-full bg-rose-500/20 px-3 py-1 text-xs font-medium text-rose-200">
                    {(item.breach_probability * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="mt-2 text-xs text-slate-200">
                  {item.priority} | {item.status} | {item.assignee} | Age {item.age_days}d | SLA window {item.hours_to_sla ?? 'N/A'}h
                </p>
                <p className="mt-2 text-sm text-cyan-100">{item.recommended_intervention}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Intervention Actions</CardTitle>
            <CardDescription>Immediate manager actions to reduce breach exposure.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {actions.map((action) => (
              <div key={action} className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-sm text-cyan-100">
                {action}
              </div>
            ))}
            <Button className="w-full">Trigger Escalation Workflow</Button>
          </CardContent>
        </Card>
      </section>

      <Card className="border-white/10 bg-slate-950/70">
        <CardHeader>
          <CardTitle>Assignment-Level Risk Exposure</CardTitle>
          <CardDescription>Use this table to rebalance high-risk owners before SLA breach windows.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {assignment_group_risk.map((row) => (
            <div key={row.assignee} className="grid gap-2 rounded-2xl border border-white/10 bg-white/5 p-4 md:grid-cols-[1.2fr_repeat(3,minmax(0,1fr))]">
              <p className="text-sm font-medium text-white">{row.assignee}</p>
              <p className="text-xs text-slate-200">Open: {row.open_count}</p>
              <p className="text-xs text-slate-200">Breached: {row.breached_count}</p>
              <p className="text-xs text-amber-200">Risk ratio: {row.risk_ratio.toFixed(1)}%</p>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

interface RiskCardProps {
  icon: typeof Timer
  label: string
  value: string
  tone: 'cyan' | 'amber' | 'rose' | 'violet'
}

function RiskCard({ icon: Icon, label, value, tone }: RiskCardProps) {
  const tones: Record<RiskCardProps['tone'], string> = {
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
