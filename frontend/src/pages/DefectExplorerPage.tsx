import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronLeft, ChevronRight, Search, X } from 'lucide-react'
import { api } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import type { DefectListResponse, DefectRecord } from '@/types/phase1'

interface DefectFilters {
  status: string
  priority: string
  search: string
  page: number
  pageSize: number
}

const initialFilters: DefectFilters = {
  status: '',
  priority: '',
  search: '',
  page: 1,
  pageSize: 10,
}

async function fetchDefects(filters: DefectFilters) {
  const response = await api.get<DefectListResponse>('/defects', {
    params: {
      page: filters.page,
      page_size: filters.pageSize,
      status: filters.status || undefined,
      priority: filters.priority || undefined,
      search: filters.search || undefined,
    },
  })
  return response.data
}

async function fetchDefectById(defectId: string) {
  const response = await api.get<DefectRecord>(`/defects/${defectId}`)
  return response.data
}

function formatDate(value: string | null | undefined) {
  if (!value) {
    return 'N/A'
  }

  return new Date(value).toLocaleString()
}

export function DefectExplorerPage() {
  const [filters, setFilters] = useState<DefectFilters>(initialFilters)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const defectsQuery = useQuery({
    queryKey: ['defects', filters],
    queryFn: () => fetchDefects(filters),
    placeholderData: (previousData) => previousData,
  })

  const selectedDefectQuery = useQuery({
    queryKey: ['defect', selectedId],
    queryFn: () => fetchDefectById(selectedId ?? ''),
    enabled: Boolean(selectedId),
  })

  const currentPage = defectsQuery.data?.page ?? filters.page
  const totalPages = defectsQuery.data?.total_pages ?? 1
  const tableRows = defectsQuery.data?.items ?? []

  const updateFilter = (patch: Partial<DefectFilters>) => {
    setFilters((current) => ({ ...current, ...patch, page: patch.page ?? 1 }))
  }

  const clearFilters = () => {
    setSelectedId(null)
    setFilters(initialFilters)
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_22rem]">
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="border-white/10 bg-slate-950/70">
            <CardContent className="p-6">
              <p className="text-sm text-slate-400">Results</p>
              <p className="mt-2 text-3xl font-semibold text-white">{defectsQuery.data?.total ?? 0}</p>
            </CardContent>
          </Card>
          <Card className="border-white/10 bg-slate-950/70">
            <CardContent className="p-6">
              <p className="text-sm text-slate-400">Page Size</p>
              <p className="mt-2 text-3xl font-semibold text-white">{filters.pageSize}</p>
            </CardContent>
          </Card>
          <Card className="border-white/10 bg-slate-950/70">
            <CardContent className="p-6">
              <p className="text-sm text-slate-400">Current Page</p>
              <p className="mt-2 text-3xl font-semibold text-white">{currentPage}</p>
            </CardContent>
          </Card>
        </div>

        <Card className="border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Defect Explorer</CardTitle>
            <CardDescription>Filter and inspect live defect records from PostgreSQL.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-3 md:grid-cols-[1fr_1fr_2fr_auto]">
              <Select value={filters.status} onChange={(event) => updateFilter({ status: event.target.value })}>
                <option value="">All Statuses</option>
                <option value="Open">Open</option>
                <option value="In Progress">In Progress</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
                <option value="Reopened">Reopened</option>
              </Select>
              <Select value={filters.priority} onChange={(event) => updateFilter({ priority: event.target.value })}>
                <option value="">All Priorities</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </Select>
              <div className="relative">
                <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <Input
                  className="pl-10"
                  placeholder="Search number, title, category..."
                  value={filters.search}
                  onChange={(event) => updateFilter({ search: event.target.value })}
                />
              </div>
              <Button variant="outline" onClick={clearFilters} type="button">
                <X className="mr-2 h-4 w-4" />
                Clear
              </Button>
            </div>

            <div className="overflow-hidden rounded-3xl border border-white/10">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Number</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Assigned To</TableHead>
                    <TableHead>Opened At</TableHead>
                    <TableHead>SLA</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tableRows.map((defect) => (
                    <TableRow key={defect.id} className="cursor-pointer" onClick={() => setSelectedId(defect.id)}>
                      <TableCell className="font-medium text-cyan-200">{defect.number}</TableCell>
                      <TableCell>{defect.title}</TableCell>
                      <TableCell>{defect.priority}</TableCell>
                      <TableCell>{defect.status}</TableCell>
                      <TableCell>{defect.category}</TableCell>
                      <TableCell>{defect.assigned_to ?? 'Unassigned'}</TableCell>
                      <TableCell>{formatDate(defect.opened_at)}</TableCell>
                      <TableCell>{defect.is_sla_breached ? 'Breached' : 'OK'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3 rounded-3xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
              <div className="flex items-center gap-3">
                <Button
                  disabled={filters.page <= 1}
                  onClick={() => updateFilter({ page: filters.page - 1 })}
                  size="sm"
                  type="button"
                  variant="outline"
                >
                  <ChevronLeft className="mr-2 h-4 w-4" />
                  Prev
                </Button>
                <span>
                  Page {currentPage} of {totalPages}
                </span>
                <Button
                  disabled={filters.page >= totalPages}
                  onClick={() => updateFilter({ page: filters.page + 1 })}
                  size="sm"
                  type="button"
                  variant="outline"
                >
                  Next
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              </div>

              <div className="flex items-center gap-3">
                <span>Page size</span>
                <Select
                  className="w-28"
                  value={String(filters.pageSize)}
                  onChange={(event) => updateFilter({ pageSize: Number(event.target.value), page: 1 })}
                >
                  {[5, 10, 20, 50].map((value) => (
                    <option key={value} value={value}>
                      {value}
                    </option>
                  ))}
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <aside className="xl:sticky xl:top-24 xl:h-[calc(100vh-7rem)]">
        <Card className="h-full border-white/10 bg-slate-950/70">
          <CardHeader>
            <CardTitle>Defect Details</CardTitle>
            <CardDescription>Click a row to inspect the full record.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 overflow-y-auto">
            {selectedId && selectedDefectQuery.data ? (
              <div className="space-y-3 text-sm text-slate-300">
                {Object.entries(selectedDefectQuery.data).map(([key, value]) => (
                  <div key={key} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.18em] text-slate-500">{key.split('_').join(' ')}</p>
                    <p className="mt-1 break-words text-slate-100">{String(value ?? 'N/A')}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-3xl border border-dashed border-white/10 bg-white/5 p-8 text-center text-sm text-slate-400">
                Select a defect from the table to see all fields.
              </div>
            )}
          </CardContent>
        </Card>
      </aside>
    </div>
  )
}