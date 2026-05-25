import { useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@components/common/PageHeader'
import { AssistantPanel } from '@components/ai/AssistantPanel'
import { Badge } from '@components/ui/badge'
import { Card, CardContent } from '@components/ui/card'
import { api } from '@/services/api'
import type { ChatApiResponse, ChatMessage } from '@types'

export function ChatAssistantPage() {
  const queryClient = useQueryClient()
  const chatQuery = useQuery({
    queryKey: ['chat', 'history'],
    queryFn: async () => (await api.get<ChatApiResponse>('/chat/history')).data,
  })
  const suggestionsQuery = useQuery({
    queryKey: ['chat', 'suggestions'],
    queryFn: async () => (await api.get<{ suggestions: string[] }>('/chat/suggestions')).data,
  })
  const sendMutation = useMutation({
    mutationFn: async (message: string) => (await api.post('/chat/message', { message })).data,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['chat', 'history'] })
    },
  })
  const history: ChatMessage[] = useMemo(
    () =>
      (chatQuery.data?.messages ?? []).map((item, index) => ({
        id: `${item.conversation_id}-${item.role}-${index}`,
        conversationId: item.conversation_id,
        role: item.role,
        content: item.content,
        createdAt: item.created_at ?? new Date().toISOString(),
      })),
    [chatQuery.data?.messages],
  )

  const prompts = useMemo(
    () => (suggestionsQuery.data?.suggestions ?? ['Summarize the current defect posture.', 'Show the highest risk tickets.']).map((prompt) => ({ label: prompt, prompt })),
    [suggestionsQuery.data?.suggestions],
  )

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="AI copilot"
        title="Chat Assistant"
        description="Talk to DefectIQ AI about defects, trends, assignments, and operational risk in plain language."
      />

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <AssistantPanel
          title="DefectIQ AI Copilot"
          description="Ask questions, request summaries, and generate triage actions."
          messages={history}
          prompts={prompts}
          onSend={(message) => sendMutation.mutate(message)}
        />

        <Card>
          <CardContent className="space-y-4 p-6">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Conversation</p>
                <h3 className="mt-2 text-2xl font-semibold text-foreground">Live context</h3>
              </div>
              <Badge>{history.length} messages</Badge>
            </div>

            <div className="space-y-3">
              {history.slice(-5).map((message) => (
                <div key={message.id} className={`rounded-2xl border p-4 text-sm ${message.role === 'assistant' ? 'border-cyan-300/30 bg-cyan-400/10 text-cyan-50' : 'border-slate-700/80 bg-slate-950/60 text-foreground'}`}>
                  <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">{message.role}</p>
                  <p className="mt-2 leading-6">{message.content}</p>
                </div>
              ))}
              {!history.length ? <p className="text-sm text-muted-foreground">No messages yet. Ask the assistant about risk, trends, or assignments.</p> : null}
            </div>

            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Suggested prompts</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {prompts.map((prompt) => (
                  <Badge key={prompt.prompt} className="bg-slate-800/90 text-slate-100">
                    {prompt.label}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
