import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import './Onboarding.css'

const STEPS = [
  {
    id: 'skin_type',
    title: 'What\'s your skin type?',
    description: 'This helps us recommend the right products for you',
    options: [
      { value: 'oily', label: 'Oily', icon: 'water_drop', desc: 'Shiny, enlarged pores, prone to breakouts' },
      { value: 'dry', label: 'Dry', icon: 'ac_unit', desc: 'Tight, flaky, rough texture' },
      { value: 'combination', label: 'Combination', icon: 'contrast', desc: 'Oily T-zone, dry cheeks' },
      { value: 'normal', label: 'Normal', icon: 'check_circle', desc: 'Balanced, minimal issues' },
      { value: 'sensitive', label: 'Sensitive', icon: 'healing', desc: 'Reacts easily, redness, irritation' },
    ],
  },
  {
    id: 'concerns',
    title: 'What are your top concerns?',
    description: 'Select all that apply — we\'ll prioritize these in your routine',
    options: [
      { value: 'acne', label: 'Acne & Breakouts', icon: 'coronavirus' },
      { value: 'pigmentation', label: 'Dark Spots & Pigmentation', icon: 'palette' },
      { value: 'aging', label: 'Aging & Fine Lines', icon: 'schedule' },
      { value: 'dullness', label: 'Dullness & Uneven Tone', icon: 'brightness_low' },
      { value: 'dryness', label: 'Dryness & Dehydration', icon: 'water_drop' },
      { value: 'dark_circles', label: 'Dark Circles & Puffiness', icon: 'nights_stay' },
      { value: 'redness', label: 'Redness & Sensitivity', icon: 'whatshot' },
      { value: 'pores', label: 'Large Pores & Oiliness', icon: 'circle' },
    ],
  },
  {
    id: 'routine',
    title: 'What\'s your current routine?',
    description: 'This helps us know where to start',
    options: [
      { value: 'none', label: 'None', icon: 'block', desc: 'I don\'t have a skincare routine yet' },
      { value: 'basic', label: 'Basic', icon: 'spa', desc: 'Cleanser + moisturizer + sunscreen' },
      { value: 'intermediate', label: 'Intermediate', icon: 'star', desc: 'Adds serums, toners, treatments' },
      { value: 'advanced', label: 'Advanced', icon: 'auto_awesome', desc: 'Full routine with actives, exfoliants' },
    ],
  },
  {
    id: 'goals',
    title: 'What\'s your main goal?',
    description: 'We\'ll tailor your experience around this',
    options: [
      { value: 'clear_skin', label: 'Clear, Acne-Free Skin', icon: 'check_circle', desc: 'Reduce breakouts and prevent new ones' },
      { value: 'glow', label: 'Healthy Glow', icon: 'wb_sunny', desc: 'Radiant, even-toned, hydrated skin' },
      { value: 'anti_aging', label: 'Anti-Aging', icon: 'schedule', desc: 'Reduce fine lines and maintain youthfulness' },
      { value: 'even_tone', label: 'Even Skin Tone', icon: 'palette', desc: 'Reduce dark spots, pigmentation, redness' },
    ],
  },
]

function Onboarding() {
  const navigate = useNavigate()
  const { user, updateUser } = useAuth()
  const [currentStep, setCurrentStep] = useState(0)
  const [answers, setAnswers] = useState({
    skin_type: '',
    concerns: [],
    routine: '',
    goals: '',
  })
  const [saving, setSaving] = useState(false)

  const step = STEPS[currentStep]

  const handleSelect = (value) => {
    if (step.id === 'concerns') {
      setAnswers(prev => ({
        ...prev,
        concerns: prev.concerns.includes(value)
          ? prev.concerns.filter(c => c !== value)
          : [...prev.concerns, value],
      }))
    } else {
      setAnswers(prev => ({ ...prev, [step.id]: value }))
    }
  }

  const canProceed = () => {
    if (step.id === 'concerns') return answers.concerns.length > 0
    return answers[step.id] !== ''
  }

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(prev => prev + 1)
    } else {
      handleComplete()
    }
  }

  const handleComplete = async () => {
    setSaving(true)
    try {
      await updateUser({
        skin_type: answers.skin_type,
        concerns: answers.concerns,
        routine_level: answers.routine,
        skin_goals: answers.goals,
        onboarding_completed: true,
      })
      navigate('/dashboard')
    } catch {
      navigate('/dashboard')
    }
  }

  return (
    <div className="onboarding-page">
      <div className="onboarding-container">
        <div className="onboarding-header">
          <div className="onboarding-logo">
            <span className="material-symbols-outlined">spa</span>
            <span className="logo-text">Lumiere Clinical</span>
          </div>
          <div className="step-indicator">
            {STEPS.map((_, i) => (
              <div key={i} className={`step-dot ${i === currentStep ? 'active' : ''} ${i < currentStep ? 'completed' : ''}`}>
                {i < currentStep ? <span className="material-symbols-outlined">check</span> : i + 1}
              </div>
            ))}
          </div>
        </div>

        <div className="onboarding-body">
          <div className="step-label">Step {currentStep + 1} of {STEPS.length}</div>
          <h1 className="step-title">{step.title}</h1>
          <p className="step-description">{step.description}</p>

          <div className={`options-grid ${step.id === 'concerns' ? 'multi-select' : ''}`}>
            {step.options.map(option => {
              const isSelected = step.id === 'concerns'
                ? answers.concerns.includes(option.value)
                : answers[step.id] === option.value

              return (
                <button
                  key={option.value}
                  className={`option-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleSelect(option.value)}
                >
                  <span className="material-symbols-outlined option-icon">{option.icon}</span>
                  <span className="option-label">{option.label}</span>
                  {option.desc && <span className="option-desc">{option.desc}</span>}
                  {step.id === 'concerns' && isSelected && (
                    <span className="check-mark material-symbols-outlined">check_circle</span>
                  )}
                </button>
              )
            })}
          </div>
        </div>

        <div className="onboarding-footer">
          <button
            className="btn btn-secondary"
            onClick={() => currentStep > 0 ? setCurrentStep(prev => prev - 1) : navigate('/dashboard')}
          >
            {currentStep === 0 ? 'Skip' : 'Back'}
          </button>
          <button
            className="btn btn-primary"
            onClick={handleNext}
            disabled={!canProceed() || saving}
          >
            {saving ? 'Saving...' : currentStep === STEPS.length - 1 ? 'Get Started' : 'Continue'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Onboarding