import { ReactNode } from 'react'
import { ShieldCheck, Sparkles } from 'lucide-react'
import { Card, CardContent } from '@components/ui/card'
import { APP_NAME, APP_TAGLINE } from '@lib/constants'

interface AuthLayoutProps {
  title: string
  subtitle: string
  children: ReactNode
}

export function AuthLayout({ title, subtitle, children }: AuthLayoutProps) {
  return (
    <div className="page-shell flex min-h-screen items-center justify-center">
      <div className="grid w-full gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="glass-card relative overflow-hidden p-8 lg:p-10">
          <div className="absolute inset-0 bg-grid-glow opacity-90" />
          <div className="relative max-w-2xl">
            <div className="inline-flex items-center gap-3 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-200">
              <Sparkles className="h-4 w-4" />
              <span>{APP_NAME}</span>
            </div>
            <h1 className="mt-8 text-5xl font-semibold tracking-tight text-foreground lg:text-7xl">{APP_TAGLINE}</h1>
            <p className="mt-6 max-w-xl text-base leading-8 text-muted-foreground lg:text-lg">
              Premium analytics, predictive signals, and AI-assisted triage for enterprise defect operations.
            </p>

            <div className="mt-10 grid gap-4 md:grid-cols-2">
              {[
                'Secure JWT-based authentication',
                'Enterprise-grade analytics workspace',
                'AI insights and defect similarity search',
                'Responsive glassmorphism interface',
              ].map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-foreground">
                  <ShieldCheck className="mb-3 h-5 w-5 text-cyan-300" />
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>

        <Card className="flex items-center justify-center p-4">
          <CardContent className="w-full max-w-md p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-cyan-300">{APP_NAME}</p>
            <h2 className="mt-3 text-3xl font-semibold text-foreground">{title}</h2>
            <p className="mt-2 text-sm text-muted-foreground">{subtitle}</p>
            <div className="mt-8">{children}</div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}