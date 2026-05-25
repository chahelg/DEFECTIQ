import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
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
                <Tooltip contentStyle={{ background: '#020617', border: '1px solid rgba(255,255,255,0.1)' }} />
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
                  <Tooltip contentStyle={{ background: '#020617', border: '1px solid rgba(255,255,255,0.1)' }} />
                  <Legend />
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
                  <Tooltip contentStyle={{ background: '#020617', border: '1px solid rgba(255,255,255,0.1)' }} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>
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
    cyan: 'from-cyan-400/15 to-cyan-300/5 text-cyan-200 ring-cyan-300/20',
    emerald: 'from-emerald-400/15 to-emerald-300/5 text-emerald-200 ring-emerald-300/20',
    amber: 'from-amber-400/15 to-amber-300/5 text-amber-200 ring-amber-300/20',
    rose: 'from-rose-400/15 to-rose-300/5 text-rose-200 ring-rose-300/20',
    violet: 'from-violet-400/15 to-violet-300/5 text-violet-200 ring-violet-300/20',
  }

  return (
    <Card className={`border-white/10 bg-gradient-to-br ${tones[tone]}`}>
      <CardContent className="flex items-start justify-between gap-4 p-6">
        <div>
          <p className="text-sm text-slate-300">{label}</p>
          <p className="mt-3 text-3xl font-semibold text-white">{value}</p>
        </div>
        <div className="rounded-2xl bg-white/10 p-3 ring-1 ring-white/10">
          <Icon className="h-5 w-5" />
        </div>
      </CardContent>
    </Card>
  )
}