export async function postMessage(message: string){
  const res = await fetch('/api/v1/chat/message', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({message})
  })
  return res.json()
}

export async function streamMessage(message: string, onChunk: (chunk: any)=>void){
  const res = await fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({message})
  })

  if (!res.body) return
  const reader = res.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let done = false
  let buffer = ''
  while(!done){
    const result = await reader.read()
    done = !!result.done
    buffer += decoder.decode(result.value || new Uint8Array(), {stream: !done})
    let lines = buffer.split('\n')
    buffer = lines.pop() || ''
    for(const line of lines){
      if(!line.startsWith('data:')) continue
      const payload = line.replace(/^data:\s*/, '')
      try{
        const obj = JSON.parse(payload)
        onChunk(obj)
      }catch(e){
        // ignore
      }
    }
  }
}
import { api } from './http'
import { ENABLE_MOCKS } from '@lib/constants'
import {
  aiInsights,
  chatMessages,
  predictionPerformance,
  predictionSnapshots,
  suggestedPrompts,
  similarDefects,
} from '@data/mockData'
import type {
  AIInsight,
  ChatMessage,
  PredictionModelPerformance,
  PredictionSnapshot,
  SimilarDefect,
} from '@types'

export async function getAiInsights(): Promise<AIInsight[]> {
  try {
    const response = await api.get<AIInsight[]>('/ai/insights')
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    return aiInsights
  }
}

export async function getSimilarDefectCases(): Promise<SimilarDefect[]> {
  try {
    const response = await api.get<SimilarDefect[]>('/ai/similar-defects')
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    return similarDefects
  }
}

export async function getPredictionSnapshots(): Promise<PredictionSnapshot[]> {
  try {
    const response = await api.get<PredictionSnapshot[]>('/predictions')
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    return predictionSnapshots
  }
}

export async function getModelPerformance(): Promise<PredictionModelPerformance[]> {
  try {
    const response = await api.get<PredictionModelPerformance[]>('/predictions/performance')
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    return predictionPerformance
  }
}

export async function getChatHistory(): Promise<ChatMessage[]> {
  try {
    const response = await api.get<ChatMessage[]>('/chat/history')
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    return chatMessages
  }
}

export async function sendChatMessage(message: string): Promise<ChatMessage> {
  try {
    const response = await api.post<ChatMessage>('/chat/message', { message })
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    const lowerMessage = message.toLowerCase()
    const responseText = lowerMessage.includes('sla')
      ? 'SLA risk is concentrated in the payments queue and should be addressed immediately.'
      : lowerMessage.includes('assign')
        ? 'Payments SRE and Identity Platform should be prioritized based on current volume.'
        : 'I analyzed the recent defect trends and highlighted the highest-impact operational risks.'

    return {
      id: `msg-${Date.now()}`,
      conversationId: 'conv-001',
      role: 'assistant',
      content: responseText,
      createdAt: new Date().toISOString(),
    }
  }
}

export { suggestedPrompts }