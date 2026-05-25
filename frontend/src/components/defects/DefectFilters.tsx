import { Button } from '@components/ui/button'
import { Input } from '@components/ui/input'
import { Select } from '@components/ui/select'
import { Switch } from '@components/ui/switch'
import { FILTER_PRESETS } from '@lib/constants'
import type { DefectFilters } from '@types'

interface DefectFiltersProps {
  filters: DefectFilters
  onChange: (patch: Partial<DefectFilters>) => void
  onClear: () => void
}

export function DefectFiltersBar({ filters, onChange, onClear }: DefectFiltersProps) {
  return (
    <div className="glass-card mb-6 p-4">
      <div className="grid gap-4 xl:grid-cols-5">
        <Input
          value={filters.search}
          onChange={(event) => onChange({ search: event.target.value, page: 1 })}
          placeholder="Search ticket, title, service, or owner"
          className="xl:col-span-2"
        />
        <Select value={filters.status[0] ?? ''} onChange={(event) => onChange({ status: event.target.value ? [event.target.value] : [], page: 1 })}>
          <option value="">All statuses</option>
          {FILTER_PRESETS.statuses.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </Select>
        <Select value={filters.priority[0] ?? ''} onChange={(event) => onChange({ priority: event.target.value ? [event.target.value] : [], page: 1 })}>
          <option value="">All priorities</option>
          {FILTER_PRESETS.priorities.map((priority) => (
            <option key={priority} value={priority}>
              {priority}
            </option>
          ))}
        </Select>
        <div className="flex items-center justify-between rounded-2xl border border-white/10 px-4 py-2.5">
          <div>
            <p className="text-sm font-medium text-foreground">SLA breached only</p>
            <p className="text-xs text-muted-foreground">Focus on the highest risk tickets</p>
          </div>
          <Switch
            checked={filters.slaBreached === true}
            onChange={(event) => onChange({ slaBreached: event.target.checked ? true : null, page: 1 })}
          />
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-3">
        <Button variant="outline" size="sm" onClick={onClear}>
          Clear filters
        </Button>
      </div>
    </div>
  )
}