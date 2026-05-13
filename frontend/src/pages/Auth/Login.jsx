import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'
import { useAuth } from '../../context/AuthContext'
import './Auth.css'

function Login() {
  const { theme } = useTheme()
  const { login } = useAuth()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
    setError('') // Clear error on input change
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    const result = await login(formData.email, formData.password)
    
    if (result.success) {
      navigate('/dashboard')
    } else {
      setError(result.error)
    }
    
    setLoading(false)
  }

  return (
    <div className="auth-page">
      <main className="auth-main">
        {/* Left Section: Visual Hero */}
        <section className="auth-hero">
          <div className="auth-hero-overlay"></div>
          <div className="auth-hero-gradient"></div>
          
          <div className="auth-hero-content">
            <div className="auth-hero-badge">
              <span className="badge-text">Nocturnal Recovery Phase</span>
            </div>
            
            <h1 className="auth-hero-title">
              The Science of <br />
              <span className="text-gradient">Cellular Silence.</span>
            </h1>
            
            <p className="auth-hero-description">
              Experience the precision of clinical aesthetics. Our night-phase serum aligns with your circadian rhythm to restore vitality while you rest.
            </p>

            <div className="auth-hero-image">
              <img
                src="https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=600&h=500&fit=crop"
                alt="Premium skincare product"
              />
            </div>
          </div>

          <div className="auth-hero-watermark">NOCTURNE</div>
        </section>

        {/* Right Section: Login Form */}
        <section className="auth-form-section">
          <div className="auth-form-container">
            {/* Header */}
            <div className="auth-header">
              <Link to="/" className="auth-logo">
                {theme === 'dark' ? 'Lumière Clinical' : 'Aura Skincare'}
              </Link>
              <span className="auth-tagline">Sanctuary at Night</span>
            </div>

            <div className="auth-form-wrapper">
              <div className="auth-form-header">
                <h2 className="auth-title">Welcome Back</h2>
                <p className="auth-subtitle">Access your personalized clinical sanctuary.</p>
              </div>

              {/* Social Login */}
              <div className="social-login">
                <button className="social-btn">
                  <svg className="social-icon" viewBox="0 0 24 24">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="currentColor"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="currentColor"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="currentColor"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="currentColor"/>
                  </svg>
                  <span>Google</span>
                </button>
                <button className="social-btn">
                  <svg className="social-icon" viewBox="0 0 24 24">
                    <path d="M17.05 20.28c-.96.95-2.04 1.44-3.23 1.44c-1.14 0-2.09-.44-3.18-.44c-1.09 0-2.15.46-3.21.46c-1.18 0-2.31-.56-3.37-1.63c-2.16-2.16-2.28-5.75-.68-7.79c.8-1.01 1.83-1.63 3.01-1.63c1.08 0 1.95.46 3.01.46c1.06 0 1.88-.47 3.06-.47c1.04 0 2 .5 2.81 1.25c-2.35 1.17-2.73 4.39-.37 5.7c-.55 1.25-1.21 2.21-1.87 3.05zM12.03 7.25c-.02-2.3 1.91-4.22 4.19-4.25c.03 2.5-2.28 4.54-4.19 4.25z" fill="currentColor"/>
                  </svg>
                  <span>Apple</span>
                </button>
              </div>

              {/* Divider */}
              <div className="auth-divider">
                <span>Or email</span>
              </div>

              {/* Login Form */}
              <form className="auth-form" onSubmit={handleSubmit}>
                {error && (
                  <div className="form-error-message">
                    {error}
                  </div>
                )}
                
                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <div className="input-wrapper">
                    <input
                      type="email"
                      name="email"
                      className="form-input"
                      placeholder="dr.smith@clinical.com"
                      value={formData.email}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <div className="form-label-row">
                    <label className="form-label">Password</label>
                    <Link to="/forgot-password" className="form-link">Forgot?</Link>
                  </div>
                  <div className="input-wrapper">
                    <input
                      type="password"
                      name="password"
                      className="form-input"
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                  {loading ? 'Accessing...' : 'Access Sanctuary'}
                </button>
              </form>

              {/* Signup Link */}
              <div className="auth-footer">
                <p>
                  First time visiting?{' '}
                  <Link to="/register" className="auth-link">Create your profile</Link>
                </p>
              </div>
            </div>
          </div>

          {/* Decorative Elements */}
          <div className="auth-decoration auth-decoration-1"></div>
          <div className="auth-decoration auth-decoration-2"></div>
        </section>
      </main>

      {/* Footer */}
      <footer className="auth-page-footer">
        <div className="footer-links">
          <a href="#privacy">Privacy Policy</a>
          <a href="#terms">Terms of Service</a>
          <a href="#clinical">Clinical Trials</a>
          <a href="#sustainability">Sustainability</a>
        </div>
        <div className="footer-copyright">
          © 2024 Lumière Clinical. Sanctuary at Night Edition.
        </div>
      </footer>
    </div>
  )
}

export default Login
