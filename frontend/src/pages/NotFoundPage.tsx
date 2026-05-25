import { Link } from 'react-router-dom'
import { Button } from '@components/ui/button'

export function NotFoundPage() {
  return (
    <div className="page-shell flex min-h-screen items-center justify-center">
      <div className="glass-card max-w-xl p-10 text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-300">404</p>
        <h1 className="mt-4 text-4xl font-semibold text-foreground">Page not found</h1>
        <p className="mt-3 text-muted-foreground">The requested route does not exist in this DefectIQ workspace.</p>
        <div className="mt-6 flex justify-center">
          <Button>
            <Link to="/dashboard">Return to dashboard</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}