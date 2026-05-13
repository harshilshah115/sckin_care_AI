import { useState, useRef } from 'react'
import './ImageUpload.css'

function ImageUpload({ onImageSelect, disabled = false }) {
  const [dragActive, setDragActive] = useState(false)
  const [preview, setPreview] = useState(null)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file) => {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB')
      return
    }

    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result)
    }
    reader.readAsDataURL(file)

    // Pass file to parent
    onImageSelect(file)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleRemove = (e) => {
    e.stopPropagation()
    setPreview(null)
    onImageSelect(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div 
      className={`image-upload ${dragActive ? 'drag-active' : ''} ${preview ? 'has-preview' : ''} ${disabled ? 'disabled' : ''}`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={!preview ? handleClick : undefined}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleChange}
        className="upload-input"
        disabled={disabled}
      />

      {preview ? (
        <div className="preview-container">
          <img src={preview} alt="Preview" className="preview-image" />
          <div className="preview-overlay">
            <button className="preview-btn change-btn" onClick={handleClick}>
              <span className="material-symbols-outlined">refresh</span>
              Change
            </button>
            <button className="preview-btn remove-btn" onClick={handleRemove}>
              <span className="material-symbols-outlined">delete</span>
              Remove
            </button>
          </div>
          <div className="preview-badge">
            <span className="material-symbols-outlined">check_circle</span>
            Ready to analyze
          </div>
        </div>
      ) : (
        <div className="upload-content">
          <div className="upload-icon">
            <span className="material-symbols-outlined">cloud_upload</span>
          </div>
          <div className="upload-text">
            <p className="upload-title">Drag & drop your skin photo</p>
            <p className="upload-subtitle">or click to browse</p>
          </div>
          <div className="upload-hints">
            <span className="hint">
              <span className="material-symbols-outlined">photo_camera</span>
              Clear, well-lit photo
            </span>
            <span className="hint">
              <span className="material-symbols-outlined">face</span>
              Face the camera directly
            </span>
            <span className="hint">
              <span className="material-symbols-outlined">image</span>
              Max 10MB, JPG/PNG
            </span>
          </div>
        </div>
      )}

      {/* Scan animation overlay */}
      {dragActive && (
        <div className="drag-overlay">
          <span className="material-symbols-outlined">add_photo_alternate</span>
          <span>Drop to upload</span>
        </div>
      )}
    </div>
  )
}

export default ImageUpload
