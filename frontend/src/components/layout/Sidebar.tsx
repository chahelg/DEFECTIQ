import { NavLink } from 'react-router-dom'
import { NAV_ITEMS, APP_NAME } from '@lib/constants'
import { useAppStore } from '@store/useAppStore'
import { cn } from '@lib/utils'
import { Button } from '@components/ui/button'
import { Separator } from '@components/ui/separator'
import { ShieldCheck, PanelLeftClose, PanelLeftOpen } from 'lucide-react'

interface SidebarProps {
  mobile?: boolean
}

export function Sidebar({ mobile = false }: SidebarProps) {
  const collapsed = useAppStore((state) => state.sidebarCollapsed)
  const toggleSidebar = useAppStore((state) => state.toggleSidebar)
  const closeMobileSidebar = useAppStore((state) => state.setMobileSidebarOpen)
  const auth = useAppStore((state) => state.auth)
  const widthClass = mobile ? 'w-full rounded-none' : collapsed ? 'w-[92px]' : 'w-[320px]'

  return (
    <aside
      className={cn(
        'flex h-full flex-col border border-white/10 bg-slate-950/70 p-4 backdrop-blur-2xl',
        mobile ? 'w-full rounded-none' : 'hidden h-[calc(100vh-2rem)] rounded-[2rem] lg:flex',
        widthClass,
      )}
    >
      <div className="flex items-center justify-between gap-3 px-2 py-2">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-violet-500 text-slate-950 shadow-glow">
            <ShieldCheck className="h-6 w-6" />
          </div>
          {!collapsed ? (
            <div>
              <p className="text-sm font-semibold tracking-wide text-foreground">{APP_NAME}</p>
              <p className="text-xs text-muted-foreground">Enterprise command center</p>
            </div>
          ) : null}
        </div>
        {mobile ? (
          <Button variant="ghost" size="icon" onClick={() => closeMobileSidebar(false)} aria-label="Close sidebar">
            <PanelLeftClose className="h-4 w-4" />
          </Button>
        ) : (
          <Button variant="ghost" size="icon" onClick={toggleSidebar} aria-label="Toggle sidebar">
            {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
          </Button>
        )}
      </div>

      <Separator className="my-4 bg-white/10" />

      <nav className="flex-1 space-y-2 overflow-y-auto pr-1 scrollbar-thin">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'group flex items-start gap-3 rounded-2xl border px-3 py-3 transition-all',
                  isActive
                    ? 'border-cyan-400/30 bg-cyan-400/10 text-cyan-100 shadow-glow'
                    : 'border-transparent text-slate-300 hover:border-white/10 hover:bg-white/5 hover:text-white',
                  collapsed ? 'justify-center' : '',
                )
              }
              onClick={() => mobile && closeMobileSidebar(false)}
            >
              <Icon className="mt-0.5 h-5 w-5 shrink-0" />
              {!collapsed ? (
                <div>
                  <p className="text-sm font-medium">{item.label}</p>
                  <p className="mt-1 text-xs leading-5 text-muted-foreground group-hover:text-slate-200">{item.description}</p>
                </div>
              ) : null}
            </NavLink>
          )
        })}
      </nav>

      <div className="mt-4 rounded-[1.75rem] border border-white/10 bg-white/5 p-4">
        {!collapsed ? (
          <>
            <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">Signed in</p>
            <p className="mt-2 text-base font-semibold text-foreground">{auth?.user.fullName ?? 'DefectIQ User'}</p>
            <p className="text-sm text-muted-foreground">{auth?.user.department ?? 'Operations Intelligence'}</p>
          </>
        ) : (
          <div className="flex justify-center text-cyan-300">
            <ShieldCheck className="h-5 w-5" />
          </div>
        )}
      </div>
    </aside>
  )
}