import { useMutation, useQuery } from '@tanstack/react-query'
import {
  getAiInsights,
  getChatHistory,
  getModelPerformance,
  getPredictionSnapshots,
  getSimilarDefectCases,
  sendChatMessage,
} from '@api/ai'

export function useAiInsights() {
  return useQuery({
    queryKey: ['ai-insights'],
    queryFn: getAiInsights,
    staleTime: 30_000,
  })
}

export function useSimilarDefectsInsights() {
  return useQuery({
    queryKey: ['ai-similar-defects'],
    queryFn: getSimilarDefectCases,
    staleTime: 45_000,
  })
}

export function usePredictionSnapshots() {
  return useQuery({
    queryKey: ['prediction-snapshots'],
    queryFn: getPredictionSnapshots,
    staleTime: 30_000,
  })
}

export function useModelPerformance() {
  return useQuery({
    queryKey: ['model-performance'],
    queryFn: getModelPerformance,
    staleTime: 60_000,
  })
}

export function useChatHistory() {
  return useQuery({
    queryKey: ['chat-history'],
    queryFn: getChatHistory,
    staleTime: 10_000,
  })
}

export function useSendChatMessage() {
  return useMutation({
    mutationFn: sendChatMessage,
  })
}