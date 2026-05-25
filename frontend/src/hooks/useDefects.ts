import { useQuery } from '@tanstack/react-query'
import { getDefects, getDefectById, getSimilarDefects } from '@api/defects'
import type { DefectFilters } from '@types'

export function useDefects(filters: DefectFilters) {
  return useQuery({
    queryKey: ['defects', filters],
    queryFn: () => getDefects(filters),
    staleTime: 15_000,
  })
}

export function useDefect(defectId: string) {
  return useQuery({
    queryKey: ['defect', defectId],
    queryFn: () => getDefectById(defectId),
    enabled: Boolean(defectId),
  })
}

export function useSimilarDefects(defectId: string) {
  return useQuery({
    queryKey: ['similar-defects', defectId],
    queryFn: () => getSimilarDefects(defectId),
    enabled: Boolean(defectId),
    staleTime: 60_000,
  })
}