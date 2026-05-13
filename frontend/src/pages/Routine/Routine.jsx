import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import Sidebar from '../../components/Sidebar/Sidebar'
import Loader from '../../components/Loader/Loader'
import { routinesAPI } from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import './Routine.css'

const durationOptions = [7, 14, 28]

function Routine() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [selectedView, setSelectedView] = useState('today')
  const [loading, setLoading] = useState(true)
  const [morningRoutine, setMorningRoutine] = useState([])
  const [nightRoutine, setNightRoutine] = useState([])
  const [selectedDuration, setSelectedDuration] = useState(28)
  const [customDuration, setCustomDuration] = useState('')
  const [autoAdjust, setAutoAdjust] = useState(true)
  const [planStartDay, setPlanStartDay] = useState(4)
  const [editingPreferences, setEditingPreferences] = useState(false)
  const [planMessage, setPlanMessage] = useState('')
  const [planError, setPlanError] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [logMessage, setLogMessage] = useState('')
  const [logError, setLogError] = useState('')
  const [loggingType, setLoggingType] = useState(null)
  const [todayStatus, setTodayStatus] = useState({
    morning: null,
    night: null,
  })
  const { user } = useAuth()

  const preferences = useMemo(() => ({
    skinType: user?.skin_type ? user.skin_type : 'Oily',
    goal: 'Clear Skin',
    style: 'Simple Routine'
  }), [user])

  useEffect(() => {
    loadRoutines()
  }, [])

  const loadRoutines = async () => {
    setLoading(true)
    try {
      const { ok, data } = await routinesAPI.getRoutines()
      const routines = ok && Array.isArray(data) ? data : []
      const morning = routines.filter((r) => r.routine_type === 'morning' || r.time_of_day === 'morning')
      const night = routines.filter((r) => r.routine_type === 'night' || r.time_of_day === 'night')

      const statusRes = await routinesAPI.getTodayStatus()

      setMorningRoutine(morning)
      setNightRoutine(night)
      setTodayStatus(statusRes.ok ? statusRes.data : { morning: null, night: null })
    } catch (error) {
      console.error('Error loading routines:', error)
      setMorningRoutine([])
      setNightRoutine([])
      setTodayStatus({ morning: null, night: null })
    } finally {
      setLoading(false)
    }
  }

  const resolvedDuration = customDuration ? Number(customDuration) : selectedDuration
  const hasPlan =
    (morningRoutine[0]?.steps && morningRoutine[0].steps.length > 0) ||
    (nightRoutine[0]?.steps && nightRoutine[0].steps.length > 0)

  const buildPhases = (days) => {
    if (!days || Number.isNaN(days)) return []
    if (days <= 7) {
      return [
        { name: 'Reset', days: `Day 1-${days}` }
      ]
    }
    if (days <= 14) {
      return [
        { name: 'Reset', days: 'Day 1-5' },
        { name: 'Treatment', days: 'Day 6-10' },
        { name: 'Balance', days: `Day 11-${days}` }
      ]
    }
    return [
      { name: 'Reset', days: 'Day 1-7' },
      { name: 'Treatment', days: 'Day 8-14' },
      { name: 'Balance', days: 'Day 15-21' },
      { name: 'Maintenance', days: `Day 22-${days}` }
    ]
  }

  const phases = buildPhases(resolvedDuration)
  const planProgress = Math.min(100, Math.round((planStartDay / resolvedDuration) * 100))

  const weeklyTasks = [
    { id: 'mask', label: 'Hydrating Mask', completed: true },
    { id: 'exfoliation', label: 'Exfoliation', completed: false }
  ]

  const morningSteps = morningRoutine[0]?.steps?.length
    ? morningRoutine[0].steps
    : [
        { id: 'cleanser', name: 'Cleanser' },
        { id: 'toner', name: 'Toner' },
        { id: 'serum', name: 'Serum' },
        { id: 'moisturizer', name: 'Moisturizer' },
        { id: 'spf', name: 'SPF' }
      ]

  const nightSteps = nightRoutine[0]?.steps?.length
    ? nightRoutine[0].steps
    : [
        { id: 'cleanser', name: 'Cleanser' },
        { id: 'exfoliant', name: 'Exfoliant' },
        { id: 'treatment', name: 'Treatment' },
        { id: 'eye', name: 'Eye Cream' },
        { id: 'night-cream', name: 'Night Cream' }
      ]

  const getStepLabel = (step) => step?.step_name || step?.name || step?.step || step
  const isMorningDone = todayStatus?.morning?.completed
  const isNightDone = todayStatus?.night?.completed

  const handleMarkDone = async (type) => {
    const routine = type === 'morning' ? morningRoutine[0] : nightRoutine[0]
    if (!routine?.id) {
      setLogError('No routine found to log yet.')
      return
    }

    setLogMessage('')
    setLogError('')
    setLoggingType(type)

    const steps = type === 'morning' ? morningSteps : nightSteps
    const completedSteps = steps.map(getStepLabel).filter(Boolean)

    try {
      const { ok, data } = await routinesAPI.logRoutineCompletion(
        routine.id,
        routine.routine_type || type,
        completedSteps,
        ''
      )
      if (!ok) {
        setLogError(data?.error || 'Unable to log routine right now.')
        return
      }
      setLogMessage('Routine logged successfully.')
      setTodayStatus((prev) => ({
        ...prev,
        [type]: {
          ...(prev?.[type] || {}),
          completed: true,
        },
      }))
    } catch (error) {
      console.error('Error logging routine:', error)
      setLogError('Unable to log routine right now.')
    } finally {
      setLoggingType(null)
    }
  }

  const handleGeneratePlan = async () => {
    if (!customDuration && !selectedDuration) return

    setPlanMessage('')
    setPlanError('')
    setIsGenerating(true)

    const payload = customDuration
      ? { days: 'custom', custom_days: Number(customDuration) }
      : { days: selectedDuration }

    try {
      const { ok, data } = await routinesAPI.generateRoutinePlan(payload)
      if (!ok) {
        setPlanError(data?.error || 'Unable to generate routine right now.')
        return
      }

      if (data?.needs_ai) {
        setPlanMessage(data?.message || 'Please use AI first to generate a routine.')
        return
      }

      setPlanMessage(data?.message || 'Routine generated successfully.')
      setPlanStartDay(1)
      await loadRoutines()
    } catch (error) {
      console.error('Error generating routine:', error)
      setPlanError('Unable to generate routine right now.')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="dashboard-layout">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="dashboard-main">
        <header className="dashboard-header">
          <button className="mobile-menu-toggle" onClick={() => setSidebarOpen(true)}>
            <span className="material-symbols-outlined">menu</span>
          </button>

          <div className="page-title">
            <span className="material-symbols-outlined">event_note</span>
            <h1>Skincare Routine</h1>
          </div>

          <div className="header-actions">
            <select
              className="day-select"
              value={selectedView}
              onChange={(e) => setSelectedView(e.target.value)}
            >
              <option value="today">Today</option>
              <option value="week">Week</option>
              <option value="full">Full Plan</option>
            </select>
          </div>
        </header>

        <div className="routine-content">
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
              <Loader />
            </div>
          ) : !hasPlan ? (
            <div className="routine-empty">
              <div className="empty-card">
                <span className="material-symbols-outlined">routine</span>
                <h3>No Routine Yet</h3>
                <p>Get personalized skincare routine recommendations from our AI.</p>
                <Link to="/ask" className="btn btn-primary">Ask AI for Routine</Link>
              </div>

              <div className="plan-builder">
                <h4>Create Your Plan</h4>
                <div className="duration-row">
                  {durationOptions.map((days) => (
                    <button
                      key={days}
                      className={`duration-chip ${selectedDuration === days && !customDuration ? 'active' : ''}`}
                      onClick={() => {
                        setSelectedDuration(days)
                        setCustomDuration('')
                      }}
                    >
                      {days} Days
                    </button>
                  ))}
                  <input
                    type="number"
                    min="7"
                    max="90"
                    placeholder="Custom"
                    value={customDuration}
                    onChange={(e) => setCustomDuration(e.target.value)}
                    className="duration-input"
                  />
                </div>
                <button className="btn btn-primary" onClick={handleGeneratePlan} disabled={isGenerating}>
                  {isGenerating ? 'Generating...' : 'Generate Routine'}
                </button>
                {(planMessage || planError) && (
                  <p className={`plan-message ${planError ? 'error' : 'success'}`}>
                    {planError || planMessage}
                  </p>
                )}
              </div>
            </div>
          ) : (
            <>
              <div className="routine-top">
                <section className="plan-overview">
                  <div className="plan-header">
                    <div>
                      <h3>Active Plan Overview</h3>
                      <span>Day {planStartDay} of {resolvedDuration}</span>
                    </div>
                    <div className="auto-adjust">
                      <span>AI Auto-Adjust</span>
                      <button
                        className={`toggle ${autoAdjust ? 'on' : ''}`}
                        onClick={() => setAutoAdjust((prev) => !prev)}
                        aria-label="Toggle auto adjust"
                      >
                        <span className="toggle-thumb" />
                      </button>
                    </div>
                  </div>
                  <div className="plan-progress">
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${planProgress}%` }}></div>
                    </div>
                  </div>
                </section>

                <section className="weekly-tasks">
                  <h3>Weekly Tasks</h3>
                  <div className="weekly-list">
                    {weeklyTasks.map((task) => (
                      <label key={task.id} className="weekly-item">
                        <input type="checkbox" defaultChecked={task.completed} />
                        <span>{task.label}</span>
                      </label>
                    ))}
                  </div>
                </section>
              </div>

              <section className="today-section">
                <h3>Today's Routine</h3>
                <div className="routine-cards">
                  <div className="routine-card">
                    <h4>Morning Routine</h4>
                    <ul>
                      {morningSteps.map((step, index) => (
                        <li key={step.id || step.step || step.name || index}>
                          {getStepLabel(step)}
                        </li>
                      ))}
                    </ul>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleMarkDone('morning')}
                      disabled={loggingType === 'morning' || isMorningDone}
                    >
                      {isMorningDone ? 'Done Today' : loggingType === 'morning' ? 'Saving...' : 'Mark as Done'}
                    </button>
                  </div>

                  <div className="routine-card">
                    <h4>Night Routine</h4>
                    <ul>
                      {nightSteps.map((step, index) => (
                        <li key={step.id || step.step || step.name || index}>
                          {getStepLabel(step)}
                        </li>
                      ))}
                    </ul>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleMarkDone('night')}
                      disabled={loggingType === 'night' || isNightDone}
                    >
                      {isNightDone ? 'Done Today' : loggingType === 'night' ? 'Saving...' : 'Mark as Done'}
                    </button>
                  </div>
                </div>
                {(logMessage || logError) && (
                  <p className={`plan-message ${logError ? 'error' : 'success'}`}>
                    {logError || logMessage}
                  </p>
                )}
              </section>

              <div className="routine-bottom">
                <section className="plan-phases">
                  <h3>Plan Phases</h3>
                  <div className="phase-track">
                    {phases.map((phase, index) => (
                      <div key={phase.name} className={`phase-pill ${index === 0 ? 'active' : ''}`}>
                        <span>{phase.name}</span>
                        <small>{phase.days}</small>
                      </div>
                    ))}
                  </div>
                </section>

                <section className="routine-impact">
                  <h3>Routine Impact</h3>
                  <div className="impact-grid">
                    <div>
                      <span className="material-symbols-outlined">filter_vintage</span>
                      <p>Clearer Skin</p>
                    </div>
                    <div>
                      <span className="material-symbols-outlined">water_drop</span>
                      <p>Reduced Redness</p>
                    </div>
                  </div>
                </section>

                <section className="user-preferences">
                  <h3>User Preferences</h3>
                  <div className="preferences-list">
                    <p><strong>Skin Type:</strong> {preferences.skinType}</p>
                    <p><strong>Goal:</strong> {preferences.goal}</p>
                    <p><strong>Style:</strong> {preferences.style}</p>
                  </div>
                  <button className="btn btn-primary" onClick={() => setEditingPreferences(!editingPreferences)}>
                    {editingPreferences ? 'Close' : 'Customize'}
                  </button>
                </section>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default Routine
