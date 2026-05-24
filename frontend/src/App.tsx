import { Navigate, Route, Routes } from 'react-router-dom'

import styles from './App.module.css'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AuthCallbackPage } from './pages/AuthCallbackPage'
import { CourseDetailPage } from './pages/CourseDetailPage'
import { DashboardPage } from './pages/DashboardPage'
import { CoursesPage } from './pages/CoursesPage'
import { LoginPage } from './pages/LoginPage'
import { QuizPage } from './pages/QuizPage'
import { QuizResultsPage } from './pages/QuizResultsPage'
import { RegisterPage } from './pages/RegisterPage'
import { useAuthBootstrap } from './store/useAuthStore'


export function App() {
  useAuthBootstrap()

  return (
    <div className={styles.appShell}>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/auth/google/callback" element={<AuthCallbackPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/courses/:courseId" element={<CourseDetailPage />} />
          <Route path="/quiz/:quizId" element={<QuizPage />} />
          <Route path="/quiz/:sessionId/results" element={<QuizResultsPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </div>
  )
}
