import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Activity, Brain, GaugeCircle, RefreshCcw, TimerReset, Sparkles } from 'lucide-react'
import { PageHeader } from '@components/common/PageHeader'
import { Button } from '@components/ui/button'
import { Card, CardContent } from '@components/ui/card'
import { Badge } from '@components/ui/badge'
import { Select } from '@components/ui/select'
import { api } from '@/services/api'
import type { ModelStatusResponse } from '@types'

export function PredictionsPage() {
  const queryClient = useQueryClient()
  const statusQuery = useQuery({
    queryKey: ['predictions', 'status'],
    queryFn: async () => (await api.get<ModelStatusResponse>('/predictions/status')).data,
  })
  const defectsQuery = useQuery({
    queryKey: ['predictions', 'defects'],
    queryFn: async () =>
      (await api.get<{ items: Array<{ id: string; number: string; title: string; priority: string; status: string }> }>('/defects', { params: { page: 1, page_size: 3 } })).data,
  })

  const defects = defectsQuery.data?.items ?? []
  const [selectedDefectId, setSelectedDefectId] = useState<string | null>(null)

  useEffect(() => {
    if (!selectedDefectId && defects[0]) {
      setSelectedDefectId(defects[0].id)
    }
    if (selectedDefectId && !defects.some((item) => item.id === selectedDefectId)) {
      setSelectedDefectId(defects[0]?.id ?? null)
    }
  }, [defects, selectedDefectId])

  const slaQuery = useQuery({
    queryKey: ['predictions', 'sla', selectedDefectId],
    queryFn: async () => (await api.get(`/predictions/${selectedDefectId}/sla`)).data,
    enabled: Boolean(selectedDefectId),
  })
  const resolutionQuery = useQuery({
    queryKey: ['predictions', 'resolution', selectedDefectId],
    queryFn: async () => (await api.get(`/predictions/${selectedDefectId}/resolution-time`)).data,
    enabled: Boolean(selectedDefectId),
  })
  const assignmentQuery = useQuery({
    queryKey: ['predictions', 'assignment', selectedDefectId],
    queryFn: async () => (await api.get(`/predictions/${selectedDefectId}/assignment`)).data,
    enabled: Boolean(selectedDefectId),
  })

  const trainMutation = useMutation({
    mutationFn: async () => (await api.post('/predictions/train')).data,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['predictions'] })
    },
  })

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Predictive ops"
        title="Predictions"
        description="Estimate SLA breach probability, resolution time, and best assignment group before the queue backs up."
        actions={
          <Button variant="outline" onClick={() => trainMutation.mutate()} disabled={trainMutation.isPending}>
            <RefreshCcw className="mr-2 h-4 w-4" />
            Retrain models
          </Button>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="SLA model" value={statusQuery.data?.sla?.status ?? 'unknown'} delta="Training status" icon={Brain} tone="violet" />
        <MetricCard label="Embeddings" value={statusQuery.data?.embeddings_index?.exists ? `${statusQuery.data.embeddings_index.count}` : 'missing'} delta="FAISS index" icon={Activity} tone="amber" />
        <MetricCard label="Resolution model" value={statusQuery.data?.resolution?.status ?? 'unknown'} delta="Forecast service" icon={TimerReset} tone="cyan" />
        <MetricCard label="Assignment model" value={statusQuery.data?.assignment?.status ?? 'unknown'} delta="Routing service" icon={GaugeCircle} tone="emerald" />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardContent className="space-y-4 p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h3 className="text-xl font-semibold text-foreground">Live predictions</h3>
                <p className="text-sm text-muted-foreground">Pick a defect and inspect the current model outputs.</p>
              </div>
              <Badge>{defects.length} loaded</Badge>
            </div>

            <Select value={selectedDefectId ?? ''} onChange={(event) => setSelectedDefectId(event.target.value)}>
              {defects.map((defect) => (
                <option key={defect.id} value={defect.id}>
                  {defect.number} · {defect.title}
                </option>
              ))}
            </Select>

            <div className="rounded-3xl border border-slate-700/80 bg-slate-950/60 p-4">
              <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Selected defect</p>
              <p className="mt-2 text-lg font-semibold text-foreground">{defects.find((item) => item.id === selectedDefectId)?.title ?? 'No defect selected'}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {defects.find((item) => item.id === selectedDefectId)?.number} · {defects.find((item) => item.id === selectedDefectId)?.priority} · {defects.find((item) => item.id === selectedDefectId)?.status}
              </p>
            </div>

            <div className="grid gap-3 md:grid-cols-3">
              <PredictionPanel label="SLA breach" value={slaQuery.data ? `${Math.round((slaQuery.data.sla_breach_probability ?? 0) * 100)}%` : 'Loading...'} detail={`Risk level: ${slaQuery.data?.breach_risk_level ?? 'n/a'}`} />
              <PredictionPanel label="Resolution forecast" value={resolutionQuery.data ? `${resolutionQuery.data.estimated_hours}h` : 'Loading...'} detail={`ETA ${resolutionQuery.data?.estimated_completion_date ?? 'pending'}`} />
              <PredictionPanel label="Assignment" value={assignmentQuery.data?.recommendations?.[0]?.assignee ?? 'n/a'} detail={`Confidence ${Math.round((assignmentQuery.data?.recommendations?.[0]?.confidence_score ?? 0) * 100)}%`} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-4 p-6">
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-xl font-semibold text-foreground">Current defects</h3>
              <Button variant="outline" onClick={() => trainMutation.mutate()} disabled={trainMutation.isPending}>
                <Sparkles className="mr-2 h-4 w-4" />
                {trainMutation.isPending ? 'Training...' : 'Retrain models'}
              </Button>
            </div>
            <div className="space-y-3">
              {defects.map((defect) => (
                <button
                  key={defect.id}
                  type="button"
                  onClick={() => setSelectedDefectId(defect.id)}
                  className={`w-full rounded-2xl border p-4 text-left transition ${selectedDefectId === defect.id ? 'border-cyan-300/50 bg-cyan-400/10' : 'border-slate-700/80 bg-slate-950/50 hover:bg-slate-900/70'}`}
                >
                  <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">{defect.number}</p>
                  <p className="mt-2 font-medium text-foreground">{defect.title}</p>
                  <p className="text-sm text-muted-foreground">
                    {defect.priority} · {defect.status}
                  </p>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

interface MetricCardProps {
  label: string
  value: string
  delta: string
  tone?: 'cyan' | 'emerald' | 'amber' | 'rose' | 'violet'
  icon: typeof Brain
}

function MetricCard({ label, value, delta, tone = 'cyan', icon: Icon }: MetricCardProps) {
  const tones: Record<NonNullable<MetricCardProps['tone']>, string> = {
    cyan: 'from-cyan-500/35 via-cyan-500/20 to-slate-950/90',
    emerald: 'from-emerald-500/35 via-emerald-500/20 to-slate-950/90',
    amber: 'from-amber-500/35 via-amber-500/20 to-slate-950/90',
    rose: 'from-rose-500/35 via-rose-500/20 to-slate-950/90',
    violet: 'from-violet-500/35 via-violet-500/20 to-slate-950/90',
  }

  return (
    <Card className={`kpi-card ${tones[tone]}`}>
      <CardContent className="flex items-start justify-between gap-4 p-6">
        <div>
          <p className="kpi-label">{label}</p>
          <p className="kpi-value">{value}</p>
          <p className="kpi-detail">{delta}</p>
        </div>
        <div className="kpi-icon-shell">
          <Icon className="h-5 w-5" />
        </div>
      </CardContent>
    </Card>
  )
}

function PredictionPanel({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-2xl border border-slate-700/80 bg-slate-950/60 p-4">
      <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-foreground">{value}</p>
      <p className="text-sm text-muted-foreground">{detail}</p>
    </div>
  )
}
