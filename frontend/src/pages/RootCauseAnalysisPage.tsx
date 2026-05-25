import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, Network, Repeat, ShieldCheck, Wrench } from 'lucide-react'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/services/api'

interface RCASnapshot {
  generated_at: string
  summary: {
    analyzed_open_defects: number
    detected_clusters: number
    at_risk_defects: number
    rca_confidence: number
    repeat_issue_rate: number
  }
  cluster_signals: {
    cluster: string
    open_count: number
    critical_count: number
    breached_count: number
    reopened_count: number
    avg_age_days: number
    signal_score: number
    likely_cause: string
  }[]
  top_recurring_patterns: {
    pattern: string
    occurrences: number
    impact: string
  }[]
  recommended_actions: string[]
}

async function fetchRCASnapshot() {
  const response = await api.get<RCASnapshot>('/root-cause-analysis/snapshot')
  return response.data
}

export function RootCauseAnalysisPage() {
  const query = useQuery({
    queryKey: ['root-cause-analysis', 'snapshot'],
    queryFn: fetchRCASnapshot,
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
        <CardContent className="py-12 text-center text-slate-300">Failed to load root cause analysis snapshot.</CardContent>
      </Card>
    )
  }

  const { summary, cluster_signals, top_recurring_patterns, recommended_actions } = query.data

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-2">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-300">Root Cause Analysis</p>
        <h1 className="text-3xl font-semibold text-white">Recurring Failure Pattern Intelligence</h1>
        <p className="text-sm text-slate-200">Identify systemic causes, not isolated symptoms, and execute prevention actions.</p>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <RCAMetric icon={Network} label="Detected Clusters" value={String(summary.detected_clusters)} tone="cyan" />
        <RCAMetric icon={AlertTriangle} label="At Risk Defects" value={String(summary.at_risk_defects)} tone="rose" />
        <RCAMetric icon={ShieldCheck} label="RCA Confidence" value={`${summary.rca_confidence.toFixed(1)}%`} tone="violet" />
        <RCAMetric icon={Repeat} label="Repeat Issue Rate" value={`${summary.repeat_issue_rate.toFixed(1)}%`} tone="amber" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Cluster Signals</CardTitle>
            <CardDescription>Prioritize high-signal clusters to reduce recurrence and SLA exposure.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {cluster_signals.length === 0 ? (
              <p className="text-sm text-slate-300">No active root-cause clusters detected.</p>
            ) : (
              cluster_signals.map((cluster) => (
                <div key={cluster.cluster} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-white">{cluster.cluster}</p>
                    <span className="rounded-full bg-rose-500/20 px-3 py-1 text-xs font-medium text-rose-200">Signal {cluster.signal_score.toFixed(1)}</span>
                  </div>
                  <p className="mt-2 text-xs text-slate-200">
                    Open {cluster.open_count} | Critical {cluster.critical_count} | Breached {cluster.breached_count} | Reopened {cluster.reopened_count}
                  </p>
                  <p className="mt-1 text-xs text-slate-200">Avg age {cluster.avg_age_days.toFixed(1)} days</p>
                  <p className="mt-2 text-sm text-cyan-100">Likely cause: {cluster.likely_cause}</p>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Recommended Actions</CardTitle>
            <CardDescription>Management interventions that prevent repeat incidents.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {recommended_actions.map((action) => (
              <div key={action} className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-sm text-cyan-100">
                {action}
              </div>
            ))}
            <Button className="w-full">Open RCA Action Queue</Button>
          </CardContent>
        </Card>
      </section>

      <Card className="border-white/10 bg-slate-950/70">
        <CardHeader>
          <CardTitle>Recurring Patterns</CardTitle>
          <CardDescription>Top repeated issue signatures extracted from active defect narratives.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {top_recurring_patterns.length === 0 ? (
            <p className="text-sm text-slate-300">No recurring text patterns detected yet.</p>
          ) : (
            top_recurring_patterns.map((pattern) => (
              <div key={pattern.pattern} className="grid gap-2 rounded-2xl border border-white/10 bg-white/5 p-4 md:grid-cols-[1.4fr_repeat(2,minmax(0,1fr))]">
                <p className="text-sm font-medium text-white">{pattern.pattern}</p>
                <p className="text-xs text-slate-200">Occurrences {pattern.occurrences}</p>
                <p className="text-xs text-amber-200">Impact {pattern.impact}</p>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}

interface RCAMetricProps {
  icon: typeof Wrench
  label: string
  value: string
  tone: 'cyan' | 'amber' | 'rose' | 'violet'
}

function RCAMetric({ icon: Icon, label, value, tone }: RCAMetricProps) {
  const tones: Record<RCAMetricProps['tone'], string> = {
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
