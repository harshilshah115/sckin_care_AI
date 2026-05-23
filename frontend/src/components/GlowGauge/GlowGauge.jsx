import './GlowGauge.css'

function GlowGauge({ score = 0, size = 160, strokeWidth = 10, label = 'Glow Score' }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const clampedScore = Math.max(0, Math.min(100, score))
  const offset = circumference - (clampedScore / 100) * circumference

  const getColor = () => {
    if (clampedScore >= 80) return '#22c55e'
    if (clampedScore >= 60) return '#4edea3'
    if (clampedScore >= 40) return '#f59e0b'
    if (clampedScore >= 20) return '#f97316'
    return '#ef4444'
  }

  const getLevel = () => {
    if (clampedScore >= 80) return 'Excellent'
    if (clampedScore >= 60) return 'Good'
    if (clampedScore >= 40) return 'Fair'
    if (clampedScore >= 20) return 'Needs Care'
    return 'Critical'
  }

  return (
    <div className="glow-gauge" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="glow-gauge-svg">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--border-color)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getColor()}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          className="glow-gauge-arc"
        />
      </svg>
      <div className="glow-gauge-center">
        <span className="glow-gauge-score" style={{ color: getColor() }}>{clampedScore}</span>
        <span className="glow-gauge-label">{label}</span>
        <span className="glow-gauge-level" style={{ color: getColor() }}>{getLevel()}</span>
      </div>
    </div>
  )
}

export default GlowGauge