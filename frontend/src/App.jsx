import { Routes, Route, useLocation } from 'react-router-dom'
import { useTheme } from './context/ThemeContext'
import Navbar from './components/Navbar/Navbar'
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
import './App.css'

function App() {
  const { theme } = useTheme()
  const location = useLocation()
  
  // Pages that don't show the navbar (dashboard-style pages with sidebar)
  const noNavbarRoutes = ['/login', '/register', '/dashboard', '/scan', '/ask', '/routine', '/progress', '/products', '/saved', '/history', '/profile', '/settings']
  const showNavbar = !noNavbarRoutes.some(route => location.pathname.startsWith(route))

  return (
    <div className={`app ${theme}`}>
      {showNavbar && <Navbar />}
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Protected Routes (will add auth guard later) */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/scan" element={<SkinScan />} />
        <Route path="/scan/:id" element={<SkinScan />} />
        <Route path="/ask" element={<AskQuestion />} />
        <Route path="/routine" element={<Routine />} />
        <Route path="/progress" element={<Progress />} />
        <Route path="/products" element={<Products />} />
        <Route path="/saved" element={<SavedItems />} />
        <Route path="/history" element={<History />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </div>
  )
}

export default App
