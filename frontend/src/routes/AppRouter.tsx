import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '@components/layout/AppShell'
import { ProtectedRoute } from '@components/guards/ProtectedRoute'
import { LoginPage } from '@pages/auth/LoginPage'
import { RegisterPage } from '@pages/auth/RegisterPage'
import { DashboardPage } from '@pages/DashboardPage'
import { DefectExplorerPage } from '@pages/DefectExplorerPage'
import { AIInsightsPage } from '@pages/AIInsightsPage'
import { SimilarDefectsPage } from '@pages/SimilarDefectsPage'
import { PredictionsPage } from '@pages/PredictionsPage'
import { ChatAssistantPage } from '@pages/ChatAssistantPage'
import { SettingsPage } from '@pages/SettingsPage'
import { NotFoundPage } from '@pages/NotFoundPage'

export function AppRouter() {
  return (
    <Routes>
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/defects" element={<DefectExplorerPage />} />
          <Route path="/ai-insights" element={<AIInsightsPage />} />
          <Route path="/similar-defects" element={<SimilarDefectsPage />} />
          <Route path="/predictions" element={<PredictionsPage />} />
          <Route path="/chat" element={<ChatAssistantPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}