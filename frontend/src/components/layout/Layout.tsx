import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { BrainCircuit, LayoutDashboard, MessageSquare, Menu, LogOut, Search, Sparkles, Upload, X } from 'lucide-react'
import clsx from 'clsx'
import { useAuthStore } from '@/store/authStore'

const navItems = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Defect Explorer', to: '/defects', icon: Search },
  { label: 'Predictions', to: '/predictions', icon: BrainCircuit },
  { label: 'NLP Intelligence', to: '/nlp', icon: Sparkles },
  { label: 'Insights', to: '/insights', icon: Sparkles },
  { label: 'Chat Assistant', to: '/chat', icon: MessageSquare },
  { label: 'Upload', to: '/upload', icon: Upload },
]

export function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-[1800px]">
        <aside
          className={clsx(
            'fixed inset-y-0 left-0 z-40 w-72 border-r border-white/10 bg-slate-950/95 px-5 py-6 backdrop-blur-xl transition-transform duration-200 lg:static lg:translate-x-0',
            mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
          )}
        >
          <div className="flex items-center justify-between gap-3 lg:justify-start">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-cyan-300/80">DefectIQ AI</p>
              <h1 className="mt-1 text-2xl font-semibold text-white">Control Center</h1>
            </div>
            <button
              className="rounded-xl border border-white/10 p-2 text-slate-200 lg:hidden"
              onClick={() => setMobileOpen(false)}
              type="button"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <nav className="mt-10 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  className={({ isActive }) =>
                    clsx(
                      'flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition',
                      isActive ? 'bg-cyan-400/15 text-cyan-200 ring-1 ring-cyan-300/30' : 'text-slate-300 hover:bg-white/5 hover:text-white',
                    )
                  }
                  to={item.to}
                  onClick={() => setMobileOpen(false)}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </NavLink>
              )
            })}
          </nav>
        </aside>

        {mobileOpen ? (
          <button
            aria-label="Close sidebar overlay"
            className="fixed inset-0 z-30 bg-slate-950/70 lg:hidden"
            onClick={() => setMobileOpen(false)}
            type="button"
          />
        ) : null}

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
            <div className="flex items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
              <button
                className="rounded-xl border border-white/10 p-2 text-slate-100 lg:hidden"
                onClick={() => setMobileOpen(true)}
                type="button"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div className="min-w-0">
                <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Operational Analytics</p>
                <h2 className="truncate text-lg font-semibold text-white">DefectIQ AI</h2>
              </div>
              <button
                className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-slate-100 hover:bg-white/10"
                onClick={handleLogout}
                type="button"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
            </div>
          </header>

          <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}