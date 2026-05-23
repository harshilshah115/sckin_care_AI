import { Routes, Route, useLocation } from 'react-router-dom'
import { useTheme } from './context/ThemeContext'
import Navbar from './components/Navbar/Navbar'
import ProtectedRoute from './components/ProtectedRoute/ProtectedRoute'
import NotFound from './pages/NotFound/NotFound'
import LandingPage from './pages/LandingPage/LandingPage'
import Login from './pages/Auth/Login'
import Register from './pages/Auth/Register'
import Dashboard from './pages/Dashboard/Dashboard'
import SkinScan from './pages/SkinScan/SkinScan'
import AskQuestion from './pages/AskQuestion/AskQuestion'
import History from './pages/History/History'
import Profile from './pages/Profile/Profile'
import Products from './pages/Products/Products'
import SavedItems from './pages/SavedItems/SavedItems'
import Routine from './pages/Routine/Routine'
import Progress from './pages/Progress/Progress'
import Settings from './pages/Settings/Settings'
import Onboarding from './pages/Onboarding/Onboarding'
import './App.css'

function App() {
  const { theme } = useTheme()
  const location = useLocation()
  
  // Pages that don't show the navbar (dashboard-style pages with sidebar)
  const noNavbarRoutes = ['/login', '/register', '/dashboard', '/scan', '/ask', '/routine', '/progress', '/products', '/saved', '/history', '/profile', '/settings', '/onboarding']
  const showNavbar = !noNavbarRoutes.some(route =>
    location.pathname === route || location.pathname.startsWith(route + '/')
  )

  return (
    <div className={`app ${theme}`}>
      {showNavbar && <Navbar />}
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/onboarding" element={<Onboarding />} />
        
        {/* Protected Routes */}
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/scan" element={<ProtectedRoute><SkinScan /></ProtectedRoute>} />
        <Route path="/scan/:id" element={<ProtectedRoute><SkinScan /></ProtectedRoute>} />
        <Route path="/ask" element={<ProtectedRoute><AskQuestion /></ProtectedRoute>} />
        <Route path="/routine" element={<ProtectedRoute><Routine /></ProtectedRoute>} />
        <Route path="/progress" element={<ProtectedRoute><Progress /></ProtectedRoute>} />
        <Route path="/products" element={<ProtectedRoute><Products /></ProtectedRoute>} />
        <Route path="/saved" element={<ProtectedRoute><SavedItems /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />

        {/* 404 Catch-all */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  )
}

export default App
