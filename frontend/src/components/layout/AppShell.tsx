import { Outlet } from 'react-router-dom'
import { useAppStore } from '@store/useAppStore'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'

export function AppShell() {
  const mobileSidebarOpen = useAppStore((state) => state.mobileSidebarOpen)
  const setMobileSidebarOpen = useAppStore((state) => state.setMobileSidebarOpen)

  return (
    <div className="page-shell">
      {mobileSidebarOpen ? (
        <div className="fixed inset-0 z-40 bg-slate-950/70 backdrop-blur-sm lg:hidden" onClick={() => setMobileSidebarOpen(false)}>
          <div className="absolute inset-y-0 left-0 w-[88vw] max-w-sm" onClick={(event) => event.stopPropagation()}>
            <Sidebar mobile />
          </div>
        </div>
      ) : null}
      <div className="grid gap-4 lg:grid-cols-[auto_minmax(0,1fr)]">
        <Sidebar />
        <div className="min-w-0">
          <Topbar />
          <main className="enter-stage min-h-[calc(100vh-8rem)] rounded-[2rem] border border-white/10 bg-slate-950/35 p-4 backdrop-blur-2xl lg:p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}