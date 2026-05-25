import { useLocation } from 'react-router-dom'
import { MoonStar, SunMedium, Bell, Search, Menu } from 'lucide-react'
import { NAV_ITEMS } from '@lib/constants'
import { useAppStore } from '@store/useAppStore'
import { Button } from '@components/ui/button'
import { Input } from '@components/ui/input'

export function Topbar() {
  const location = useLocation()
  const theme = useAppStore((state) => state.theme)
  const toggleTheme = useAppStore((state) => state.toggleTheme)
  const setMobileSidebarOpen = useAppStore((state) => state.setMobileSidebarOpen)

  const currentPage = NAV_ITEMS.find((item) => location.pathname.startsWith(item.path))

  return (
    <header className="glass-card mb-4 flex items-center justify-between gap-4 rounded-[2rem] px-4 py-3 lg:px-6">
      <div className="min-w-0">
        <p className="text-xs uppercase tracking-[0.26em] text-cyan-300">DefectIQ AI</p>
        <h2 className="truncate text-lg font-semibold text-foreground">{currentPage?.label ?? 'Workspace'}</h2>
      </div>

      <div className="hidden flex-1 items-center gap-3 lg:flex lg:max-w-xl">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input className="pl-11" placeholder="Global search across defects, insights, and predictions" />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="outline" size="icon" className="lg:hidden" onClick={() => setMobileSidebarOpen(true)} aria-label="Open menu">
          <Menu className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
          {theme === 'dark' ? <SunMedium className="h-4 w-4" /> : <MoonStar className="h-4 w-4" />}
        </Button>
        <Button variant="outline" size="icon" aria-label="Notifications">
          <Bell className="h-4 w-4" />
        </Button>
      </div>
    </header>
  )
}