import { api } from './http'
import { ENABLE_MOCKS } from '@lib/constants'
import {
  agingBuckets,
  assignmentLoad,
  dashboardSummary,
  dashboardTrendData,
  priorityBreakdown,
} from '@data/mockData'
import type {
  AgingBucket,
  AssignmentLoadPoint,
  DashboardSummary,
  DashboardTrendPoint,
  PriorityBreakdownPoint,
} from '@types'

export interface DashboardSnapshot {
  summary: DashboardSummary
  trend: DashboardTrendPoint[]
  priorityBreakdown: PriorityBreakdownPoint[]
  assignmentLoad: AssignmentLoadPoint[]
  agingBuckets: AgingBucket[]
}

export async function getDashboardSnapshot(): Promise<DashboardSnapshot> {
  try {
    const response = await api.get<DashboardSnapshot>('/dashboard/summary')
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    return {
      summary: dashboardSummary,
      trend: dashboardTrendData,
      priorityBreakdown,
      assignmentLoad,
      agingBuckets,
    }
  }
}