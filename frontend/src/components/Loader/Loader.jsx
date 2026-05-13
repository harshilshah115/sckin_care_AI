import './Loader.css'

function Loader({ size = 'medium', text = '' }) {
  return (
    <div className={`loader-container loader-${size}`}>
      <div className="loader-spinner">
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-core"></div>
      </div>
      {text && <p className="loader-text">{text}</p>}
    </div>
  )
}

export function PageLoader({ text = 'Loading...' }) {
  return (
    <div className="page-loader">
      <Loader size="large" text={text} />
    </div>
  )
}

export function ButtonLoader() {
  return (
    <div className="button-loader">
      <div className="dot"></div>
      <div className="dot"></div>
      <div className="dot"></div>
    </div>
  )
}

export default Loader
