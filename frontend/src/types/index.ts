export type ThemeMode = 'dark' | 'light'
export type UserRole = 'admin' | 'manager' | 'analyst' | 'viewer'
export type DefectPriority = 'Critical' | 'High' | 'Medium' | 'Low'
export type DefectStatus = 'Open' | 'In Progress' | 'Resolved' | 'Closed' | 'Reopened' | 'On Hold'

export interface NavItem {
  label: string
  path: string
  description: string
}

export interface User {
  id: string
  email: string
  username: string
  fullName: string
  role: UserRole
  department: string
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface AuthSession {
  accessToken: string
  refreshToken: string
  expiresAt: string
  user: User
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload extends LoginPayload {
  username: string
  fullName: string
  department: string
}

export interface Defect {
  id: string
  ticketId: string
  ticketNumber: string
  title: string
  description: string
  status: DefectStatus
  priority: DefectPriority
  severity: string
  assignmentGroup: string
  assignedTo: string
  serviceOffering: string
  businessDomain: string
  openedAt: string
  closedAt?: string | null
  slaBreached: boolean
  reassignmentCount: number
  reopenCount: number
  ingestionDate: string
  updatedAt: string
  isAnalyzed: boolean
  similarityScore?: number
  aiConfidence?: number
}

export interface DefectFilters {
  search: string
  status: string[]
  priority: string[]
  assignmentGroup: string[]
  serviceOffering: string[]
  slaBreached: boolean | null
  page: number
  pageSize: number
}

export interface DashboardSummary {
  totalDefects: number
  openDefects: number
  closedDefects: number
  criticalDefects: number
  slaBreachPercentage: number
  avgResolutionHours: number
  reopenRate: number
  mttrHours: number
  predictedBreachCount: number
}

export interface DashboardTrendPoint {
  label: string
  total: number
  open: number
  closed: number
  slaBreached: number
}

export interface PriorityBreakdownPoint {
  name: DefectPriority
  value: number
  color: string
}

export interface AssignmentLoadPoint {
  name: string
  workload: number
  breachRisk: number
}

export interface AgingBucket {
  bucket: string
  count: number
}

export interface AIInsight {
  id: string
  title: string
  summary: string
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  confidence: number
  impact: string
  recommendedAction: string
  source: string
}

export interface SimilarDefect {
  id: string
  ticketNumber: string
  title: string
  similarity: number
  priority: DefectPriority
  status: DefectStatus
  assignmentGroup: string
  resolutionHours: number
}

export interface PredictionSnapshot {
  defectId: string
  slaBreachProbability: number
  slaBreachConfidence: number
  estimatedResolutionHours: number
  recommendedAssignmentGroup: string
  confidenceScore: number
}

export interface PredictionModelPerformance {
  modelName: string
  accuracy: number
  precision: number
  recall: number
  f1Score: number
}

export interface ModelStatusResponse {
  sla?: {
    status: string
    trained_at?: string | null
    metrics?: Record<string, number>
    exists?: boolean
  }
  resolution?: {
    status: string
    trained_at?: string | null
    metrics?: Record<string, number>
    exists?: boolean
  }
  assignment?: {
    status: string
    exists?: boolean
  }
  embeddings_index?: {
    exists: boolean
    count: number
    path: string
  }
}

export interface InsightResponse {
  metrics: {
    total_defects: number
    sla_breaches: number
    average_resolution_hours: number
  }
  summary?: {
    summary?: string
    method?: string
  }
  recommendations?: string[]
  method?: string
  openai?: string
}

export interface ChatApiMessage {
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  intent?: string | null
  created_at?: string | null
}

export interface ChatApiResponse {
  messages: ChatApiMessage[]
}

export interface SemanticSearchResult {
  id: string
  number?: string
  title: string
  description?: string | null
  priority?: DefectPriority
  status?: DefectStatus
  assigned_to?: string | null
  category?: string | null
  score?: number
}

export interface ChatMessage {
  id: string
  conversationId: string
  role: 'user' | 'assistant' | 'system'
  content: string
  createdAt: string
}

export interface ChatPrompt {
  label: string
  prompt: string
}

export interface SettingsFormValues {
  fullName: string
  email: string
  department: string
  theme: ThemeMode
  notificationsEnabled: boolean
  refreshInterval: number
  defaultPageSize: number
}

export interface ApiResponse<T> {
  data: T
  message?: string
  status: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}
