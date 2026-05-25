export interface AuthUser {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string | null
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: AuthUser
}

export interface AuthSession {
  token: string
  user: AuthUser
}

export interface KpiResponse {
  total_defects: number
  open_defects: number
  closed_defects: number
  sla_breached_count: number
  avg_resolution_hours: number
  critical_count: number
  reopen_rate: number
  sla_compliance_pct: number
}

export interface TrendPoint {
  week: string
  count: number
}

export interface CountPoint {
  name: string
  value: number
}

export interface DefectRecord {
  id: string
  number: string
  title: string
  description: string | null
  priority: string
  status: string
  category: string
  assigned_to: string | null
  opened_at: string
  resolved_at: string | null
  sla_due: string | null
  is_sla_breached: boolean
  reopen_count: number
  created_at: string
  updated_at: string
  is_deleted: boolean
}

export interface DefectListResponse {
  items: DefectRecord[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface UploadResponse {
  rows_inserted: number
  rows_failed: number
  column_mapping_used: Record<string, string>
  errors: Array<{ row: number; error: string }>
}