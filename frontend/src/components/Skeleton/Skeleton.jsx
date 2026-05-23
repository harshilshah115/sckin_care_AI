import './Skeleton.css'

function Skeleton({ width, height, variant = 'text', count = 1, className = '' }) {
  const items = Array.from({ length: count }, (_, i) => i)

  return (
    <div className={`skeleton-group ${className}`}>
      {items.map(i => (
        <div
          key={i}
          className={`skeleton skeleton-${variant}`}
          style={{
            width: width || (variant === 'circle' ? height || '40px' : '100%'),
            height: height || (variant === 'text' ? '1rem' : variant === 'circle' ? '40px' : '100px'),
          }}
        />
      ))}
    </div>
  )
}

export function SkeletonCard({ lines = 3, imageHeight = '200px' }) {
  return (
    <div className="skeleton-card">
      <Skeleton variant="rect" height={imageHeight} />
      <div className="skeleton-card-body">
        <Skeleton width="60%" height="0.75rem" />
        <Skeleton width="80%" height="1rem" />
        <Skeleton width="40%" height="0.75rem" count={lines - 2} />
      </div>
    </div>
  )
}

export function SkeletonTable({ rows = 5, cols = 4 }) {
  return (
    <div className="skeleton-table">
      {Array.from({ length: rows }, (_, r) => (
        <div key={r} className="skeleton-table-row">
          {Array.from({ length: cols }, (_, c) => (
            <Skeleton key={c} width={`${80 / cols}%`} height="1rem" />
          ))}
        </div>
      ))}
    </div>
  )
}

export default Skeleton