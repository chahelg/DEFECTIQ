import { useQuery } from '@tanstack/react-query'
import { getDashboardSnapshot } from '@api/dashboard'

export function useDashboardData() {
  return useQuery({
    queryKey: ['dashboard-snapshot'],
    queryFn: getDashboardSnapshot,
    staleTime: 30_000,
  })
}