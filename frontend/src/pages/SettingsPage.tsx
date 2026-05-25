import { useEffect } from 'react'
import { PageHeader } from '@components/common/PageHeader'
import { Button } from '@components/ui/button'
import { Card, CardContent } from '@components/ui/card'
import { Input } from '@components/ui/input'
import { Select } from '@components/ui/select'
import { Switch } from '@components/ui/switch'
import { useAppStore } from '@store/useAppStore'

export function SettingsPage() {
  const settings = useAppStore((state) => state.settings)
  const setSettings = useAppStore((state) => state.setSettings)
  const theme = useAppStore((state) => state.theme)
  const setTheme = useAppStore((state) => state.setTheme)

  useEffect(() => {
    if (settings.theme !== theme) {
      setTheme(settings.theme)
    }
  }, [settings.theme, setTheme, theme])

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Workspace preferences"
        title="Settings"
        description="Personalize your DefectIQ workspace, default filters, notifications, and display settings."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardContent className="space-y-4 p-6">
            <h3 className="text-xl font-semibold text-foreground">Profile</h3>
            <Input value={settings.fullName} onChange={(event) => setSettings({ fullName: event.target.value })} placeholder="Full name" />
            <Input value={settings.email} onChange={(event) => setSettings({ email: event.target.value })} placeholder="Email address" />
            <Input value={settings.department} onChange={(event) => setSettings({ department: event.target.value })} placeholder="Department" />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-4 p-6">
            <h3 className="text-xl font-semibold text-foreground">Experience</h3>
            <Select value={settings.theme} onChange={(event) => setSettings({ theme: event.target.value as 'dark' | 'light' })}>
              <option value="dark">Dark</option>
              <option value="light">Light</option>
            </Select>
            <div className="flex items-center justify-between rounded-2xl border border-white/10 px-4 py-3">
              <div>
                <p className="font-medium text-foreground">Notifications</p>
                <p className="text-xs text-muted-foreground">Receive alerts for new breaches and AI insights</p>
              </div>
              <Switch checked={settings.notificationsEnabled} onChange={(event) => setSettings({ notificationsEnabled: event.target.checked })} />
            </div>
            <Input
              type="number"
              value={settings.refreshInterval}
              onChange={(event) => setSettings({ refreshInterval: Number(event.target.value) })}
              placeholder="Refresh interval"
            />
            <Input
              type="number"
              value={settings.defaultPageSize}
              onChange={(event) => setSettings({ defaultPageSize: Number(event.target.value) })}
              placeholder="Default page size"
            />
            <Button onClick={() => setTheme(settings.theme)}>Save preferences</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}