import { Badge } from '@components/ui/badge'
import { Button } from '@components/ui/button'
import { Card } from '@components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@components/ui/table'
import { cn } from '@lib/utils'
import type { Defect } from '@types'
import { Eye, FileDown, FlagTriangleRight } from 'lucide-react'

interface DefectTableProps {
  defects: Defect[]
  onViewDefect?: (defect: Defect) => void
  onPredict?: (defect: Defect) => void
}

function priorityTone(priority: Defect['priority']) {
  switch (priority) {
    case 'Critical':
      return 'border-rose-500/30 bg-rose-500/10 text-rose-200'
    case 'High':
      return 'border-amber-500/30 bg-amber-500/10 text-amber-200'
    case 'Medium':
      return 'border-cyan-500/30 bg-cyan-500/10 text-cyan-200'
    default:
      return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200'
  }
}

function statusTone(status: Defect['status']) {
  switch (status) {
    case 'Open':
      return 'border-cyan-500/30 bg-cyan-500/10 text-cyan-200'
    case 'In Progress':
      return 'border-violet-500/30 bg-violet-500/10 text-violet-200'
    case 'Resolved':
      return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200'
    case 'Closed':
      return 'border-slate-500/30 bg-slate-500/10 text-slate-200'
    case 'Reopened':
      return 'border-rose-500/30 bg-rose-500/10 text-rose-200'
    default:
      return 'border-amber-500/30 bg-amber-500/10 text-amber-200'
  }
}

export function DefectTable({ defects, onViewDefect, onPredict }: DefectTableProps) {
  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Ticket</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>Assignment</TableHead>
              <TableHead>SLA</TableHead>
              <TableHead>Updated</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {defects.map((defect) => (
              <TableRow key={defect.id}>
                <TableCell className="font-medium text-cyan-300">{defect.ticketNumber}</TableCell>
                <TableCell>
                  <div>
                    <p className="font-medium text-foreground">{defect.title}</p>
                    <p className="mt-1 max-w-xl text-xs text-muted-foreground">{defect.description}</p>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge className={cn('border', statusTone(defect.status))}>{defect.status}</Badge>
                </TableCell>
                <TableCell>
                  <Badge className={cn('border', priorityTone(defect.priority))}>{defect.priority}</Badge>
                </TableCell>
                <TableCell>
                  <div>
                    <p className="font-medium text-foreground">{defect.assignmentGroup}</p>
                    <p className="text-xs text-muted-foreground">{defect.assignedTo}</p>
                  </div>
                </TableCell>
                <TableCell>
                  <span className={defect.slaBreached ? 'text-rose-300' : 'text-emerald-300'}>
                    {defect.slaBreached ? 'Breached' : 'Healthy'}
                  </span>
                </TableCell>
                <TableCell>{new Date(defect.updatedAt).toLocaleString()}</TableCell>
                <TableCell>
                  <div className="flex justify-end gap-2">
                    <Button variant="ghost" size="icon" onClick={() => onViewDefect?.(defect)} aria-label="View defect">
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => onPredict?.(defect)} aria-label="Predict defect outcome">
                      <FlagTriangleRight className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" aria-label="Export defect">
                      <FileDown className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </Card>
  )
}