// frontend/src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { Sidebar } from './components/Sidebar'
import ResearchPage from './pages/ResearchPage'
import PDFPage from './pages/PDFPage'
import HistoryPage from './pages/HistoryPage'
import SettingsPage from './pages/SettingsPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-surface-900 text-gray-100">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-6 py-8">
            <Routes>
              <Route path="/"         element={<ResearchPage />} />
              <Route path="/pdf"      element={<PDFPage />} />
              <Route path="/history"  element={<HistoryPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </main>
      </div>
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: '#1a1a2e',
            color: '#e5e7eb',
            border: '1px solid rgba(16,185,129,0.2)',
          },
          success: { iconTheme: { primary: '#10b981', secondary: '#1a1a2e' } },
          error:   { iconTheme: { primary: '#ef4444', secondary: '#1a1a2e' } },
        }}
      />
    </BrowserRouter>
  )
}
