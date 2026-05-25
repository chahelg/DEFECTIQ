import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { AuthSession, DefectFilters, SettingsFormValues, ThemeMode } from '@types'
import { DEFAULT_THEME, THEME_STORAGE_KEY } from '@lib/constants'

const defaultDefectFilters: DefectFilters = {
  search: '',
  status: [],
  priority: [],
  assignmentGroup: [],
  serviceOffering: [],
  slaBreached: null,
  page: 1,
  pageSize: 8,
}

const defaultSettings: SettingsFormValues = {
  fullName: 'Ava Morgan',
  email: 'analyst@defectiq.ai',
  department: 'Operations Intelligence',
  theme: DEFAULT_THEME,
  notificationsEnabled: true,
  refreshInterval: 30,
  defaultPageSize: 8,
}

interface AppState {
  auth: AuthSession | null
  theme: ThemeMode
  sidebarCollapsed: boolean
  mobileSidebarOpen: boolean
  defectFilters: DefectFilters
  settings: SettingsFormValues
  setAuth: (session: AuthSession | null) => void
  clearAuth: () => void
  setTheme: (theme: ThemeMode) => void
  toggleTheme: () => void
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  setMobileSidebarOpen: (open: boolean) => void
  setDefectFilters: (filters: Partial<DefectFilters>) => void
  resetDefectFilters: () => void
  setSettings: (settings: Partial<SettingsFormValues>) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      auth: null,
      theme: DEFAULT_THEME,
      sidebarCollapsed: false,
      mobileSidebarOpen: false,
      defectFilters: defaultDefectFilters,
      settings: defaultSettings,
      setAuth: (session) => set({ auth: session }),
      clearAuth: () => set({ auth: null }),
      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set({ theme: get().theme === 'dark' ? 'light' : 'dark' }),
      toggleSidebar: () => set({ sidebarCollapsed: !get().sidebarCollapsed }),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      setMobileSidebarOpen: (open) => set({ mobileSidebarOpen: open }),
      setDefectFilters: (filters) =>
        set({ defectFilters: { ...get().defectFilters, ...filters } }),
      resetDefectFilters: () => set({ defectFilters: defaultDefectFilters }),
      setSettings: (settings) => set({ settings: { ...get().settings, ...settings } }),
    }),
    {
      name: THEME_STORAGE_KEY,
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        auth: state.auth,
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
        mobileSidebarOpen: state.mobileSidebarOpen,
        settings: state.settings,
        defectFilters: state.defectFilters,
      }),
    },
  ),
)

export { defaultDefectFilters, defaultSettings }