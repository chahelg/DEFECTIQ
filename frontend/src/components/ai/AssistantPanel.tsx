import { useState } from 'react'
import { Button } from '@components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@components/ui/card'
import { Input } from '@components/ui/input'
import { Badge } from '@components/ui/badge'
import type { ChatMessage, ChatPrompt } from '@types'
import { Bot, Send, Sparkles } from 'lucide-react'

interface AssistantPanelProps {
  title: string
  description: string
  messages: ChatMessage[]
  prompts: ChatPrompt[]
  onSend: (message: string) => void
  compact?: boolean
}

export function AssistantPanel({ title, description, messages, prompts, onSend, compact = false }: AssistantPanelProps) {
  const [draft, setDraft] = useState('')

  const submit = () => {
    if (!draft.trim()) return
    onSend(draft.trim())
    setDraft('')
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 p-3 text-cyan-300">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <CardTitle>{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className={compact ? 'space-y-3' : 'space-y-4'}>
          {messages.slice(-4).map((message) => (
            <div
              key={message.id}
              className={`rounded-2xl border px-4 py-3 text-sm ${
                message.role === 'assistant'
                  ? 'border-cyan-400/20 bg-cyan-400/10 text-cyan-50'
                  : 'border-white/10 bg-white/5 text-foreground'
              }`}
            >
              <div className="mb-1 flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-muted-foreground">
                <Sparkles className="h-3.5 w-3.5" />
                <span>{message.role}</span>
              </div>
              <p>{message.content}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-2 md:grid-cols-2">
          {prompts.slice(0, compact ? 2 : 4).map((prompt) => (
            <button
              key={prompt.prompt}
              type="button"
              onClick={() => onSend(prompt.prompt)}
              className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-left text-sm text-foreground transition hover:bg-white/10"
            >
              <Badge className="mb-2 border-cyan-400/20 bg-cyan-400/10 text-cyan-200">Prompt</Badge>
              <p>{prompt.label}</p>
            </button>
          ))}
        </div>

        <div className="flex gap-3">
          <Input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Ask DefectIQ AI..." />
          <Button onClick={submit} size="icon" aria-label="Send message">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default AssistantPanel