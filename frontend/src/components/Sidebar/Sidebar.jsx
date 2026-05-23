import { NavLink, useNavigate } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'
import { useAuth } from '../../context/AuthContext'
import './Sidebar.css'

function Sidebar({ isOpen, onClose }) {
  const { theme, toggleTheme } = useTheme()
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const getUserName = () => {
    if (!user) return 'User'
    return user.name || (user.email ? user.email.split('@')[0] : 'User')
  }

  const getUserRole = () => {
    if (!user) return 'Member'
    return user.skin_type ? `${user.skin_type} skin` : 'Member'
  }

  const navItems = [
    { path: '/dashboard', icon: 'dashboard', label: 'Dashboard' },
    { path: '/scan', icon: 'clinical_notes', label: 'AI Analysis' },
    { path: '/ask', icon: 'forum', label: 'Chat Concierge' },
    { path: '/routine', icon: 'calendar_today', label: 'Routine Planner' },
    { path: '/progress', icon: 'monitoring', label: 'Progress Tracker' },
    { path: '/products', icon: 'science', label: 'Product Lab' },
    { path: '/saved', icon: 'bookmark', label: 'Saved Items' },
    { path: '/history', icon: 'history', label: 'History' },
  ]

  const bottomNavItems = [
    { path: '/profile', icon: 'person', label: 'Profile' },
    { path: '/settings', icon: 'settings', label: 'Settings' },
  ]

  return (
    <>
      {/* Mobile Overlay */}
      <div 
        className={`sidebar-overlay ${isOpen ? 'active' : ''}`}
        onClick={onClose}
      />

      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-inner">
          {/* Logo */}
          <div className="sidebar-header">
            <span className="sidebar-logo">
              {theme === 'dark' ? 'Clinical Portal' : 'Aura Portal'}
            </span>
          </div>

          {/* User Profile */}
          <div className="sidebar-user">
            <div className="user-avatar">
              {user?.avatar ? (
                <img src={user.avatar} alt="User avatar" />
              ) : (
                <div className="avatar-placeholder">
                  {getUserName().charAt(0).toUpperCase()}
                </div>
              )}
            </div>
            <div className="user-info">
              <span className="user-name">{getUserName()}</span>
              <span className="user-role">{getUserRole()}</span>
            </div>
          </div>

          {/* Main Navigation */}
          <nav className="sidebar-nav">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => 
                  `sidebar-link ${isActive ? 'active' : ''}`
                }
                onClick={onClose}
              >
                <span className="material-symbols-outlined">{item.icon}</span>
                <span className="link-label">{item.label}</span>
              </NavLink>
            ))}
          </nav>

          {/* Bottom Section */}
          <div className="sidebar-bottom">
            {/* Theme Toggle */}
            <button className="sidebar-link theme-btn" onClick={toggleTheme}>
              <span className="material-symbols-outlined">
                {theme === 'dark' ? 'light_mode' : 'dark_mode'}
              </span>
              <span className="link-label">
                {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </span>
            </button>

            {/* Bottom Nav Items */}
            {bottomNavItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => 
                  `sidebar-link ${isActive ? 'active' : ''}`
                }
                onClick={onClose}
              >
                <span className="material-symbols-outlined">{item.icon}</span>
                <span className="link-label">{item.label}</span>
              </NavLink>
            ))}

            {/* Logout */}
            <button className="sidebar-link logout-btn" onClick={handleLogout}>
              <span className="material-symbols-outlined">logout</span>
              <span className="link-label">Sign Out</span>
            </button>
          </div>
        </div>

        {/* Sidebar Border */}
        <div className="sidebar-border"></div>
      </aside>
    </>
  )
}

export default Sidebar
