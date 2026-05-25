import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Cell,
  CartesianGrid,
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
import { CHART_COLORS } from '@lib/constants'
import { ChartCard } from '@components/common/ChartCard'
import type { AssignmentLoadPoint, DashboardTrendPoint, PriorityBreakdownPoint } from '@types'

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number }>; label?: string }) {
  if (!active || !payload?.length) {
    return null
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/95 px-3 py-2 text-xs text-slate-100 shadow-panel backdrop-blur-xl">
      <p className="font-semibold text-cyan-300">{label}</p>
      <p className="mt-1">{payload[0]?.value}</p>
    </div>
  )
}

export function SlaTrendChart({ data }: { data: DashboardTrendPoint[] }) {
  return (
    <ChartCard title="Defect throughput trend" description="Weekly intake, closure, and SLA breach behavior.">
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART_COLORS.cyan} stopOpacity={0.4} />
                <stop offset="95%" stopColor={CHART_COLORS.cyan} stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.12)" />
            <XAxis dataKey="label" stroke="rgba(148,163,184,0.7)" />
            <YAxis stroke="rgba(148,163,184,0.7)" />
            <Tooltip content={<ChartTooltip />} />
            <Legend />
            <Area type="monotone" dataKey="total" stroke={CHART_COLORS.cyan} fill="url(#trendFill)" strokeWidth={2} />
            <Line type="monotone" dataKey="closed" stroke={CHART_COLORS.emerald} strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="slaBreached" stroke={CHART_COLORS.rose} strokeWidth={2} dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  )
}

export function PriorityChart({ data }: { data: PriorityBreakdownPoint[] }) {
  return (
    <ChartCard title="Priority mix" description="Current defect distribution by severity band.">
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" innerRadius={65} outerRadius={95} paddingAngle={4}>
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  )
}

export function AssignmentChart({ data }: { data: AssignmentLoadPoint[] }) {
  return (
    <ChartCard title="Assignment load" description="Queue saturation and breach risk by team.">
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.12)" />
            <XAxis dataKey="name" stroke="rgba(148,163,184,0.7)" />
            <YAxis stroke="rgba(148,163,184,0.7)" />
            <Tooltip />
            <Legend />
            <Bar dataKey="workload" fill={CHART_COLORS.violet} radius={[12, 12, 0, 0]} />
            <Bar dataKey="breachRisk" fill={CHART_COLORS.amber} radius={[12, 12, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  )
}

export function ResolutionForecastChart({ data }: { data: DashboardTrendPoint[] }) {
  return (
    <ChartCard title="Resolution momentum" description="Closed work versus incoming demand pressure.">
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.12)" />
            <XAxis dataKey="label" stroke="rgba(148,163,184,0.7)" />
            <YAxis stroke="rgba(148,163,184,0.7)" />
            <Tooltip />
            <Line type="monotone" dataKey="open" stroke={CHART_COLORS.amber} strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="closed" stroke={CHART_COLORS.emerald} strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  )
}