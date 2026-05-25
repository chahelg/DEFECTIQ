import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@components/common/PageHeader'
import { Badge } from '@components/ui/badge'
import { Button } from '@components/ui/button'
import { Card, CardContent } from '@components/ui/card'
import { api } from '@/services/api'
import type { InsightResponse } from '@types'

export function AIInsightsPage() {
  const queryClient = useQueryClient()
  const insightsQuery = useQuery({
    queryKey: ['insights', 'latest'],
    queryFn: async () => (await api.get<InsightResponse>('/insights/latest')).data,
  })
  const refreshMutation = useMutation({
    mutationFn: async () => (await api.post('/insights/generate')).data,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['insights', 'latest'] })
    },
  })
  const metrics = insightsQuery.data?.metrics
  const recommendations = insightsQuery.data?.recommendations ?? []

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="AI narratives"
        title="AI Insights"
        description="Read the platform-generated narratives that explain the latest patterns, risks, and recommended actions."
        actions={
          <Button variant="outline" onClick={() => refreshMutation.mutate()} disabled={refreshMutation.isPending}>
            {refreshMutation.isPending ? 'Generating...' : 'Generate insights'}
          </Button>
        }
      />

      <div className="grid gap-4 md:grid-cols-3">
        <InsightMetric label="Total defects" value={String(metrics?.total_defects ?? 0)} />
        <InsightMetric label="SLA breaches" value={String(metrics?.sla_breaches ?? 0)} />
        <InsightMetric label="Average resolution" value={metrics ? `${metrics.average_resolution_hours}h` : '0h'} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card className="relative overflow-hidden">
          <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-cyan-400 via-violet-400 to-emerald-400" />
          <CardContent className="space-y-4 p-6 pt-8">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">Executive summary</p>
            <p className="text-sm text-muted-foreground">{insightsQuery.data?.summary?.summary ?? insightsQuery.data?.openai ?? 'No insight summary returned yet.'}</p>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-foreground">
              <span className="font-semibold text-cyan-300">Method:</span> {insightsQuery.data?.method ?? 'unknown'}
            </div>
            {insightsQuery.data?.summary?.summary ? <Badge className="w-fit bg-cyan-400/10 text-cyan-100">Live narrative ready</Badge> : null}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-4 p-6">
            <h3 className="text-xl font-semibold text-foreground">Recommendations</h3>
            <div className="space-y-3">
              {recommendations.map((item) => (
                <div key={item} className="rounded-2xl border border-slate-700/80 bg-slate-950/60 p-4 text-sm text-foreground">{item}</div>
              ))}
              {!recommendations.length ? <p className="text-sm text-muted-foreground">No recommendations returned yet.</p> : null}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function InsightMetric({ label, value }: { label: string; value: string }) {
  return (
    <Card className="kpi-card from-slate-800/70 via-slate-800/55 to-slate-950/90">
      <CardContent className="p-6">
        <p className="kpi-label">{label}</p>
        <p className="kpi-value">{value}</p>
      </CardContent>
    </Card>
  )
}
