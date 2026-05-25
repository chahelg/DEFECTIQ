import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { ProtectedRoute } from '@/components/guards/ProtectedRoute'
import { useAuthStore } from '@/store/authStore'
import { DashboardPage } from '@/pages/DashboardPage'
import { AgeingDefectsPage } from '@/pages/AgeingDefectsPage'
import { DefectExplorerPage } from '@/pages/DefectExplorerPage'
import { LoginPage } from '@/pages/LoginPage'
import { ManagerCommandCenterPage } from '@/pages/ManagerCommandCenterPage'
import { RootCauseAnalysisPage } from '@/pages/RootCauseAnalysisPage'
import { SLARiskCenterPage } from '@/pages/SLARiskCenterPage'
import { UploadPage } from '@/pages/UploadPage'
import { WorkflowIntelligencePage } from '@/pages/WorkflowIntelligencePage'
import { WorkloadIntelligencePage } from '@/pages/WorkloadIntelligencePage'

function RootRedirect() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return <Navigate to={isAuthenticated ? '/command-center' : '/login'} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<RootRedirect />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/command-center" element={<ManagerCommandCenterPage />} />
          <Route path="/sla-risk" element={<SLARiskCenterPage />} />
          <Route path="/workload-intelligence" element={<WorkloadIntelligencePage />} />
          <Route path="/workflow-intelligence" element={<WorkflowIntelligencePage />} />
          <Route path="/root-cause-analysis" element={<RootCauseAnalysisPage />} />
          <Route path="/ageing-defects" element={<AgeingDefectsPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/defects" element={<DefectExplorerPage />} />
          <Route path="/upload" element={<UploadPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}