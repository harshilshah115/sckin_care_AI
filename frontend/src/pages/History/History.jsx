import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import Sidebar from '../../components/Sidebar/Sidebar'
import { historyAPI } from '../../services/api'
import Loader from '../../components/Loader/Loader'
import './History.css'

function History() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('scans')
  const [filterDate, setFilterDate] = useState('all')
  const [loading, setLoading] = useState(true)
  const [scanHistory, setScanHistory] = useState([])
  const [questionHistory, setQuestionHistory] = useState([])

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setLoading(true)
    
    try {
      const scansRes = await historyAPI.getScanHistory()
      const questionsRes = await historyAPI.getQuestionHistory()
      
      setScanHistory(scansRes.ok ? scansRes.data : [])
      setQuestionHistory(questionsRes.ok ? questionsRes.data : [])
    } catch (error) {
      console.error('Error loading history:', error)
    }
    
    setLoading(false)
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    
    if (date.toDateString() === today.toDateString()) {
      return 'Today'
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday'
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    }
  }

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'excellent'
    if (score >= 60) return 'good'
    return 'fair'
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
    if (filterDate === 'all') return null

    const now = new Date()
    const end = endOfDay(now)
    let start = null

    if (filterDate === 'week') {
      start = startOfWeek(now)
    }

    if (filterDate === 'month') {
      start = new Date(now.getFullYear(), now.getMonth(), 1)
    }

    return start ? { start, end } : null
  }

  const filterByRange = (items) => {
    const range = getDateRange()
    if (!range) return items

    return items.filter((item) => {
      const dateValue = new Date(item.created_at)
      if (Number.isNaN(dateValue.getTime())) return false
      return dateValue >= range.start && dateValue <= range.end
    })
  }

  const filteredScanHistory = useMemo(
    () => filterByRange(scanHistory),
    [scanHistory, filterDate]
  )

  const filteredQuestionHistory = useMemo(
    () => filterByRange(questionHistory),
    [questionHistory, filterDate]
  )

  return (
    <div className="dashboard-layout">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="dashboard-main">
        {/* Header */}
        <header className="dashboard-header">
          <button className="mobile-menu-toggle" onClick={() => setSidebarOpen(true)}>
            <span className="material-symbols-outlined">menu</span>
          </button>

          <div className="page-title">
            <span className="material-symbols-outlined">history</span>
            <h1>Activity History</h1>
          </div>

          <div className="header-actions">
            <select 
              className="filter-select"
              value={filterDate}
              onChange={(e) => setFilterDate(e.target.value)}
            >
              <option value="all">All Time</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
          </div>
        </header>

        {/* Content */}
        <div className="history-content">
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
              <Loader />
            </div>
          ) : (
            <>
              {/* Tabs */}
              <div className="history-tabs">
                <button 
                  className={`tab-btn ${activeTab === 'scans' ? 'active' : ''}`}
                  onClick={() => setActiveTab('scans')}
                >
                  <span className="material-symbols-outlined">clinical_notes</span>
                  Scan History
                  <span className="tab-count">{filteredScanHistory.length}</span>
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'questions' ? 'active' : ''}`}
                  onClick={() => setActiveTab('questions')}
                >
                  <span className="material-symbols-outlined">forum</span>
                  Chat History
                  <span className="tab-count">{filteredQuestionHistory.length}</span>
                </button>
              </div>

              {/* Scan History */}
              {activeTab === 'scans' && (
                <div className="history-list">
                  {filteredScanHistory.length > 0 ? (
                    filteredScanHistory.map((scan) => (
                      <Link key={scan.id} to={`/scan/${scan.id}`} className="history-card scan-card">
                        <div className="scan-image">
                          {scan.image ? (
                            <img src={scan.image} alt="Scan" />
                          ) : (
                            <div className="scan-placeholder">
                              <span className="material-symbols-outlined">clinical_notes</span>
                            </div>
                          )}
                        </div>
                        <div className="scan-details">
                          <div className="scan-header">
                            <span className="scan-type">{scan.scan_type?.replace('_', ' ') || 'Skin Scan'}</span>
                            <span className="scan-date">{formatDate(scan.created_at)} • {formatTime(scan.created_at)}</span>
                          </div>
                          <div className="scan-issues">
                            {scan.detected_issues?.slice(0, 3).map((issue, index) => (
                              <span key={index} className="issue-tag">{issue.name}</span>
                            ))}
                          </div>
                        </div>
                        <div className={`scan-score ${getScoreColor(scan.skin_score)}`}>
                          <span className="score-value">{scan.skin_score}</span>
                          <span className="score-label">Score</span>
                        </div>
                        <span className="material-symbols-outlined card-arrow">chevron_right</span>
                      </Link>
                    ))
                  ) : (
                    <div className="empty-state">
                      <span className="material-symbols-outlined">clinical_notes</span>
                      <h3>{scanHistory.length > 0 ? 'No scans in this range' : 'No scans yet'}</h3>
                      <p>{scanHistory.length > 0
                        ? 'Try a different filter to see earlier scans.'
                        : 'Start analyzing your skin to see your history here'}
                      </p>
                      <Link to="/scan" className="btn btn-primary">Start First Scan</Link>
                    </div>
                  )}
                </div>
              )}

              {/* Question History */}
              {activeTab === 'questions' && (
                <div className="history-list">
                  {filteredQuestionHistory.length > 0 ? (
                    filteredQuestionHistory.map((item) => (
                      <Link key={item.id} to={`/ask?history=${item.id}`} className="history-card question-card">
                        <div className="question-icon">
                          <span className="material-symbols-outlined">chat_bubble</span>
                        </div>
                        <div className="question-details">
                          <div className="question-header">
                            <span className="question-text">{item.question_text}</span>
                            <span className="question-date">{formatDate(item.created_at)} • {formatTime(item.created_at)}</span>
                          </div>
                          <p className="question-preview">
                            {item.answer_text?.substring(0, 150)}...
                          </p>
                        </div>
                        <span className="material-symbols-outlined card-arrow">chevron_right</span>
                      </Link>
                    ))
                  ) : (
                    <div className="empty-state">
                      <span className="material-symbols-outlined">forum</span>
                      <h3>{questionHistory.length > 0 ? 'No questions in this range' : 'No questions yet'}</h3>
                      <p>{questionHistory.length > 0
                        ? 'Try a different filter to see earlier questions.'
                        : 'Ask our AI assistant about skincare to see your chat history'}
                      </p>
                      <Link to="/ask" className="btn btn-primary">Ask AI</Link>
                    </div>
                  )}
                </div>
              )}

              {/* Stats Summary */}
              <div className="history-stats">
                <div className="stat-card">
                  <span className="material-symbols-outlined">clinical_notes</span>
                  <div className="stat-info">
                    <span className="stat-value">{filteredScanHistory.length}</span>
                    <span className="stat-label">Total Scans</span>
                  </div>
                </div>
                <div className="stat-card">
                  <span className="material-symbols-outlined">forum</span>
                  <div className="stat-info">
                    <span className="stat-value">{filteredQuestionHistory.length}</span>
                    <span className="stat-label">Questions Asked</span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}

export default History
