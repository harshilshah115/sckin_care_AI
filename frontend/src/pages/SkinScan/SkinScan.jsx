import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import Sidebar from '../../components/Sidebar/Sidebar'
import ImageUpload from '../../components/ImageUpload/ImageUpload'
import Loader from '../../components/Loader/Loader'
import { scanAPI } from '../../services/api'
import './SkinScan.css'

function SkinScan() {
  const { id: scanId } = useParams()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [selectedImage, setSelectedImage] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [loadingScan, setLoadingScan] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')
  const [actionTab, setActionTab] = useState('daily')
  const [userContext, setUserContext] = useState({
    age: '',
    skinType: '',
    sleepHours: '',
    waterIntake: ''
  })

  const ExpandableText = ({ text, maxChars = 200, className = '' }) => {
    const [expanded, setExpanded] = useState(false)
    if (!text) return null

    const normalized = String(text).replace(/\s+/g, ' ').trim()
    const isLong = normalized.length > maxChars
    const displayText = expanded || !isLong
      ? normalized
      : `${normalized.slice(0, maxChars).trim()}...`

    return (
      <span className={className}>
        {displayText}
        {isLong && (
          <button
            type="button"
            className="link-button"
            onClick={() => setExpanded((prev) => !prev)}
          >
            {expanded ? 'Show less' : 'Show more'}
          </button>
        )}
      </span>
    )
  }

  const handleImageSelect = (file) => {
    setSelectedImage(file)
    setResults(null)
    setError('')
  }

  const normalizeArray = (value) => {
    if (Array.isArray(value)) return value
    return value ? [value] : []
  }

  const normalizeFaceZones = (faceZones) => {
    if (!faceZones) return []
    if (Array.isArray(faceZones)) return faceZones
    if (typeof faceZones !== 'object') return []

    return Object.entries(faceZones).map(([zone, details]) => {
      if (!details || typeof details !== 'object') {
        return { zone, conditions: [], severity: 'mild' }
      }

      const issues = normalizeArray(details.issues)
      const conditions = issues.length
        ? issues.map((name) => ({ name, severity: details.severity || 'mild' }))
        : Object.entries(details).map(([name, severity]) => ({ name, severity }))

      return {
        zone,
        conditions,
        severity: details.severity || 'mild'
      }
    })
  }

  const normalizeAlerts = (alerts) => (
    normalizeArray(alerts).map((alert) => {
      const message = typeof alert === 'string'
        ? alert
        : alert?.message || alert?.text || String(alert)

      return { message: String(message).replace(/\s+/g, ' ').trim() }
    })
  )

  const normalizeRiskFlags = (riskFlags) => {
    if (Array.isArray(riskFlags)) return riskFlags
    if (riskFlags && typeof riskFlags === 'object') return Object.keys(riskFlags)
    return riskFlags ? [riskFlags] : []
  }

  const formatMetricValue = (value) => {
    if (value && typeof value === 'object') {
      const level = value.level || value.status || ''
      const score = value.score ?? value.value ?? ''
      if (level && score !== '') return `${level} (${score})`
      if (level) return level
      if (score !== '') return String(score)
    }
    if (typeof value === 'string') return value
    return value ?? '—'
  }

  const formatTitleCase = (value) => (
    String(value || '')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase())
  )

  const getScoreTone = (score) => {
    if (score >= 70) return 'good'
    if (score >= 40) return 'moderate'
    return 'poor'
  }

  const getSeverityTone = (severity) => {
    const normalized = String(severity || '').toLowerCase()
    if (['refer_to_doctor', 'severe', 'critical'].includes(normalized)) return 'severe'
    if (['high', 'moderate', 'medium'].includes(normalized)) return 'high'
    if (['mild', 'low'].includes(normalized)) return 'mild'
    return 'mild'
  }

  const getSeverityRank = (severity) => {
    const tone = getSeverityTone(severity)
    if (tone === 'severe') return 3
    if (tone === 'high') return 2
    return 1
  }

  const getMetricScore = (value) => {
    if (value && typeof value === 'object') {
      const score = value.score ?? value.value
      if (typeof score === 'number') return Math.max(0, Math.min(score, 100))
      const level = String(value.level || value.status || '').toLowerCase()
      if (level.includes('high')) return 85
      if (level.includes('moderate')) return 55
      if (level.includes('low')) return 25
      if (level.includes('poor')) return 20
      if (level.includes('good')) return 75
    }
    if (typeof value === 'string') {
      const level = value.toLowerCase()
      if (level.includes('high')) return 85
      if (level.includes('very')) return 85
      if (level.includes('moderate')) return 55
      if (level.includes('low')) return 25
      if (level.includes('poor')) return 20
      if (level.includes('good')) return 75
    }
    if (typeof value === 'number') return Math.max(0, Math.min(value, 100))
    return 0
  }

  const buildIssueSeverityMap = (issues) => {
    const map = new Map()
    issues.forEach((issue) => {
      if (!issue?.name) return
      map.set(String(issue.name).toLowerCase(), getSeverityTone(issue.severity))
    })
    return map
  }

  const describeMetric = (key, value) => {
    const level = value?.level || value?.status || value || ''
    const normalized = String(level).toLowerCase()
    if (key === 'oiliness' && normalized.includes('high')) return 'High oiliness may clog pores and worsen acne.'
    if (key === 'hydration' && normalized.includes('moderate')) return 'Hydration is moderate. Support barrier repair with gentle moisturizers.'
    if (key === 'texture' && normalized.includes('rough')) return 'Rough texture suggests uneven cell turnover.'
    if (key === 'pore_visibility' && normalized.includes('high')) return 'Visible pores can indicate excess sebum and congestion.'
    if (key === 'pigmentation' && normalized.includes('significant')) return 'Pigmentation is elevated. Sun protection is essential.'
    if (key === 'overall_health' && normalized.includes('compromised')) return 'Overall health is compromised. Focus on gentle recovery.'
    return 'Monitor this metric and adjust your routine if it worsens.'
  }

  const formatRiskFlag = (flag) => {
    const map = {
      barrier_damage: 'Skin Barrier Damage Risk: your skin may be irritated and sensitive.',
      acne_worsening: 'Acne Worsening Risk: without treatment, breakouts may spread or scar.',
      pigmentation_risk: 'Pigmentation Risk: dark spots may increase over time.'
    }
    return map[flag] || formatTitleCase(flag)
  }

  const formatCause = (cause) => {
    const map = {
      'hormonal fluctuations': 'Hormonal fluctuations can trigger breakouts and oiliness.',
      'excess sebum production': 'Excess sebum clogs pores and fuels acne.',
      'bacterial overgrowth': 'Bacterial overgrowth increases inflammation and irritation.',
      inflammation: 'Inflammation worsens redness and slows healing.'
    }
    const key = String(cause || '').toLowerCase()
    return map[key] || formatTitleCase(cause)
  }

  const coerceList = (value) => (Array.isArray(value) ? value : (value ? [value] : []))

  const buildBenefits = (item, fallbackKey) => {
    const benefits = coerceList(item?.benefits)
    if (benefits.length) return benefits
    if (item?.benefit) return [item.benefit]
    if (item?.description) return [item.description]
    if (fallbackKey && item?.[fallbackKey]) return [item[fallbackKey]]
    return []
  }

  const normalizeRecommendations = (recommendations = {}) => {
    const natural = normalizeArray(recommendations.natural).map((item) => {
      if (typeof item === 'string') {
        return { name: item, benefits: [] }
      }
      return {
        name: item?.name || item?.remedy || item?.title || 'Natural remedy',
        benefits: buildBenefits(item)
      }
    })

    const cosmetic = normalizeArray(recommendations.cosmetic).map((item) => {
      if (typeof item === 'string') {
        return { suggestion: item, category: '', key_ingredients: [] }
      }
      return {
        suggestion: item?.suggestion || item?.name || item?.type || 'Cosmetic product',
        category: item?.category || item?.type || '',
        key_ingredients: item?.key_ingredients || item?.ingredients || []
      }
    })

    const otc = normalizeArray(recommendations.otc).map((item) => {
      if (typeof item === 'string') {
        return { ingredient: item, concentration: '', benefits: [] }
      }
      return {
        ingredient: item?.ingredient || item?.name || item?.type || 'OTC ingredient',
        concentration: item?.concentration || '',
        benefits: buildBenefits(item, 'use')
      }
    })

    const lifestyle = normalizeArray(recommendations.lifestyle).map((item) => (
      typeof item === 'string' ? item : (item?.tip || item?.name || String(item))
    ))

    return { natural, cosmetic, otc, lifestyle }
  }

  const buildResultsFromScan = (scanData) => {
    const scan = scanData?.scan || scanData || {}
    const recommendations = scan.recommendations || {}
    const analysis = recommendations.analysis || scan.analysis || scan || {}
    const meta = recommendations.meta || scan.meta || {}
    const normalizedRecommendations = normalizeRecommendations(recommendations)

    return {
      overallScore: scan.skin_score || analysis.skin_score || 75,
      skinTypeDetected: analysis.skin_type_detected || scan.skin_type_detected || null,
      analysisText: scan.analysis_text || scan.analysis_text_preview || analysis.overall_assessment || '',
      imageQuality: meta.image_quality || scan.image_quality || null,
      metrics: analysis.metrics || scan.metrics || {},
      faceZones: normalizeFaceZones(analysis.face_zones || scan.face_zones),
      causes: analysis.probable_causes || scan.probable_causes || [],
      risks: normalizeRiskFlags(analysis.risk_flags || scan.risk_flags || []),
      issues: normalizeArray(analysis.detected_issues || scan.detected_issues || []).map((issue) => ({
        name: issue.name || 'Unspecified issue',
        severity: issue.severity || 'mild',
        confidence: issue.confidence ?? 0,
        description: issue.description || (issue.zones ? `Zones: ${issue.zones.join(', ')}` : '')
      })),
      recommendations: normalizedRecommendations,
      routine: recommendations.routine || scan.routine || {},
      progress: recommendations.progress_tracking || scan.progress_tracking || {},
      alerts: normalizeAlerts(recommendations.alerts || scan.alerts || [])
    }
  }

  useEffect(() => {
    const loadScanDetail = async () => {
      if (!scanId) return
      setLoadingScan(true)
      setError('')

      try {
        const { ok, data } = await scanAPI.getScanDetail(scanId)
        if (ok) {
          setResults(buildResultsFromScan(data))
        } else {
          setError(data?.detail || data?.error || 'Unable to load scan report.')
        }
      } catch (err) {
        console.error('Scan detail error:', err)
        setError('Unable to load scan report. Please try again.')
      } finally {
        setLoadingScan(false)
      }
    }

    loadScanDetail()
  }, [scanId])

  const handleAnalyze = async () => {
    if (!selectedImage) return

    setAnalyzing(true)
    setError('')
    
    try {
      const { ok, data } = await scanAPI.uploadScan(selectedImage, 'full_face', userContext)
      
      if (ok) {
        if (data.error || data.fallback) {
          setError(data.error || data.message || 'AI analysis failed. Please try again.')
          setResults(null)
          return
        }

        setResults(buildResultsFromScan(data))
      } else {
        setError(data.detail || data.error || 'Analysis failed. Please try again.')
      }
    } catch (err) {
      setError('Unable to connect to server. Please check your connection.')
      console.error('Scan error:', err)
    }
    
    setAnalyzing(false)
  }

  const handleReset = () => {
    setSelectedImage(null)
    setResults(null)
    setError('')
    setUserContext({
      age: '',
      skinType: '',
      sleepHours: '',
      waterIntake: ''
    })
  }

  const handleContextChange = (field, value) => {
    setUserContext((prev) => ({
      ...prev,
      [field]: value
    }))
  }

  const scoreTone = results ? getScoreTone(results.overallScore) : 'moderate'
  const highRisk = results
    ? results.issues.some((issue) => getSeverityTone(issue.severity) === 'severe')
    : false
  const issueSeverityMap = results ? buildIssueSeverityMap(results.issues) : new Map()
  const worstIssue = results?.issues
    ?.slice()
    .sort((a, b) => getSeverityRank(b.severity) - getSeverityRank(a.severity))[0]
  const heroSummary = results
    ? `${formatTitleCase(results.skinTypeDetected?.type || 'Skin')} ${worstIssue ? `with ${worstIssue.name}` : ''}`.trim()
    : ''
  const improvementTip = results?.recommendations?.lifestyle?.[0] || 'Start a gentle routine and avoid picking.'
  const treatmentItems = results
    ? [
        ...results.recommendations.otc.map((item) => item.ingredient || String(item)),
        ...results.recommendations.cosmetic.map((item) => item.suggestion || String(item))
      ].filter(Boolean)
    : []
  const groupedIssues = results
    ? results.issues.reduce(
        (acc, issue) => {
          const tone = getSeverityTone(issue.severity)
          if (!acc[tone]) acc[tone] = []
          acc[tone].push(issue)
          return acc
        },
        { severe: [], high: [], mild: [] }
      )
    : { severe: [], high: [], mild: [] }
  const actionsStart = results
    ? [
        ...results.recommendations.lifestyle.slice(0, 2),
        ...(results.routine.morning || []).slice(0, 2).map((step) => step.action || step)
      ].filter(Boolean)
    : []
  const actionsNext = results
    ? [
        ...(results.routine.night || []).slice(0, 2).map((step) => step.action || step),
        ...results.recommendations.otc.slice(0, 2).map((item) => item.ingredient)
      ].filter(Boolean)
    : []
  const actionsOptional = results
    ? results.recommendations.natural.map((item) => item.name).filter(Boolean)
    : []
  const actionsAvoid = results
    ? results.recommendations.cosmetic
        .map((item) => item.suggestion)
        .filter((text) => String(text).toLowerCase().includes('avoid'))
    : []
  const routineMorning = results
    ? (results.routine.morning || []).map((step) => step.action || step)
    : []
  const routineNight = results
    ? (results.routine.night || []).map((step) => step.action || step)
    : []
  const routineWeekly = results
    ? (results.routine.weekly || []).map((step) => step.action || step)
    : []
  const zoneGroups = results
    ? results.faceZones.reduce(
        (acc, zone) => {
          const issues = zone.conditions || []
          const detectedIssues = zone.detected_issues || []
          const names = [
            ...issues.map((condition) => condition.name),
            ...detectedIssues
          ].filter(Boolean)
          const severityScores = names.map((name) => issueSeverityMap.get(String(name).toLowerCase()) || 'mild')
          const group = severityScores.includes('severe')
            ? 'problem'
            : severityScores.includes('high')
              ? 'mild'
              : names.length
                ? 'mild'
                : 'clear'
          acc[group].push({
            name: formatTitleCase(zone.zone),
            summary: names.length ? names.map(formatTitleCase).join(', ') : 'No issues'
          })
          return acc
        },
        { problem: [], mild: [], clear: [] }
      )
    : { problem: [], mild: [], clear: [] }

  return (
    <div className="dashboard-layout">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="dashboard-main">
        {/* Top Bar */}
        <header className="dashboard-header">
          <button 
            className="mobile-menu-toggle"
            onClick={() => setSidebarOpen(true)}
          >
            <span className="material-symbols-outlined">menu</span>
          </button>

          <div className="page-title">
            <span className="material-symbols-outlined">clinical_notes</span>
            <h1>AI Skin Analysis</h1>
          </div>

          <div className="header-actions">
            <button className="header-btn">
              <span className="material-symbols-outlined">help</span>
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="scan-content">
          {!results ? (
            <>
              {/* Upload Section */}
              <section className="upload-section">
                <div className="section-intro">
                  <h2>Upload Your Skin Photo</h2>
                  <p>Our AI will analyze your skin and provide personalized recommendations.</p>
                </div>

                <ImageUpload 
                  onImageSelect={handleImageSelect}
                  disabled={analyzing}
                />

                <div className="context-section">
                  <div className="context-header">
                    <h3>Personal Context (Optional)</h3>
                    <p>Helps the AI provide more accurate skin insights.</p>
                  </div>
                  <div className="context-grid">
                    <label className="context-field">
                      <span>Age</span>
                      <input
                        type="number"
                        min="0"
                        placeholder="e.g., 24"
                        value={userContext.age}
                        onChange={(e) => handleContextChange('age', e.target.value)}
                        disabled={analyzing}
                      />
                    </label>
                    <label className="context-field">
                      <span>Skin Type</span>
                      <select
                        value={userContext.skinType}
                        onChange={(e) => handleContextChange('skinType', e.target.value)}
                        disabled={analyzing}
                      >
                        <option value="">Select</option>
                        <option value="oily">Oily</option>
                        <option value="dry">Dry</option>
                        <option value="combination">Combination</option>
                        <option value="normal">Normal</option>
                        <option value="sensitive">Sensitive</option>
                      </select>
                    </label>
                    <label className="context-field">
                      <span>Sleep (hours/night)</span>
                      <input
                        type="number"
                        min="0"
                        step="0.5"
                        placeholder="e.g., 7.5"
                        value={userContext.sleepHours}
                        onChange={(e) => handleContextChange('sleepHours', e.target.value)}
                        disabled={analyzing}
                      />
                    </label>
                    <label className="context-field">
                      <span>Water Intake (liters/day)</span>
                      <input
                        type="number"
                        min="0"
                        step="0.1"
                        placeholder="e.g., 2"
                        value={userContext.waterIntake}
                        onChange={(e) => handleContextChange('waterIntake', e.target.value)}
                        disabled={analyzing}
                      />
                    </label>
                  </div>
                </div>

                {error && (
                  <div className="scan-error">
                    <span className="material-symbols-outlined">error</span>
                    {error}
                  </div>
                )}

                {loadingScan && (
                  <div className="analyzing-status">
                    <div className="status-item active">
                      <span className="material-symbols-outlined">sync</span>
                      Loading scan report...
                    </div>
                  </div>
                )}

                {selectedImage && (
                  <div className="analyze-actions">
                    <button 
                      className="btn btn-primary btn-lg"
                      onClick={handleAnalyze}
                      disabled={analyzing}
                    >
                      {analyzing ? (
                        <>
                          <Loader size="small" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <span className="material-symbols-outlined">scan</span>
                          Start Analysis
                        </>
                      )}
                    </button>
                  </div>
                )}

                {analyzing && (
                  <div className="analyzing-status">
                    <div className="status-item active">
                      <span className="material-symbols-outlined">check_circle</span>
                      Image uploaded
                    </div>
                    <div className="status-item active">
                      <span className="material-symbols-outlined">sync</span>
                      Analyzing skin markers...
                    </div>
                    <div className="status-item">
                      <span className="material-symbols-outlined">radio_button_unchecked</span>
                      Generating recommendations
                    </div>
                  </div>
                )}
              </section>

              {/* Tips Section */}
              <section className="tips-section">
                <h3>Tips for Best Results</h3>
                <div className="tips-grid">
                  <div className="tip-card">
                    <span className="material-symbols-outlined">light_mode</span>
                    <h4>Good Lighting</h4>
                    <p>Natural daylight works best. Avoid harsh shadows.</p>
                  </div>
                  <div className="tip-card">
                    <span className="material-symbols-outlined">face</span>
                    <h4>Clean Face</h4>
                    <p>Remove makeup for accurate analysis.</p>
                  </div>
                  <div className="tip-card">
                    <span className="material-symbols-outlined">center_focus_strong</span>
                    <h4>Clear Focus</h4>
                    <p>Keep the camera steady and in focus.</p>
                  </div>
                  <div className="tip-card">
                    <span className="material-symbols-outlined">straighten</span>
                    <h4>Face Forward</h4>
                    <p>Look directly at the camera.</p>
                  </div>
                </div>
              </section>
            </>
          ) : (
            /* Results Section */
            <section className="results-section">
              <div className="results-header">
                <div className="results-title">
                  <h2>Analysis Complete</h2>
                  <p>Here's what we found about your skin</p>
                </div>
                <button className="btn btn-secondary" onClick={handleReset}>
                  <span className="material-symbols-outlined">refresh</span>
                  New Scan
                </button>
              </div>

              {/* Hero Summary */}
              <div className={`hero-card tone-${scoreTone}`}>
                <div className="hero-score">
                  <svg className="hero-ring" viewBox="0 0 100 100">
                    <circle className="hero-ring-bg" cx="50" cy="50" r="45" />
                    <circle
                      className="hero-ring-fill"
                      cx="50" cy="50" r="45"
                      strokeDasharray={`${results.overallScore * 2.83} 283`}
                    />
                  </svg>
                  <div className="hero-score-value">
                    <span>{results.overallScore}</span>
                    <small>{scoreTone} score</small>
                  </div>
                </div>
                <div className="hero-content">
                  <h3>{heroSummary || 'Skin analysis summary'}</h3>
                  <p>
                    {results.analysisText ? (
                      <ExpandableText text={results.analysisText} maxChars={220} />
                    ) : (
                      'Your skin shows key areas that need targeted care and a gentle routine.'
                    )}
                  </p>
                  <div className={`risk-pill ${highRisk ? 'risk-high' : 'risk-normal'}`}>
                    {highRisk ? 'High Risk: Consult Dermatologist' : 'Routine Care Recommended'}
                  </div>
                  <div className="hero-tip">Tip: {improvementTip}</div>
                </div>
              </div>

              {/* Alerts */}
              {results.alerts.length > 0 && (
                <div className="alert-hero">
                  <div className="alert-hero-header">
                    <span className="material-symbols-outlined">warning</span>
                    <h3>Immediate Attention</h3>
                  </div>
                  <p>Your skin condition shows signs that require professional guidance.</p>
                  <button className="btn btn-primary alert-cta" type="button">
                    Book Consultation
                  </button>
                  <ul>
                    {results.alerts.map((alert, index) => (
                      <li key={index}>{alert.message}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Key Issues */}
              <div className="issues-section">
                <div className="section-title">
                  <h3>Key Issues</h3>
                  <p>Most impactful concerns ranked by severity.</p>
                </div>
                <div className="issue-groups">
                  {groupedIssues.severe.length > 0 && (
                    <div className="issue-group">
                      <h4>Severe Issues</h4>
                      <ul>
                        {groupedIssues.severe.map((issue, index) => (
                          <li key={index}>
                            <span>{formatTitleCase(issue.name)}</span>
                            <span className="issue-pill">{formatTitleCase(issue.severity)}</span>
                            <span className="issue-confidence">{issue.confidence}%</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {groupedIssues.high.length > 0 && (
                    <div className="issue-group">
                      <h4>High Impact</h4>
                      <ul>
                        {groupedIssues.high.map((issue, index) => (
                          <li key={index}>
                            <span>{formatTitleCase(issue.name)}</span>
                            <span className="issue-pill">{formatTitleCase(issue.severity)}</span>
                            <span className="issue-confidence">{issue.confidence}%</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {groupedIssues.mild.length > 0 && (
                    <div className="issue-group">
                      <h4>Moderate</h4>
                      <ul>
                        {groupedIssues.mild.map((issue, index) => (
                          <li key={index}>
                            <span>{formatTitleCase(issue.name)}</span>
                            <span className="issue-pill">{formatTitleCase(issue.severity)}</span>
                            <span className="issue-confidence">{issue.confidence}%</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>

              {/* What You Should Do */}
              <div className="action-section">
                <div className="section-title">
                  <h3>What You Should Do</h3>
                  <p>Actionable steps based on your skin profile.</p>
                </div>
                <div className="action-card">
                  <div className="action-grid">
                    <div>
                      <h4>Start Immediately</h4>
                      <ul>
                        {actionsStart.length ? actionsStart.map((item, index) => (
                          <li key={index}>{item}</li>
                        )) : <li>Follow a gentle routine and avoid picking.</li>}
                      </ul>
                    </div>
                    <div>
                      <h4>Add Next</h4>
                      <ul>
                        {actionsNext.length ? actionsNext.map((item, index) => (
                          <li key={index}>{item}</li>
                        )) : <li>Add supportive treatments once irritation calms.</li>}
                      </ul>
                    </div>
                    <div>
                      <h4>Optional / Natural</h4>
                      <ul>
                        {actionsOptional.length ? actionsOptional.map((item, index) => (
                          <li key={index}>{item}</li>
                        )) : <li>No natural options available.</li>}
                      </ul>
                    </div>
                    <div>
                      <h4>Avoid</h4>
                      <ul>
                        {actionsAvoid.length ? actionsAvoid.map((item, index) => (
                          <li key={index}>{item}</li>
                        )) : <li>Harsh scrubs and over-exfoliation.</li>}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Skin Metrics */}
              <div className="metrics-section">
                <div className="section-title">
                  <h3>Skin Metrics</h3>
                  <p>Focus areas highlighted by the analysis.</p>
                </div>
                <div className="metrics-bars">
                  {Object.entries(results.metrics || {}).map(([key, value]) => (
                    <div key={key} className="metric-row">
                      <div className="metric-header">
                        <span>{formatTitleCase(key)}</span>
                        <span>{formatMetricValue(value)}</span>
                      </div>
                      <div className="metric-track">
                        <div
                          className="metric-fill"
                          style={{ width: `${getMetricScore(value)}%` }}
                        ></div>
                      </div>
                      <p className="metric-description">{describeMetric(key, value)}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Face Zone Analysis */}
              <div className="zone-section">
                <div className="section-title">
                  <h3>Face Zone Analysis</h3>
                  <p>Where the issues are concentrated.</p>
                </div>
                <div className="zone-group">
                  <div>
                    <h4>Problem Areas</h4>
                    {zoneGroups.problem.length ? zoneGroups.problem.map((zone, index) => (
                      <div key={index} className="zone-row">
                        <span className="zone-name">{zone.name}</span>
                        <span className="zone-details">{zone.summary}</span>
                      </div>
                    )) : <div className="zone-row">No high concern zones.</div>}
                  </div>
                  <div>
                    <h4>Mild Areas</h4>
                    {zoneGroups.mild.length ? zoneGroups.mild.map((zone, index) => (
                      <div key={index} className="zone-row">
                        <span className="zone-name">{zone.name}</span>
                        <span className="zone-details">{zone.summary}</span>
                      </div>
                    )) : <div className="zone-row">No mild concern zones.</div>}
                  </div>
                  <div>
                    <h4>Clear Areas</h4>
                    {zoneGroups.clear.length ? zoneGroups.clear.map((zone, index) => (
                      <div key={index} className="zone-row">
                        <span className="zone-name">{zone.name}</span>
                        <span className="zone-details">{zone.summary}</span>
                      </div>
                    )) : <div className="zone-row">No clear zones reported.</div>}
                  </div>
                </div>
              </div>

              {/* Root Causes */}
              <div className="causes-section">
                <div className="section-title">
                  <h3>Likely Root Causes</h3>
                  <p>Insights driving the recommendations.</p>
                </div>
                <ul className="cause-list">
                  {results.causes.length ? (
                    results.causes.map((cause, index) => (
                      <li key={index}>{formatCause(cause)}</li>
                    ))
                  ) : (
                    <li>No root causes detected.</li>
                  )}
                </ul>
              </div>

              {/* Routine Plan */}
              <div className="routine-section">
                <div className="section-title">
                  <h3>Daily Routine</h3>
                  <p>Suggested steps to follow consistently.</p>
                </div>
                <div className="routine-grid">
                  <div className="routine-card">
                    <h4>Morning</h4>
                    <ol>
                      {routineMorning.length ? routineMorning.map((step, index) => (
                        <li key={index}>{step}</li>
                      )) : <li>No morning routine recommended.</li>}
                    </ol>
                  </div>
                  <div className="routine-card">
                    <h4>Night</h4>
                    <ol>
                      {routineNight.length ? routineNight.map((step, index) => (
                        <li key={index}>{step}</li>
                      )) : <li>No night routine recommended.</li>}
                    </ol>
                  </div>
                  <div className="routine-card">
                    <h4>Weekly</h4>
                    <ul>
                      {routineWeekly.length ? routineWeekly.map((step, index) => (
                        <li key={index}>{step}</li>
                      )) : <li>No weekly treatments recommended.</li>}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Progress Tracking */}
              <div className="progress-section">
                <div className="section-title">
                  <h3>Progress Tracking</h3>
                  <p>Track improvement across weekly scans.</p>
                </div>
                <div className="progress-card">
                  <h4>No previous scans found</h4>
                  <p>Take weekly scans to see how your skin score improves over time.</p>
                  <div className="progress-highlight">Improvement potential: High</div>
                  <p>With proper care, your score can improve to 60–70 in 6–8 weeks.</p>
                </div>
              </div>

              {/* Advanced Details */}
              <div className="advanced-section">
                <div className="section-title">
                  <h3>Advanced Details</h3>
                  <p>Technical context from the AI analysis.</p>
                </div>
                <div className="advanced-grid">
                  <div className="advanced-card">
                    <h4>Image Quality</h4>
                    {results.imageQuality ? (
                      <ul>
                        <li>Lighting: {results.imageQuality.lighting}</li>
                        <li>Blur: {results.imageQuality.blur}</li>
                        <li>Angle: {results.imageQuality.angle}</li>
                        <li>Confidence: {results.imageQuality.confidence}%</li>
                      </ul>
                    ) : (
                      <p className="muted">No image quality data available.</p>
                    )}
                  </div>
                  <div className="advanced-card">
                    <h4>Risk Flags</h4>
                    <ul>
                      {results.risks.length ? (
                        results.risks.map((risk, index) => (
                          <li key={index}>{formatRiskFlag(risk)}</li>
                        ))
                      ) : (
                        <li>No risk flags detected.</li>
                      )}
                    </ul>
                  </div>
                </div>
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  )
}

export default SkinScan
