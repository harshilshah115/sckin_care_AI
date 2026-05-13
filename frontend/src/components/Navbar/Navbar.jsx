import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'
import './Navbar.css'

function Navbar() {
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const navLinks = [
    { name: 'Science', href: '#science', active: true },
    { name: 'Treatment', href: '#treatment', active: false },
    { name: 'Membership', href: '#membership', active: false },
    { name: 'Routines', href: '#routines', active: false },
  ]

  const handleLogin = () => {
    navigate('/login')
  }

  const handleGetStarted = () => {
    navigate('/register')
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <Link to="/" className="navbar-logo">
          {theme === 'dark' ? 'Lumière Clinical' : 'Aura Skincare'}
        </Link>

        {/* Desktop Navigation */}
        <div className="navbar-links">
          {navLinks.map((link) => (
            <a
              key={link.name}
              href={link.href}
              className={`navbar-link ${link.active ? 'active' : ''}`}
            >
              {link.name}
            </a>
          ))}
        </div>

        {/* Actions */}
        <div className="navbar-actions">
          {/* Theme Toggle */}
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            <span className="material-symbols-outlined">
              {theme === 'dark' ? 'light_mode' : 'dark_mode'}
            </span>
          </button>

          <button className="btn-login" onClick={handleLogin}>Login</button>
          <button className="btn btn-primary" onClick={handleGetStarted}>Get Started</button>

          {/* Mobile Menu Button */}
          <button
            className="mobile-menu-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            <span className="material-symbols-outlined">
              {mobileMenuOpen ? 'close' : 'menu'}
            </span>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <div className={`mobile-menu ${mobileMenuOpen ? 'open' : ''}`}>
        {navLinks.map((link) => (
          <a
            key={link.name}
            href={link.href}
            className={`mobile-link ${link.active ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            {link.name}
          </a>
        ))}
        <div className="mobile-actions">
          <button className="btn-login" onClick={handleLogin}>Login</button>
          <button className="btn btn-primary" onClick={handleGetStarted}>Get Started</button>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
