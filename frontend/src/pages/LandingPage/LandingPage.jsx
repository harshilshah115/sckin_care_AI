import { useNavigate } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'
import './LandingPage.css'

function LandingPage() {
  const { theme } = useTheme()
  const navigate = useNavigate()

  const handleScanClick = () => {
    navigate('/register')
  }

  const handleAskAIClick = () => {
    navigate('/register')
  }

  const features = [
    {
      icon: 'clinical_notes',
      title: 'AI Scan',
      description: 'High-resolution dermis mapping through multi-spectral smartphone imaging.',
    },
    {
      icon: 'forum',
      title: 'Chat',
      description: 'Real-time consultation with our clinical AI specialized in ingredient synergy.',
    },
    {
      icon: 'routine',
      title: 'Routine',
      description: 'Dynamic daily regimens that adapt to your environment and sleep cycles.',
    },
    {
      icon: 'monitoring',
      title: 'Tracking',
      description: "Longitudinal progress visualization using proprietary 'Glow-Score' metrics.",
    },
  ]

  const testimonials = [
    {
      quote: "The AI analysis picked up on dehydration levels that even my aesthetician missed. The nocturnal routine has transformed my morning radiance.",
      name: 'Elena Vance',
      role: 'Dermatology Patient',
      image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop',
    },
    {
      quote: "Simple, clinical, and effective. Lumière takes the guesswork out of complex skincare chemistry. It's like having a lab in my pocket.",
      name: 'Dr. Julian Thorne',
      role: 'Molecular Biologist',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop',
    },
    {
      quote: "I finally understand why certain products weren't working. The ingredient synergy chat saved me hundreds on the wrong routine.",
      name: 'Sasha K.',
      role: 'Lifestyle Creator',
      image: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop',
    },
  ]

  return (
    <main className="landing-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-bg">
          <div className="hero-glow hero-glow-1"></div>
          <div className="hero-glow hero-glow-2"></div>
        </div>

        <div className="hero-content container">
          <div className="hero-text">
            <div className="hero-badge">
              <span className="badge-dot"></span>
              <span className="badge-text">New Clinical Release 2.0</span>
            </div>

            <h1 className="hero-title text-glow">
              AI-Powered <br />
              Personalized <span className="text-primary italic">Skincare</span>
            </h1>

            <p className="hero-description">
              {theme === 'dark'
                ? "A clinical-grade diagnostic engine in the palm of your hand. Discover your skin's nocturnal rhythm with our AI-driven Lumière analysis."
                : 'Precision analysis meets botanical luxury. Our Clinical Sanctuary uses advanced AI to decode your skin\'s unique needs and craft a routine that evolves with you.'}
            </p>

            <div className="hero-buttons">
              <button className="btn btn-primary btn-lg" onClick={handleScanClick}>
                Scan Your Skin
                <span className="material-symbols-outlined filled">scan</span>
              </button>
              <button className="btn btn-outline btn-lg" onClick={handleAskAIClick}>Ask AI</button>
            </div>
          </div>

          <div className="hero-image">
            <div className="hero-image-wrapper">
              <img
                src="https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?w=600&h=750&fit=crop"
                alt="Person with glowing clear skin"
                className="hero-img"
              />
              <div className="hero-image-overlay"></div>

              {/* Floating Card */}
              <div className="hero-float-card glass-card">
                <div className="float-card-icon">
                  <span className="material-symbols-outlined">biotech</span>
                </div>
                <div className="float-card-content">
                  <div className="float-card-title">Molecular Analysis</div>
                  <div className="float-card-subtitle">99.8% Precision Accuracy</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features section">
        <div className="container">
          <div className="features-header">
            <div className="features-header-left">
              <span className="section-label">Precision Science</span>
              <h2 className="section-title">
                The Digital <br />Aesthetician Protocol
              </h2>
            </div>
            <p className="features-description">
              Our platform integrates cellular imaging with algorithmic dermatology to provide a sanctuary for your skin health.
            </p>
          </div>

          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card glass-card">
                <div className="feature-icon">
                  <span className="material-symbols-outlined">{feature.icon}</span>
                </div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials section">
        <div className="container">
          <h2 className="section-title text-center">Clinical Results</h2>

          <div className="testimonials-grid">
            {testimonials.map((testimonial, index) => (
              <div
                key={index}
                className={`testimonial-card ${index === 1 ? 'testimonial-offset' : ''}`}
              >
                <div className="testimonial-image">
                  <img src={testimonial.image} alt={testimonial.name} />
                </div>
                <span className="material-symbols-outlined filled quote-icon">format_quote</span>
                <p className="testimonial-quote">{testimonial.quote}</p>
                <div className="testimonial-author">
                  <div className="author-name">{testimonial.name}</div>
                  <div className="author-role">{testimonial.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta section">
        <div className="container">
          <div className="cta-card">
            <div className="cta-bg"></div>
            <div className="cta-content">
              <h2 className="cta-title">
                Ready for your <br />best skin yet?
              </h2>
              <p className="cta-description">
                Join over 100,000 users who have transformed their skin health through AI-powered clinical guidance.
              </p>
              <button className="btn btn-cta btn-lg" onClick={handleScanClick}>Start Free Analysis</button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-logo">
              {theme === 'dark' ? 'Lumière Clinical' : 'Aura Clinical Sanctuary'}
            </div>
            <div className="footer-links">
              <a href="#privacy">Privacy Policy</a>
              <a href="#terms">Terms of Service</a>
              <a href="#clinical">Clinical Trials</a>
              <a href="#sustainability">Sustainability</a>
            </div>
            <div className="footer-social">
              <span className="material-symbols-outlined">public</span>
              <span className="material-symbols-outlined">science</span>
            </div>
          </div>
          <div className="footer-copyright">
            © 2024 {theme === 'dark' ? 'Lumière Clinical. Sanctuary at Night Edition.' : 'Aura Clinical Sanctuary. All rights reserved.'}
          </div>
        </div>
      </footer>
    </main>
  )
}

export default LandingPage
