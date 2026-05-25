import { Badge } from '@components/ui/badge'
import { Card, CardContent } from '@components/ui/card'
import type { SimilarDefect } from '@types'

interface SimilarDefectsListProps {
  defects: SimilarDefect[]
  activeId?: string
  onSelect?: (defect: SimilarDefect) => void
}

export function SimilarDefectsList({ defects, activeId, onSelect }: SimilarDefectsListProps) {
  return (
    <div className="grid gap-4 xl:grid-cols-3">
      {defects.map((defect) => (
        <Card
          key={defect.id}
          className={`relative overflow-hidden ${activeId === defect.id ? 'ring-2 ring-cyan-300/60' : ''}`}
          onClick={() => onSelect?.(defect)}
          role={onSelect ? 'button' : undefined}
          tabIndex={onSelect ? 0 : undefined}
        >
          <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-cyan-400 via-violet-400 to-emerald-400" />
          <CardContent className="space-y-3 p-5 pt-6">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">{defect.ticketNumber}</p>
                <h3 className="mt-2 text-lg font-semibold text-foreground">{defect.title}</h3>
              </div>
              <Badge>{Math.round(defect.similarity * 100)}% match</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{defect.assignmentGroup}</p>
            <div className="flex flex-wrap gap-2">
              <Badge className="border border-white/10 bg-white/5">{defect.priority}</Badge>
              <Badge className="border border-white/10 bg-white/5">{defect.status}</Badge>
              <Badge className="border border-white/10 bg-white/5">{defect.resolutionHours}h resolution</Badge>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}