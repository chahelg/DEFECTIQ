import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { AlertTriangle, Clock3, RefreshCcw, ShieldAlert, Sparkles } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/services/api'
import type { CountPoint, KpiResponse, TrendPoint } from '@/types/phase1'

const PIE_COLORS = ['#22d3ee', '#38bdf8', '#818cf8', '#c084fc', '#f472b6', '#fb7185']

async function fetchKpis() {
  const response = await api.get<KpiResponse>('/dashboard/kpis')
  return response.data
}

async function fetchTrends() {
  const response = await api.get<TrendPoint[]>('/dashboard/trends')
  return response.data
}

async function fetchByPriority() {
  const response = await api.get<CountPoint[]>('/dashboard/by_priority')
  return response.data
}

async function fetchByStatus() {
  const response = await api.get<CountPoint[]>('/dashboard/by_status')
  return response.data
}

function SkeletonCard() {
  return <div className="h-28 animate-pulse rounded-3xl border border-white/10 bg-white/5" />
}

export function DashboardPage() {
  const queryClient = useQueryClient()
  const kpisQuery = useQuery({ queryKey: ['dashboard', 'kpis'], queryFn: fetchKpis })
  const trendsQuery = useQuery({ queryKey: ['dashboard', 'trends'], queryFn: fetchTrends })
  const priorityQuery = useQuery({ queryKey: ['dashboard', 'priority'], queryFn: fetchByPriority })
  const statusQuery = useQuery({ queryKey: ['dashboard', 'status'], queryFn: fetchByStatus })

  const isLoading = kpisQuery.isPending || trendsQuery.isPending || priorityQuery.isPending || statusQuery.isPending
  const isError = kpisQuery.isError || trendsQuery.isError || priorityQuery.isError || statusQuery.isError

  const retry = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'kpis'] }),
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'trends'] }),
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'priority'] }),
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'status'] }),
    ])
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <SkeletonCard key={index} />
          ))}
        </div>
        <div className="grid gap-6 xl:grid-cols-2">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    )
  }

  if (isError || !kpisQuery.data || !trendsQuery.data || !priorityQuery.data || !statusQuery.data) {
    return (
      <Card className="border-white/10 bg-slate-950/70">
        <CardContent className="flex flex-col items-center gap-4 py-16 text-center">
          <AlertTriangle className="h-10 w-10 text-amber-300" />
          <div>
            <h2 className="text-2xl font-semibold text-white">Unable to load dashboard data</h2>
            <p className="mt-2 text-sm text-slate-400">Check that the backend is running and the seeded data exists.</p>
          </div>
          <Button onClick={retry} variant="outline">
            <RefreshCcw className="mr-2 h-4 w-4" />
            Retry
          </Button>
        </CardContent>
      </Card>
    )
  }

  const kpis = kpisQuery.data
  const slaBreachedPct = Math.max(0, 100 - kpis.sla_compliance_pct)
  const topPriority = [...priorityQuery.data].sort((left, right) => right.value - left.value)[0]
  const topStatus = [...statusQuery.data].sort((left, right) => right.value - left.value)[0]

  const actionSignals = [
    {
      key: 'Open Defects',
      value: kpis.open_defects,
      action: 'Run focused triage on the top open clusters.',
    },
    {
      key: 'Critical Defects',
      value: kpis.critical_count,
      action: 'Assign incident leads and 4-hour checkpoints.',
    },
    {
      key: 'SLA Breaches',
      value: kpis.sla_breached_count,
      action: 'Escalate breached queue with owner accountability.',
    },
    {
      key: 'Reopen Pressure',
      value: Number(kpis.reopen_rate.toFixed(1)),
      action: 'Audit root causes for repeatedly reopened items.',
    },
  ]

  const businessActions = [
    `Highest defect concentration is '${topPriority?.name ?? 'N/A'}' priority — allocate extra resolver capacity there first.`,
    `Dominant status is '${topStatus?.name ?? 'N/A'}' — clear this stage bottleneck to improve flow velocity.`,
    `SLA breach rate is ${slaBreachedPct.toFixed(1)}% — enforce urgent queue review every 4 hours.`,
  ]

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard icon={Sparkles} label="Total Defects" value={kpis.total_defects.toLocaleString()} />
        <MetricCard icon={AlertTriangle} label="Open" value={kpis.open_defects.toLocaleString()} tone="amber" />
        <MetricCard icon={ShieldAlert} label="Closed" value={kpis.closed_defects.toLocaleString()} tone="emerald" />
        <MetricCard icon={Clock3} label="SLA Breached %" value={`${slaBreachedPct.toFixed(1)}%`} tone="rose" />
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard icon={AlertTriangle} label="Critical Count" value={kpis.critical_count.toLocaleString()} tone="violet" />
        <MetricCard icon={Clock3} label="Avg Resolution Time" value={`${kpis.avg_resolution_hours.toFixed(1)} hrs`} tone="cyan" />
        <MetricCard icon={RefreshCcw} label="Reopen Rate" value={`${kpis.reopen_rate.toFixed(1)}%`} tone="emerald" />
        <MetricCard icon={ShieldAlert} label="SLA Compliance" value={`${kpis.sla_compliance_pct.toFixed(1)}%`} tone="cyan" />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Defect Trend</CardTitle>
            <CardDescription>Defects opened over the last 12 weeks.</CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendsQuery.data}>
                <CartesianGrid stroke="rgba(148,163,184,0.15)" strokeDasharray="3 3" />
                <XAxis
                  dataKey="week"
                  tick={{ fill: '#cbd5e1', fontSize: 12 }}
                  tickFormatter={(value: string | number) => String(value).slice(5)}
                />
                <YAxis tick={{ fill: '#cbd5e1', fontSize: 12 }} />
                <Tooltip content={<ChartTooltip />} />
                <Line dataKey="count" stroke="#22d3ee" strokeWidth={3} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <div className="grid gap-6">
          <Card className="border-white/10 bg-slate-950/70">
            <CardHeader>
              <CardTitle>By Priority</CardTitle>
            </CardHeader>
            <CardContent className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={priorityQuery.data} dataKey="value" nameKey="name" innerRadius={48} outerRadius={88} paddingAngle={4}>
                    {priorityQuery.data.map((entry, index) => (
                      <Cell key={entry.name} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<ChartTooltip />} />
                  <Legend wrapperStyle={{ color: '#e2e8f0', fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="border-white/10 bg-slate-950/70">
            <CardHeader>
              <CardTitle>By Status</CardTitle>
            </CardHeader>
            <CardContent className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={statusQuery.data} dataKey="value" nameKey="name" innerRadius={48} outerRadius={88} paddingAngle={4}>
                    {statusQuery.data.map((entry, index) => (
                      <Cell key={entry.name} fill={PIE_COLORS[(index + 2) % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip content={<ChartTooltip />} />
                  <Legend wrapperStyle={{ color: '#e2e8f0', fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_1fr]">
        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Operational Action Signals</CardTitle>
            <CardDescription>Business-facing indicators with direct intervention guidance.</CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={actionSignals}>
                <CartesianGrid stroke="rgba(148,163,184,0.15)" strokeDasharray="3 3" />
                <XAxis dataKey="key" tick={{ fill: '#cbd5e1', fontSize: 11 }} interval={0} angle={-12} textAnchor="end" height={60} />
                <YAxis tick={{ fill: '#cbd5e1', fontSize: 12 }} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="value" radius={[10, 10, 0, 0]} fill="#22d3ee" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Recommended Business Actions</CardTitle>
            <CardDescription>Immediate actions derived from live operational metrics.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {businessActions.map((item) => (
              <div key={item} className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-sm text-cyan-100">
                {item}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

interface ChartTooltipProps {
  active?: boolean
  payload?: Array<{ name?: string; value?: number | string; color?: string; payload?: Record<string, unknown> }>
  label?: string
}

function ChartTooltip({ active, payload, label }: ChartTooltipProps) {
  if (!active || !payload?.length) {
    return null
  }

  const detailText = typeof payload[0]?.payload?.action === 'string' ? payload[0].payload.action : null

  return (
    <div className="max-w-xs rounded-xl border border-white/15 bg-slate-950/95 px-3 py-2 text-xs text-slate-100 shadow-xl">
      {label ? <p className="mb-1 font-semibold text-white">{label}</p> : null}
      <div className="space-y-1">
        {payload.map((entry) => (
          <div key={`${entry.name}-${entry.value}`} className="flex items-center justify-between gap-3">
            <span className="inline-flex items-center gap-2 text-slate-200">
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: entry.color ?? '#22d3ee' }} />
              {entry.name}
            </span>
            <span className="font-semibold text-white">{entry.value}</span>
          </div>
        ))}
      </div>
      {detailText ? <p className="mt-2 text-[11px] text-cyan-100">{detailText}</p> : null}
    </div>
  )
}

interface MetricCardProps {
  label: string
  value: string
  tone?: 'cyan' | 'emerald' | 'amber' | 'rose' | 'violet'
  icon: typeof Sparkles
}

function MetricCard({ label, value, tone = 'cyan', icon: Icon }: MetricCardProps) {
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
        </div>
        <div className="kpi-icon-shell">
          <Icon className="h-5 w-5" />
        </div>
      </CardContent>
    </Card>
  )
}