import { Routes, Route, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { AuthProvider, useAuth } from './context/AuthContext'
import Landing from './pages/Landing'
import Auth    from './pages/Auth'
import Session from './pages/Session'
import History from './pages/History'

function Guard({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/auth" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/"        element={<Landing />} />
          <Route path="/auth"    element={<Auth />} />
          <Route path="/session" element={<Guard><Session /></Guard>} />
          <Route path="/history" element={<Guard><History /></Guard>} />
          <Route path="*"        element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
    </AuthProvider>
  )
}
