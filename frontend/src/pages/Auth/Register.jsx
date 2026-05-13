import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'
import { useAuth } from '../../context/AuthContext'
import './Auth.css'

function Register() {
  const { theme } = useTheme()
  const { register } = useAuth()
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    skinType: '',
    sensitivity: '',
    allergies: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const skinTypes = [
    { value: 'oily', label: 'Oily', icon: '💧' },
    { value: 'dry', label: 'Dry', icon: '🏜️' },
    { value: 'combination', label: 'Combination', icon: '⚖️' },
    { value: 'normal', label: 'Normal', icon: '✨' },
    { value: 'sensitive', label: 'Sensitive', icon: '🌸' },
  ]

  const sensitivityLevels = [
    { value: 'low', label: 'Low', description: 'Rarely react to products' },
    { value: 'normal', label: 'Normal', description: 'Occasionally sensitive' },
    { value: 'high', label: 'High', description: 'Very reactive skin' },
  ]

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
    setError('')
  }

  const handleSkinTypeSelect = (value) => {
    setFormData({ ...formData, skinType: value })
    setError('')
  }

  const handleSensitivitySelect = (value) => {
    setFormData({ ...formData, sensitivity: value })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    // Validate step 1
    if (step === 1) {
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match')
        return
      }
      if (formData.password.length < 8) {
        setError('Password must be at least 8 characters')
        return
      }
      setStep(2)
      return
    }
    
    // Validate step 2
    if (step === 2) {
      if (!formData.skinType) {
        setError('Please select your skin type')
        return
      }
      setStep(3)
      return
    }
    
    // Step 3: Submit registration
    if (!formData.sensitivity) {
      setError('Please select your sensitivity level')
      return
    }
    
    setLoading(true)
    
    const userData = {
      name: formData.name,
      email: formData.email,
      password: formData.password,
      password_confirm: formData.confirmPassword,  // Backend expects this field
      skin_type: formData.skinType,
      sensitivity: formData.sensitivity,
      allergies: formData.allergies,
    }
    
    const result = await register(userData)
    
    if (result.success) {
      navigate('/dashboard')
    } else {
      setError(result.error)
    }
    
    setLoading(false)
  }

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <>
            <div className="auth-form-header">
              <h2 className="auth-title">Create Account</h2>
              <p className="auth-subtitle">Begin your personalized skincare journey.</p>
            </div>

            {/* Social Login */}
            <div className="social-login">
              <button type="button" className="social-btn">
                <svg className="social-icon" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="currentColor"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="currentColor"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="currentColor"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="currentColor"/>
                </svg>
                <span>Google</span>
              </button>
              <button type="button" className="social-btn">
                <svg className="social-icon" viewBox="0 0 24 24">
                  <path d="M17.05 20.28c-.96.95-2.04 1.44-3.23 1.44c-1.14 0-2.09-.44-3.18-.44c-1.09 0-2.15.46-3.21.46c-1.18 0-2.31-.56-3.37-1.63c-2.16-2.16-2.28-5.75-.68-7.79c.8-1.01 1.83-1.63 3.01-1.63c1.08 0 1.95.46 3.01.46c1.06 0 1.88-.47 3.06-.47c1.04 0 2 .5 2.81 1.25c-2.35 1.17-2.73 4.39-.37 5.7c-.55 1.25-1.21 2.21-1.87 3.05zM12.03 7.25c-.02-2.3 1.91-4.22 4.19-4.25c.03 2.5-2.28 4.54-4.19 4.25z" fill="currentColor"/>
                </svg>
                <span>Apple</span>
              </button>
            </div>

            <div className="auth-divider">
              <span>Or email</span>
            </div>

            <div className="form-group">
              <label className="form-label">Full Name</label>
              <div className="input-wrapper">
                <input
                  type="text"
                  name="name"
                  className="form-input"
                  placeholder="Dr. Jane Smith"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Email Address</label>
              <div className="input-wrapper">
                <input
                  type="email"
                  name="email"
                  className="form-input"
                  placeholder="jane@clinical.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
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

            <div className="form-group">
              <label className="form-label">Confirm Password</label>
              <div className="input-wrapper">
                <input
                  type="password"
                  name="confirmPassword"
                  className="form-input"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
          </>
        )

      case 2:
        return (
          <>
            <div className="auth-form-header">
              <h2 className="auth-title">Your Skin Type</h2>
              <p className="auth-subtitle">Help us understand your skin better.</p>
            </div>

            <div className="skin-type-grid">
              {skinTypes.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  className={`skin-type-card ${formData.skinType === type.value ? 'selected' : ''}`}
                  onClick={() => handleSkinTypeSelect(type.value)}
                >
                  <span className="skin-type-icon">{type.icon}</span>
                  <span className="skin-type-label">{type.label}</span>
                </button>
              ))}
            </div>
          </>
        )

      case 3:
        return (
          <>
            <div className="auth-form-header">
              <h2 className="auth-title">Sensitivity Level</h2>
              <p className="auth-subtitle">How does your skin typically react?</p>
            </div>

            <div className="sensitivity-options">
              {sensitivityLevels.map((level) => (
                <button
                  key={level.value}
                  type="button"
                  className={`sensitivity-card ${formData.sensitivity === level.value ? 'selected' : ''}`}
                  onClick={() => handleSensitivitySelect(level.value)}
                >
                  <div className="sensitivity-header">
                    <span className="sensitivity-label">{level.label}</span>
                    {formData.sensitivity === level.value && (
                      <span className="material-symbols-outlined check-icon">check_circle</span>
                    )}
                  </div>
                  <span className="sensitivity-description">{level.description}</span>
                </button>
              ))}
            </div>

            <div className="form-group">
              <label className="form-label">Known Allergies (Optional)</label>
              <div className="input-wrapper">
                <input
                  type="text"
                  name="allergies"
                  className="form-input"
                  placeholder="e.g., Fragrance, Parabens, Nuts"
                  value={formData.allergies}
                  onChange={handleChange}
                />
              </div>
              <span className="form-hint">Separate multiple allergies with commas</span>
            </div>
          </>
        )

      default:
        return null
    }
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
              <span className="badge-text">Clinical Onboarding</span>
            </div>
            
            <h1 className="auth-hero-title">
              Your Skin, <br />
              <span className="text-gradient">Our Science.</span>
            </h1>
            
            <p className="auth-hero-description">
              Join thousands who have transformed their skincare routine with AI-powered personalization.
            </p>

            <div className="auth-hero-image">
              <img
                src="https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=600&h=500&fit=crop"
                alt="Skincare routine"
              />
            </div>
          </div>

          <div className="auth-hero-watermark">LUMIÈRE</div>
        </section>

        {/* Right Section: Register Form */}
        <section className="auth-form-section">
          <div className="auth-form-container">
            {/* Header */}
            <div className="auth-header">
              <Link to="/" className="auth-logo">
                {theme === 'dark' ? 'Lumière Clinical' : 'Aura Skincare'}
              </Link>
              <span className="auth-tagline">Step {step} of 3</span>
            </div>

            <div className="auth-form-wrapper">
              {/* Progress Bar */}
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${(step / 3) * 100}%` }}></div>
              </div>

              <form className="auth-form" onSubmit={handleSubmit}>
                {error && (
                  <div className="form-error-message">
                    {error}
                  </div>
                )}
                
                {renderStep()}

                <div className="form-actions">
                  {step > 1 && (
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => setStep(step - 1)}
                    >
                      Back
                    </button>
                  )}
                  <button
                    type="submit"
                    className="btn btn-primary btn-block"
                    disabled={loading}
                  >
                    {loading ? 'Creating...' : step < 3 ? 'Continue' : 'Create Account'}
                  </button>
                </div>
              </form>

              {/* Login Link */}
              <div className="auth-footer">
                <p>
                  Already have an account?{' '}
                  <Link to="/login" className="auth-link">Sign in</Link>
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
        </div>
        <div className="footer-copyright">
          © 2024 Lumière Clinical.
        </div>
      </footer>
    </div>
  )
}

export default Register
