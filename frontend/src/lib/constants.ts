export const API_BASE_URL = '/api/v1'
export const ENABLE_MOCKS = false

export const APP_NAME = 'DefectIQ AI'
export const APP_TAGLINE = 'Operational defect intelligence for local demo and analytics.'

export const DEFAULT_THEME = 'dark'
export const THEME_STORAGE_KEY = 'defectiq-theme'

export const NAV_ITEMS = [
  { label: 'Dashboard', path: '/dashboard', description: 'Live operational overview' },
  { label: 'Defect Explorer', path: '/defects', description: 'Search defect records' },
  { label: 'Upload', path: '/upload', description: 'Bulk import defects' },
]

export const FILTER_PRESETS = {
  statuses: ['Open', 'In Progress', 'Resolved', 'Closed', 'Reopened'],
  priorities: ['Critical', 'High', 'Medium', 'Low'],
}

export const CHART_COLORS = ['#22d3ee', '#38bdf8', '#818cf8', '#c084fc', '#f472b6', '#fb7185']

export const QUICK_ACTIONS = [
  { label: 'Summarize current risk', prompt: 'Summarize the current defect risk posture.' },
  { label: 'Highlight critical items', prompt: 'Highlight critical defects that need attention.' },
]