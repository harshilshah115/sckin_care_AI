import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import Sidebar from '../../components/Sidebar/Sidebar'
import Loader from '../../components/Loader/Loader'
import { historyAPI } from '../../services/api'
import './Progress.css'

function Progress() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [timeRange, setTimeRange] = useState('month')
  const [loading, setLoading] = useState(true)
  const [skinScores, setSkinScores] = useState([])
  const [progressImages, setProgressImages] = useState([])

  useEffect(() => {
    loadProgressData()
  }, [])

  const loadProgressData = async () => {
    setLoading(true)
    try {
      const scansRes = await historyAPI.getScanHistory()
      const scans = scansRes.ok ? scansRes.data : []

      setProgressImages(scans)

      const scanScores = scans
        .filter((scan) => scan.created_at && typeof scan.skin_score === 'number')
        .map((scan) => ({
          date: scan.created_at,
          score: scan.skin_score
        }))
        .sort((a, b) => new Date(a.date) - new Date(b.date))

      setSkinScores(scanScores)
    } catch (error) {
      console.error('Error loading progress:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  const startOfDay = (date) => new Date(date.getFullYear(), date.getMonth(), date.getDate())

  const endOfDay = (date) => new Date(
    date.getFullYear(),
    date.getMonth(),
    date.getDate(),
    23,
    59,
    59,
    999
  )

  const startOfWeek = (date) => {
    const dayStart = startOfDay(date)
    const dayIndex = dayStart.getDay()
    const diff = (dayIndex + 6) % 7
    dayStart.setDate(dayStart.getDate() - diff)
    return dayStart
  }

  const getDateRange = () => {
    const now = new Date()
    const end = endOfDay(now)
    let start = null

    if (timeRange === 'week') {
      start = startOfWeek(now)
    }

    if (timeRange === 'month') {
      start = new Date(now.getFullYear(), now.getMonth(), 1)
    }

    if (timeRange === '3months') {
      start = new Date(now.getFullYear(), now.getMonth() - 2, 1)
    }

    if (timeRange === 'year') {
      start = new Date(now.getFullYear(), 0, 1)
    }

    return start ? { start: startOfDay(start), end } : null
  }

  const filterByRange = (items, getDate) => {
    const range = getDateRange()
    if (!range) return items

    return items.filter((item) => {
      const dateValue = new Date(getDate(item))
      if (Number.isNaN(dateValue.getTime())) return false
      return dateValue >= range.start && dateValue <= range.end
    })
  }

  const displayScores = useMemo(
    () => filterByRange(skinScores, (item) => item.date),
    [skinScores, timeRange]
  )

  const displayImages = useMemo(
    () => filterByRange(progressImages, (item) => item.created_at),
    [progressImages, timeRange]
  )

  const displayDaysTracked = displayScores.length
  const maxScore = displayScores.length > 0 ? Math.max(...displayScores.map((s) => s.score)) : 0
  const minScore = displayScores.length > 0 ? Math.min(...displayScores.map((s) => s.score)) : 0
  const scoreRange = maxScore - minScore || 1
  const scoreChange = displayScores.length > 0
    ? displayScores[displayScores.length - 1].score - displayScores[0].score
    : 0
  const hasAnyScores = skinScores.length > 0
  const hasFilteredScores = displayScores.length > 0

  return (
    <div className="dashboard-layout">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="dashboard-main">
        <header className="dashboard-header">
          <button className="mobile-menu-toggle" onClick={() => setSidebarOpen(true)}>
            <span className="material-symbols-outlined">menu</span>
          </button>

          <div className="page-title">
            <span className="material-symbols-outlined">trending_up</span>
            <h1>Skin Progress</h1>
          </div>

          <div className="header-actions">
            <select 
              className="range-select"
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="3months">3 Months</option>
              <option value="year">This Year</option>
            </select>
          </div>
        </header>

        <div className="progress-content">
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
              <Loader />
            </div>
          ) : !hasAnyScores ? (
            <div className="empty-state" style={{ textAlign: 'center', padding: '4rem' }}>
              <span className="material-symbols-outlined" style={{ fontSize: '4rem', opacity: 0.3 }}>trending_up</span>
              <h3>No Progress Data Yet</h3>
              <p>Complete at least 2 scans to track your progress</p>
              <Link to="/scan" className="btn btn-primary" style={{ marginTop: '1rem' }}>Start First Scan</Link>
            </div>
          ) : !hasFilteredScores ? (
            <div className="empty-state" style={{ textAlign: 'center', padding: '4rem' }}>
              <span className="material-symbols-outlined" style={{ fontSize: '4rem', opacity: 0.3 }}>trending_up</span>
              <h3>No progress in this range</h3>
              <p>Try a different filter to view more data.</p>
            </div>
          ) : (
            <>
              {/* Summary Cards */}
          <div className="summary-cards">
            <div className="summary-card highlight">
              <div className="summary-icon">
                <span className="material-symbols-outlined">spa</span>
              </div>
              <div className="summary-info">
                <span className="summary-value">{displayScores[displayScores.length - 1]?.score || 0}</span>
                <span className="summary-label">Current Score</span>
              </div>
            </div>
            <div className="summary-card">
              <div className="summary-icon positive">
                <span className="material-symbols-outlined">trending_up</span>
              </div>
              <div className="summary-info">
                <span className="summary-value">{scoreChange > 0 ? '+' : ''}{scoreChange}</span>
                <span className="summary-label">Improvement</span>
              </div>
            </div>
            <div className="summary-card">
              <div className="summary-icon">
                <span className="material-symbols-outlined">clinical_notes</span>
              </div>
              <div className="summary-info">
                <span className="summary-value">{displayImages.length}</span>
                <span className="summary-label">Scans</span>
              </div>
            </div>
            <div className="summary-card">
              <div className="summary-icon">
                <span className="material-symbols-outlined">calendar_month</span>
              </div>
              <div className="summary-info">
                <span className="summary-value">{displayDaysTracked}</span>
                <span className="summary-label">Days Tracked</span>
              </div>
            </div>
          </div>

          {/* Score Chart */}
          <div className="chart-card">
            <h3>Skin Health Score Over Time</h3>
            <div className="chart-container">
              <div className="chart-y-axis">
                <span>{maxScore}</span>
                <span>{Math.round((maxScore + minScore) / 2)}</span>
                <span>{minScore}</span>
              </div>
              <div className="chart-area">
                <div className="chart-grid">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="grid-line"></div>
                  ))}
                </div>
                <div className="chart-line">
                  <svg viewBox={`0 0 ${displayScores.length * 60} 100`} preserveAspectRatio="none">
                    <path
                      className="line-path"
                      d={displayScores.map((s, i) => {
                        const x = i * 60 + 30
                        const y = 100 - ((s.score - minScore) / scoreRange) * 80 - 10
                        return `${i === 0 ? 'M' : 'L'} ${x} ${y}`
                      }).join(' ')}
                    />
                    {displayScores.map((s, i) => {
                      const x = i * 60 + 30
                      const y = 100 - ((s.score - minScore) / scoreRange) * 80 - 10
                      return (
                        <circle key={i} cx={x} cy={y} r="4" className="data-point" />
                      )
                    })}
                  </svg>
                </div>
                <div className="chart-x-axis">
                  {displayScores.map((s, i) => (
                    <span key={i}>{formatDate(s.date)}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Progress Photos */}
          <div className="photos-section">
            <h3>Progress Photos</h3>
            <div className="photos-grid">
              {displayImages.map((img) => (
                <div key={img.id} className="photo-card">
                  <div className="photo-image">
                    {img.image ? (
                      <img src={img.image} alt={`Progress ${formatDate(img.created_at)}`} />
                    ) : (
                      <div className="scan-placeholder">
                        <span className="material-symbols-outlined">clinical_notes</span>
                      </div>
                    )}
                    <div className="photo-score">{img.skin_score}</div>
                  </div>
                  <div className="photo-info">
                    <span className="photo-date">{formatDate(img.created_at)}</span>
                    <p className="photo-notes">{img.notes || 'Skin scan'}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default Progress
