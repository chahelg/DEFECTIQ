import { api } from './http'
import { ENABLE_MOCKS } from '@lib/constants'
import { defects as mockDefects } from '@data/mockData'
import type { Defect, DefectFilters, PaginatedResponse, SimilarDefect } from '@types'
import { similarDefects as mockSimilarDefects } from '@data/mockData'

function matches(values: string[], candidate: string) {
  return values.length === 0 || values.includes(candidate)
}

function filterDefects(source: Defect[], filters: DefectFilters): Defect[] {
  const query = filters.search.trim().toLowerCase()

  return source.filter((defect) => {
    const textMatches =
      !query ||
      [defect.ticketNumber, defect.title, defect.description, defect.assignmentGroup, defect.serviceOffering]
        .join(' ')
        .toLowerCase()
        .includes(query)

    const statusMatches = matches(filters.status, defect.status)
    const priorityMatches = matches(filters.priority, defect.priority)
    const assignmentMatches = matches(filters.assignmentGroup, defect.assignmentGroup)
    const serviceMatches = matches(filters.serviceOffering, defect.serviceOffering)
    const slaMatches =
      filters.slaBreached === null || filters.slaBreached === defect.slaBreached

    return textMatches && statusMatches && priorityMatches && assignmentMatches && serviceMatches && slaMatches
  })
}

export async function getDefects(filters: DefectFilters): Promise<PaginatedResponse<Defect>> {
  try {
    const response = await api.get<PaginatedResponse<Defect>>('/defects', { params: filters })
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }

    const filtered = filterDefects(mockDefects, filters)
    const pageSize = filters.pageSize || 8
    const page = filters.page || 1
    const total = filtered.length
    const totalPages = Math.max(1, Math.ceil(total / pageSize))
    const start = (page - 1) * pageSize

    return {
      items: filtered.slice(start, start + pageSize),
      total,
      page,
      pageSize,
      totalPages,
    }
  }
}

export async function getDefectById(defectId: string): Promise<Defect | null> {
  try {
    const response = await api.get<Defect>(`/defects/${defectId}`)
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    return mockDefects.find((item) => item.id === defectId) ?? null
  }
}

export async function getSimilarDefects(defectId: string): Promise<SimilarDefect[]> {
  try {
    const response = await api.get<SimilarDefect[]>(`/defects/${defectId}/similar`)
    return response.data
  } catch (error) {
    if (!ENABLE_MOCKS) {
      throw error
    }
    return mockSimilarDefects
  }
}

export async function exportDefects(filters: DefectFilters): Promise<Defect[]> {
  const result = await getDefects({ ...filters, page: 1, pageSize: 1000 })
  return result.items
}