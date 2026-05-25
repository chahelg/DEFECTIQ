import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { ProtectedRoute } from '@/components/guards/ProtectedRoute'
import { useAuthStore } from '@/store/authStore'
import { DashboardPage } from '@/pages/DashboardPage'
import { AIInsightsPage } from '@/pages/AIInsightsPage'
import { ChatAssistantPage } from '@/pages/ChatAssistantPage'
import { DefectExplorerPage } from '@/pages/DefectExplorerPage'
import { LoginPage } from '@/pages/LoginPage'
import { PredictionsPage } from '@/pages/PredictionsPage'
import { SimilarDefectsPage } from '@/pages/SimilarDefectsPage'
import { UploadPage } from '@/pages/UploadPage'

function RootRedirect() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return <Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<RootRedirect />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/defects" element={<DefectExplorerPage />} />
          <Route path="/predictions" element={<PredictionsPage />} />
          <Route path="/nlp" element={<SimilarDefectsPage />} />
          <Route path="/insights" element={<AIInsightsPage />} />
          <Route path="/chat" element={<ChatAssistantPage />} />
          <Route path="/upload" element={<UploadPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}