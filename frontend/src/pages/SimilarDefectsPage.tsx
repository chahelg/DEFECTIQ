import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { PageHeader } from '@components/common/PageHeader'
import { SimilarDefectsList } from '@components/ai/SimilarDefectsList'
import { Badge } from '@components/ui/badge'
import { Button } from '@components/ui/button'
import { Card, CardContent } from '@components/ui/card'
import { Input } from '@components/ui/input'
import { api } from '@/services/api'
import type { DefectPriority, DefectStatus, SemanticSearchResult, SimilarDefect } from '@types'

export function SimilarDefectsPage() {
  const [query, setQuery] = useState('payments checkout timeout')
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const searchQuery = useQuery({
    queryKey: ['nlp', 'search', query],
    queryFn: async () =>
      (
        await api.post<{ results: Array<{ id: string; number?: string; title: string; description?: string | null; priority?: string; status?: string; assigned_to?: string | null; score?: number }> }>('/nlp/semantic-search', {
          query,
          top_k: 6,
        })
      ).data,
  })
  const keywordsQuery = useQuery({
    queryKey: ['nlp', 'keywords'],
    queryFn: async () => (await api.get<{ keywords: Array<{ keyword: string; score: number }> }>('/nlp/keywords')).data,
  })
  const clusterQuery = useQuery({
    queryKey: ['nlp', 'cluster'],
    queryFn: async () => (await api.post<{ clusters: Array<{ cluster_id: string; size: number; sample_titles?: string[] }>; status: string }>('/nlp/cluster', { limit: 100 })).data,
  })

  const defects = useMemo<SimilarDefect[]>(
    () =>
      (searchQuery.data?.results ?? []).map((item) => ({
        id: item.id,
        ticketNumber: item.number ?? item.id,
        title: item.title,
        similarity: item.score ?? 0,
        priority: (item.priority as DefectPriority) ?? 'Medium',
        status: (item.status as DefectStatus) ?? 'Open',
        assignmentGroup: item.assigned_to ?? item.description ?? 'Unknown',
        resolutionHours: Math.round((1 - (item.score ?? 0)) * 24),
      })),
    [searchQuery.data?.results],
  )

  useEffect(() => {
    if (!selectedId && defects[0]) {
      setSelectedId(defects[0].id)
    }
    if (selectedId && !defects.some((item) => item.id === selectedId)) {
      setSelectedId(defects[0]?.id ?? null)
    }
  }, [defects, selectedId])

  const selectedDefect = defects.find((item) => item.id === selectedId) ?? defects[0] ?? null
  const summaryQuery = useQuery({
    queryKey: ['nlp', 'summary', selectedDefect?.id],
    queryFn: async () => (await api.post<{ summary?: string; actions?: string[]; risk?: string; method?: string }>('/nlp/summarize', { defect_id: selectedDefect?.id })).data,
    enabled: Boolean(selectedDefect?.id),
  })

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="NLP intelligence"
        title="NLP Intelligence"
        description="Search by meaning, review semantically related defects, inspect auto-summaries, and see the dominant language patterns in the dataset."
      />

      <Card>
        <CardContent className="space-y-4 p-6">
          <div className="flex flex-col gap-3 lg:flex-row">
            <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Describe the issue to search for" />
            <Button onClick={() => searchQuery.refetch()} type="button">
              Search
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <Metric label="Matches" value={String(defects.length)} detail="Semantic hits returned" />
            <Metric label="Clusters" value={String(clusterQuery.data?.clusters?.length ?? 0)} detail={clusterQuery.data?.status ?? 'pending'} />
            <Metric label="Keywords" value={String(keywordsQuery.data?.keywords?.length ?? 0)} detail="Top terms extracted" />
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardContent className="space-y-4 p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Selected match</p>
                <h3 className="mt-2 text-2xl font-semibold text-foreground">{selectedDefect?.title ?? 'No match selected'}</h3>
              </div>
              {selectedDefect ? <Badge>{Math.round(selectedDefect.similarity * 100)}% match</Badge> : null}
            </div>

            {selectedDefect ? (
              <div className="space-y-3 rounded-3xl border border-slate-700/80 bg-slate-950/60 p-5">
                <p className="text-sm text-muted-foreground">{selectedDefect.assignmentGroup}</p>
                <div className="flex flex-wrap gap-2">
                  <Badge>{selectedDefect.priority}</Badge>
                  <Badge>{selectedDefect.status}</Badge>
                  <Badge>{selectedDefect.resolutionHours}h resolution</Badge>
                </div>
                <p className="text-sm text-slate-300">Similarity is based on the current semantic index and falls back to keyword overlap when embeddings are unavailable.</p>
                <div className="rounded-2xl border border-white/8 bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Summary</p>
                  <p className="mt-2 text-sm text-foreground">{summaryQuery.data?.summary ?? 'Select a result to generate a defect summary.'}</p>
                  <p className="mt-3 text-xs uppercase tracking-[0.2em] text-slate-500">Method: {summaryQuery.data?.method ?? 'pending'}</p>
                  {summaryQuery.data?.actions?.length ? (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {summaryQuery.data.actions.map((action) => (
                        <Badge key={action} className="bg-cyan-400/10 text-cyan-100">
                          {action}
                        </Badge>
                      ))}
                    </div>
                  ) : null}
                </div>
              </div>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-4 p-6">
            <h3 className="text-xl font-semibold text-foreground">Top keywords</h3>
            <div className="flex flex-wrap gap-2">
              {keywordsQuery.data?.keywords?.slice(0, 12).map((keyword) => (
                <Badge key={keyword.keyword} className="bg-slate-800/90 text-slate-100">
                  {keyword.keyword}
                </Badge>
              ))}
              {!keywordsQuery.data?.keywords?.length ? <p className="text-sm text-muted-foreground">No keywords yet.</p> : null}
            </div>

            <div className="space-y-3">
              <h3 className="text-xl font-semibold text-foreground">Cluster overview</h3>
              {clusterQuery.data?.clusters?.map((cluster) => (
                <div key={cluster.cluster_id} className="rounded-2xl border border-slate-700/80 bg-slate-950/60 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium text-foreground">{cluster.cluster_id}</p>
                    <Badge>{cluster.size} defects</Badge>
                  </div>
                  {cluster.sample_titles?.length ? <p className="mt-2 text-sm text-muted-foreground">{cluster.sample_titles.join(' · ')}</p> : null}
                </div>
              ))}
              {!clusterQuery.data?.clusters?.length ? <p className="text-sm text-muted-foreground">Cluster analysis will appear after the dataset is loaded.</p> : null}
            </div>
          </CardContent>
        </Card>
      </div>

      <SimilarDefectsList defects={defects} activeId={selectedDefect?.id} onSelect={(defect) => setSelectedId(defect.id)} />
    </div>
  )
}

function Metric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-3xl border border-slate-700/80 bg-slate-950/60 p-4">
      <p className="text-sm text-slate-300">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-foreground">{value}</p>
      <p className="mt-2 text-xs uppercase tracking-[0.18em] text-slate-500">{detail}</p>
    </div>
  )
}
