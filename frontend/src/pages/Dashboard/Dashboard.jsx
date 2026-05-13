import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import Sidebar from '../../components/Sidebar/Sidebar'
import { useAuth } from '../../context/AuthContext'
import { historyAPI, scanAPI, questionAPI, routinesAPI } from '../../services/api'
import Loader from '../../components/Loader/Loader'
import './Dashboard.css'

function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState({
    metrics: null,
    recentScans: [],
    recentQuestions: [],
  })
  const [routineStatus, setRoutineStatus] = useState({
    morning: null,
    night: null,
  })
  const [routineMessage, setRoutineMessage] = useState('')
  const [routineError, setRoutineError] = useState('')
  const [loggingRoutine, setLoggingRoutine] = useState(null)
  const [morningChecked, setMorningChecked] = useState([])
  const [nightChecked, setNightChecked] = useState([])

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setLoading(true)

    try {
      const progressRes = await historyAPI.getProgressSummary()
      const scansRes = await scanAPI.getScanHistory()
      const questionsRes = await questionAPI.getQuestionHistory()
      const routineRes = await routinesAPI.getTodayStatus()

      setDashboardData({
        metrics: progressRes.ok ? progressRes.data : null,
        recentScans: scansRes.ok ? scansRes.data.slice(0, 3) : [],
        recentQuestions: questionsRes.ok ? questionsRes.data.slice(0, 3) : [],
      })
      setRoutineStatus(routineRes.ok ? routineRes.data : { morning: null, night: null })
    } catch (error) {
      console.error('Error loading dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good Morning'
    if (hour < 18) return 'Good Afternoon'
    return 'Good Evening'
  }

  const getUserName = () => {
    if (!user) return 'User'
    return user.name || user.email.split('@')[0]
  }

  const quickActions = [
    { icon: 'clinical_notes', title: 'Scan Skin', description: 'Update skin analysis', path: '/scan', color: 'primary' },
    { icon: 'forum', title: 'Ask AI', description: 'Consult skin assistant', path: '/ask', color: 'secondary' },
    { icon: 'calendar_today', title: 'View Routine', description: 'Personalized regimen', path: '/routine', color: 'tertiary' },
  ]

  const latestScan = dashboardData.recentScans[0]
  const score = dashboardData.metrics?.current_score || latestScan?.skin_score || 0
  const scoreLabel = score >= 70 ? 'Improving' : score >= 40 ? 'Needs Attention' : 'High Priority'
  const scoreChange = dashboardData.metrics?.score_change ?? 0
  const issuePrimary = latestScan?.detected_issues?.[0]?.name || 'Acne'
  const issueSecondary = latestScan?.detected_issues?.[1]?.name || 'Oiliness'

  const breakdownRows = [
    { label: issuePrimary, tone: 'critical', value: Math.min(90, Math.max(20, 100 - score)) },
    { label: issueSecondary, tone: 'warning', value: Math.min(85, Math.max(25, 90 - score)) },
    { label: 'Hydration', tone: 'critical', value: Math.min(70, Math.max(20, 60 - scoreChange)) },
    { label: 'Pores', tone: 'success', value: Math.min(80, Math.max(30, score)) },
  ]

  const morningSteps = routineStatus?.morning?.routine?.steps || []
  const nightSteps = routineStatus?.night?.routine?.steps || []
  const morningLabel = morningSteps.length ? `Morning (${morningSteps.length} steps)` : 'Morning'
  const nightLabel = nightSteps.length ? `Night (${nightSteps.length} steps)` : 'Night'
  const isMorningDone = routineStatus?.morning?.completed
  const isNightDone = routineStatus?.night?.completed
  const morningRoutineId = routineStatus?.morning?.routine?.id
  const nightRoutineId = routineStatus?.night?.routine?.id

  const getStepLabel = useCallback((step) => step?.step_name || step?.name || step?.step || step, [])
  const getStepKey = useCallback(
    (step, index) => `${index}-${step?.id ?? step?.step ?? step?.step_name ?? step?.name ?? 'step'}`,
    []
  )

  useEffect(() => {
    if (isMorningDone) {
      setMorningChecked(morningSteps.map(getStepKey))
      return
    }
    setMorningChecked([])
  }, [isMorningDone, morningRoutineId, morningSteps, getStepKey])

  useEffect(() => {
    if (isNightDone) {
      setNightChecked(nightSteps.map(getStepKey))
      return
    }
    setNightChecked([])
  }, [isNightDone, nightRoutineId, nightSteps, getStepKey])

  const logRoutine = useCallback(
    async (type) => {
      if (loggingRoutine === type) return

      const routine = type === 'morning' ? routineStatus?.morning?.routine : routineStatus?.night?.routine
      if (!routine?.id) {
        setRoutineError('No routine found to log yet.')
        return
      }

      setRoutineMessage('')
      setRoutineError('')
      setLoggingRoutine(type)

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
          setRoutineError(data?.error || 'Unable to log routine right now.')
          return
        }
        setRoutineMessage(`${type === 'morning' ? 'Morning' : 'Night'} routine saved.`)
        setRoutineStatus((prev) => ({
          ...prev,
          [type]: {
            ...(prev?.[type] || {}),
            completed: true,
          },
        }))
      } catch (error) {
        console.error('Error logging routine:', error)
        setRoutineError('Unable to log routine right now.')
      } finally {
        setLoggingRoutine(null)
      }
    },
    [getStepLabel, loggingRoutine, morningSteps, nightSteps, routineStatus]
  )

  const handleToggle = (type, stepKey) => {
    setRoutineMessage('')
    setRoutineError('')

    if (type === 'morning') {
      const next = morningChecked.includes(stepKey)
        ? morningChecked.filter((key) => key !== stepKey)
        : [...morningChecked, stepKey]

      setMorningChecked(next)
      if (!isMorningDone && morningSteps.length > 0 && next.length === morningSteps.length) {
        logRoutine('morning')
      }
      return
    }

    const next = nightChecked.includes(stepKey)
      ? nightChecked.filter((key) => key !== stepKey)
      : [...nightChecked, stepKey]

    setNightChecked(next)
    if (!isNightDone && nightSteps.length > 0 && next.length === nightSteps.length) {
      logRoutine('night')
    }
  }

  return (
    <div className="dashboard-layout">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="dashboard-main">
        <header className="dashboard-header">
          <button
            className="mobile-menu-toggle"
            onClick={() => setSidebarOpen(true)}
          >
            <span className="material-symbols-outlined">menu</span>
          </button>

          {/*
          <div className="header-search">
            <span className="material-symbols-outlined">search</span>
            <input type="text" placeholder="Search your skin records..." />
          </div>

          <div className="header-actions">
            <button className="header-btn">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button className="header-btn">
              <span className="material-symbols-outlined">history</span>
            </button>
            <div className="header-user">
              <div className="header-user-info">
                <span className="header-user-name">{getUserName()}</span>
                <span className="header-user-role">Clinical Portal</span>
              </div>
              <div className="header-user-avatar">
                {getUserName().charAt(0).toUpperCase()}
              </div>
            </div>
          </div>
          */}
        </header>

        <div className="dashboard-content">
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
              <Loader />
            </div>
          ) : (
            <>
              <section className="welcome-section">
                <div className="welcome-text">
                  <h1>{getGreeting()}, {getUserName()}</h1>
                  <p>
                    {dashboardData.recentScans.length > 0
                      ? 'Your skin is improving - keep going!'
                      : 'Welcome! Start by analyzing your skin with our AI scanner.'}
                  </p>
                </div>
                <div className="welcome-date">
                  <span className="material-symbols-outlined">calendar_today</span>
                  <span>{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</span>
                </div>
              </section>

              <div className="dashboard-hero">
                <section className="quick-actions">
                  {quickActions.map((action, index) => (
                    <Link key={index} to={action.path} className={`action-card action-${action.color}`}>
                      <div className="action-icon">
                        <span className="material-symbols-outlined">{action.icon}</span>
                      </div>
                      <div className="action-content">
                        <h3>{action.title}</h3>
                        <p>{action.description}</p>
                      </div>
                    </Link>
                  ))}
                </section>

                <section className="score-panel">
                  <div className="score-gauge" style={{ '--score': score }}>
                    <div className="score-ring">
                      <div className="score-inner">
                        <div className="score-value">{score}</div>
                        <div className="score-max">/100</div>
                        <div className="score-label">{scoreLabel}</div>
                      </div>
                    </div>
                  </div>
                  <div className="score-issues">
                    <div className="issue-chip">
                      <span className="issue-title">{issuePrimary}</span>
                      <span className="issue-level">Moderate</span>
                    </div>
                    <div className="issue-chip">
                      <span className="issue-title">{issueSecondary}</span>
                      <span className="issue-level">High</span>
                    </div>
                  </div>
                  <p className="score-note">
                    {dashboardData.recentScans.length > 0
                      ? 'Your skin is currently showing imbalance. Focus on balancing and calming.'
                      : 'Run your first scan to see your personalized analysis and score.'}
                  </p>
                </section>

                <section className="routine-panel">
                  <div className="routine-header">
                    <h3>Today's Routine</h3>
                    <span className="routine-meta">{morningLabel}</span>
                  </div>
                  <div className="routine-list">
                    {morningSteps.length ? (
                      morningSteps.map((step, index) => {
                        const stepKey = getStepKey(step, index)
                        return (
                          <label
                            key={stepKey}
                            className={`routine-item ${isMorningDone ? 'disabled' : ''}`}
                          >
                            <input
                              type="checkbox"
                              checked={morningChecked.includes(stepKey)}
                              onChange={() => handleToggle('morning', stepKey)}
                              disabled={isMorningDone || loggingRoutine === 'morning'}
                            />
                            <span>{getStepLabel(step)}</span>
                          </label>
                        )
                      })
                    ) : (
                      <p className="routine-empty">No morning routine yet.</p>
                    )}
                  </div>
                  <div className="routine-header alt">
                    <span className="routine-meta">{nightLabel}</span>
                  </div>
                  <div className="routine-list">
                    {nightSteps.length ? (
                      nightSteps.map((step, index) => {
                        const stepKey = getStepKey(step, index)
                        return (
                          <label
                            key={stepKey}
                            className={`routine-item ${isNightDone ? 'disabled' : ''}`}
                          >
                            <input
                              type="checkbox"
                              checked={nightChecked.includes(stepKey)}
                              onChange={() => handleToggle('night', stepKey)}
                              disabled={isNightDone || loggingRoutine === 'night'}
                            />
                            <span>{getStepLabel(step)}</span>
                          </label>
                        )
                      })
                    ) : (
                      <p className="routine-empty">No night routine yet.</p>
                    )}
                  </div>
                  {(routineMessage || routineError) && (
                    <p className={`routine-feedback ${routineError ? 'error' : 'success'}`}>
                      {routineError || routineMessage}
                    </p>
                  )}
                  <Link to="/routine" className="btn btn-primary">Follow Routine</Link>
                </section>
              </div>

              <div className="dashboard-lower">
                <section className="breakdown-panel">
                  <div className="section-header">
                    <h2>Skin Breakdown</h2>
                    <Link to="/history" className="view-all">View All</Link>
                  </div>
                  <div className="breakdown-list">
                    {breakdownRows.map((row) => (
                      <div key={row.label} className="breakdown-row">
                        <div className="breakdown-label">
                          <span>{row.label}</span>
                          <span className={`breakdown-tone ${row.tone}`}>{row.value}%</span>
                        </div>
                        <div className="breakdown-bar">
                          <div className={`breakdown-fill ${row.tone}`} style={{ width: `${row.value}%` }}></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                <section className="progress-panel">
                  <div className="section-header">
                    <h2>Progress Section</h2>
                  </div>
                  <div className="progress-main">
                    <div className="progress-score">
                      <span>{score - Math.abs(scoreChange)}</span>
                      <span className="progress-arrow">to</span>
                      <span>{score}</span>
                    </div>
                    <span className="progress-caption">Score improvement</span>
                  </div>
                  <ul className="progress-list">
                    <li>Acne score decreased by {Math.max(1, Math.abs(scoreChange) || 3)} points.</li>
                    <li>Oiliness is still high, but stable.</li>
                    <li>Hydration levels are slowly rising.</li>
                  </ul>
                </section>

                <div className="insights-stack">
                  <section className="insight-panel">
                    <div className="section-header">
                      <h2>AI Insights</h2>
                    </div>
                    <p>
                      Tip: With oily skin, consider using a salicylic acid cleanser for your morning
                      wash to manage oil production throughout the day.
                    </p>
                  </section>

                  <section className="latest-panel">
                    <div className="section-header">
                      <h2>Latest Scan</h2>
                    </div>
                    <p>{latestScan ? new Date(latestScan.created_at).toLocaleString('en-US') : 'No scans yet'}</p>
                    <Link to={latestScan ? `/scan/${latestScan.id}` : '/scan'} className="btn btn-outline">
                      View Full Report
                    </Link>
                  </section>
                </div>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default Dashboard
