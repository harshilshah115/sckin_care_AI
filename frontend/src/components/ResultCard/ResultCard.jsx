import './ResultCard.css'

function ResultCard({ icon, title, description, severity, actions, children }) {
  return (
    <div className={`result-card ${severity ? `severity-${severity}` : ''}`}>
      <div className="result-card-header">
        {icon && <span className="material-symbols-outlined result-icon">{icon}</span>}
        <div className="result-card-title">
          <h3>{title}</h3>
          {description && <p>{description}</p>}
        </div>
        {severity && (
          <span className={`severity-badge ${severity}`}>{severity}</span>
        )}
      </div>
      {children && <div className="result-card-body">{children}</div>}
      {actions && <div className="result-card-actions">{actions}</div>}
    </div>
  )
}

export default ResultCard