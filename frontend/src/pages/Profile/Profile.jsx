import { useState, useEffect } from 'react'
import Sidebar from '../../components/Sidebar/Sidebar'
import { useAuth } from '../../context/AuthContext'
import Loader from '../../components/Loader/Loader'
import './Profile.css'

function Profile() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activeSection, setActiveSection] = useState('profile')
  const [isEditing, setIsEditing] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [loading, setLoading] = useState(false)
  const { user, updateUser } = useAuth()

  const [profile, setProfile] = useState({
    name: '',
    email: '',
    phone: '',
    avatar: '',
    joinDate: '',
  })

  const [skinProfile, setSkinProfile] = useState({
    skinType: '',
    sensitivity: '',
    concerns: [],
    allergies: '',
    age: '',
    climate: '',
  })

  const [preferences, setPreferences] = useState({
    notifications: true,
    emailUpdates: false,
    language: 'english',
  })

  useEffect(() => {
    if (user) {
      setProfile({
        name: user.name || '',
        email: user.email || '',
        phone: user.phone || '',
        avatar: user.avatar || '',
        joinDate: new Date(user.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }),
      })
      
      setSkinProfile({
        skinType: user.skin_type || '',
        sensitivity: user.sensitivity || 'normal',
        concerns: user.concerns || [],
        allergies: user.allergies || '',
        age: user.age_group || '',
        climate: user.climate || '',
      })
      
      setPreferences({
        notifications: user.notifications_enabled !== undefined ? user.notifications_enabled : true,
        emailUpdates: user.email_updates !== undefined ? user.email_updates : false,
        language: 'english',
      })
    }
  }, [user])

  const skinTypeOptions = [
    { value: 'dry', label: 'Dry', icon: 'water_drop' },
    { value: 'oily', label: 'Oily', icon: 'opacity' },
    { value: 'combination', label: 'Combination', icon: 'contrast' },
    { value: 'normal', label: 'Normal', icon: 'balance' },
    { value: 'sensitive', label: 'Sensitive', icon: 'healing' },
  ]

  const sensitivityOptions = [
    { value: 'low', label: 'Low Sensitivity' },
    { value: 'normal', label: 'Normal' },
    { value: 'high', label: 'High Sensitivity' },
  ]

  const concernOptions = [
    { value: 'acne', label: 'Acne' },
    { value: 'dark-spots', label: 'Dark Spots' },
    { value: 'large-pores', label: 'Large Pores' },
    { value: 'wrinkles', label: 'Wrinkles' },
    { value: 'dark-circles', label: 'Dark Circles' },
    { value: 'dryness', label: 'Dryness' },
    { value: 'oiliness', label: 'Oiliness' },
    { value: 'redness', label: 'Redness' },
    { value: 'uneven-tone', label: 'Uneven Tone' },
  ]

  const handleConcernToggle = (value) => {
    setSkinProfile(prev => ({
      ...prev,
      concerns: prev.concerns.includes(value)
        ? prev.concerns.filter(c => c !== value)
        : [...prev.concerns, value]
    }))
  }

  const handleSaveProfile = async () => {
    setLoading(true)
    
    const updateData = {
      name: profile.name,
      phone: profile.phone,
      skin_type: skinProfile.skinType,
      sensitivity: skinProfile.sensitivity,
      concerns: skinProfile.concerns,
      allergies: skinProfile.allergies,
      age_group: skinProfile.age,
      climate: skinProfile.climate,
      notifications_enabled: preferences.notifications,
      email_updates: preferences.emailUpdates,
    }
    
    const result = await updateUser(updateData)
    
    if (result.success) {
      setIsEditing(false)
      // Show success message (you can add a toast notification here)
    } else {
      // Show error (you can add error handling here)
      console.error('Update failed:', result.error)
    }
    
    setLoading(false)
  }

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
            <span className="material-symbols-outlined">person</span>
            <h1>Profile & Settings</h1>
          </div>

          <div className="header-actions">
            {isEditing ? (
              <>
                <button className="btn btn-secondary" onClick={() => setIsEditing(false)}>
                  Cancel
                </button>
                <button className="btn btn-primary" onClick={handleSaveProfile}>
                  <span className="material-symbols-outlined">save</span>
                  Save
                </button>
              </>
            ) : (
              <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
                <span className="material-symbols-outlined">edit</span>
                Edit Profile
              </button>
            )}
          </div>
        </header>

        {/* Content */}
        <div className="profile-content">
          {/* Navigation */}
          <nav className="profile-nav">
            <button 
              className={`nav-item ${activeSection === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveSection('profile')}
            >
              <span className="material-symbols-outlined">account_circle</span>
              <span>Personal Info</span>
            </button>
            <button 
              className={`nav-item ${activeSection === 'skin' ? 'active' : ''}`}
              onClick={() => setActiveSection('skin')}
            >
              <span className="material-symbols-outlined">face</span>
              <span>Skin Profile</span>
            </button>
            <button 
              className={`nav-item ${activeSection === 'preferences' ? 'active' : ''}`}
              onClick={() => setActiveSection('preferences')}
            >
              <span className="material-symbols-outlined">settings</span>
              <span>Preferences</span>
            </button>
            <button 
              className={`nav-item ${activeSection === 'security' ? 'active' : ''}`}
              onClick={() => setActiveSection('security')}
            >
              <span className="material-symbols-outlined">security</span>
              <span>Security</span>
            </button>
          </nav>

          {/* Main Content Area */}
          <div className="profile-main">
            {/* Personal Info Section */}
            {activeSection === 'profile' && (
              <div className="section-content">
                <div className="profile-header-card">
                  <div className="avatar-section">
                    <div className="avatar-wrapper">
                      <img src={profile.avatar} alt={profile.name} />
                      {isEditing && (
                        <button className="avatar-edit-btn">
                          <span className="material-symbols-outlined">photo_camera</span>
                        </button>
                      )}
                    </div>
                    <div className="avatar-info">
                      <h2>{profile.name}</h2>
                      <p>Member since {profile.joinDate}</p>
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3 className="section-title">Personal Information</h3>
                  
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Full Name</label>
                      <input 
                        type="text"
                        value={profile.name}
                        onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                        disabled={!isEditing}
                      />
                    </div>
                    <div className="form-group">
                      <label>Email Address</label>
                      <input 
                        type="email"
                        value={profile.email}
                        onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                        disabled={!isEditing}
                      />
                    </div>
                    <div className="form-group">
                      <label>Phone Number</label>
                      <input 
                        type="tel"
                        value={profile.phone}
                        onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                        disabled={!isEditing}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Skin Profile Section */}
            {activeSection === 'skin' && (
              <div className="section-content">
                <div className="form-section">
                  <h3 className="section-title">Your Skin Type</h3>
                  <p className="section-description">Select the option that best describes your skin</p>
                  
                  <div className="skin-type-grid">
                    {skinTypeOptions.map((option) => (
                      <button 
                        key={option.value}
                        className={`skin-type-card ${skinProfile.skinType === option.value ? 'active' : ''}`}
                        onClick={() => isEditing && setSkinProfile({ ...skinProfile, skinType: option.value })}
                        disabled={!isEditing}
                      >
                        <span className="material-symbols-outlined">{option.icon}</span>
                        <span>{option.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="form-section">
                  <h3 className="section-title">Sensitivity Level</h3>
                  
                  <div className="sensitivity-options">
                    {sensitivityOptions.map((option) => (
                      <label key={option.value} className="radio-option">
                        <input 
                          type="radio"
                          name="sensitivity"
                          value={option.value}
                          checked={skinProfile.sensitivity === option.value}
                          onChange={(e) => setSkinProfile({ ...skinProfile, sensitivity: e.target.value })}
                          disabled={!isEditing}
                        />
                        <span className="radio-label">{option.label}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="form-section">
                  <h3 className="section-title">Skin Concerns</h3>
                  <p className="section-description">Select all that apply</p>
                  
                  <div className="concerns-grid">
                    {concernOptions.map((option) => (
                      <button 
                        key={option.value}
                        className={`concern-chip ${skinProfile.concerns.includes(option.value) ? 'active' : ''}`}
                        onClick={() => isEditing && handleConcernToggle(option.value)}
                        disabled={!isEditing}
                      >
                        {skinProfile.concerns.includes(option.value) && (
                          <span className="material-symbols-outlined">check</span>
                        )}
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="form-section">
                  <h3 className="section-title">Known Allergies</h3>
                  
                  <div className="form-group">
                    <textarea 
                      placeholder="Enter any known allergies or ingredients to avoid..."
                      value={skinProfile.allergies}
                      onChange={(e) => setSkinProfile({ ...skinProfile, allergies: e.target.value })}
                      disabled={!isEditing}
                      rows={3}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Preferences Section */}
            {activeSection === 'preferences' && (
              <div className="section-content">
                <div className="form-section">
                  <h3 className="section-title">Notifications</h3>
                  
                  <div className="toggle-list">
                    <div className="toggle-item">
                      <div className="toggle-info">
                        <span className="toggle-label">Push Notifications</span>
                        <span className="toggle-description">Receive reminders for your routine</span>
                      </div>
                      <label className="switch">
                        <input 
                          type="checkbox"
                          checked={preferences.notifications}
                          onChange={(e) => setPreferences({ ...preferences, notifications: e.target.checked })}
                        />
                        <span className="slider"></span>
                      </label>
                    </div>
                    <div className="toggle-item">
                      <div className="toggle-info">
                        <span className="toggle-label">Email Updates</span>
                        <span className="toggle-description">Weekly skin tips and product recommendations</span>
                      </div>
                      <label className="switch">
                        <input 
                          type="checkbox"
                          checked={preferences.emailUpdates}
                          onChange={(e) => setPreferences({ ...preferences, emailUpdates: e.target.checked })}
                        />
                        <span className="slider"></span>
                      </label>
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3 className="section-title">Appearance</h3>
                  
                  <div className="toggle-list">
                    <div className="toggle-item">
                      <div className="toggle-info">
                        <span className="toggle-label">Dark Mode</span>
                        <span className="toggle-description">Use dark theme throughout the app</span>
                      </div>
                      <label className="switch">
                        <input 
                          type="checkbox"
                          checked={preferences.darkMode}
                          onChange={(e) => setPreferences({ ...preferences, darkMode: e.target.checked })}
                        />
                        <span className="slider"></span>
                      </label>
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3 className="section-title">Language</h3>
                  
                  <div className="form-group">
                    <select 
                      value={preferences.language}
                      onChange={(e) => setPreferences({ ...preferences, language: e.target.value })}
                    >
                      <option value="english">English</option>
                      <option value="hindi">Hindi</option>
                      <option value="spanish">Spanish</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Security Section */}
            {activeSection === 'security' && (
              <div className="section-content">
                <div className="form-section">
                  <h3 className="section-title">Change Password</h3>
                  
                  <div className="form-stack">
                    <div className="form-group">
                      <label>Current Password</label>
                      <input type="password" placeholder="Enter current password" />
                    </div>
                    <div className="form-group">
                      <label>New Password</label>
                      <input type="password" placeholder="Enter new password" />
                    </div>
                    <div className="form-group">
                      <label>Confirm New Password</label>
                      <input type="password" placeholder="Confirm new password" />
                    </div>
                    <button className="btn btn-primary">Update Password</button>
                  </div>
                </div>

                <div className="form-section danger-zone">
                  <h3 className="section-title">Danger Zone</h3>
                  
                  <div className="danger-card">
                    <div className="danger-info">
                      <span className="material-symbols-outlined">warning</span>
                      <div>
                        <h4>Delete Account</h4>
                        <p>Once deleted, your account cannot be recovered. All your data will be permanently removed.</p>
                      </div>
                    </div>
                    <button 
                      className="btn btn-danger"
                      onClick={() => setShowDeleteModal(true)}
                    >
                      Delete Account
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-icon danger">
              <span className="material-symbols-outlined">warning</span>
            </div>
            <h3>Delete Account?</h3>
            <p>This action cannot be undone. All your data, scan history, and saved routines will be permanently deleted.</p>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowDeleteModal(false)}>
                Cancel
              </button>
              <button className="btn btn-danger">
                Yes, Delete My Account
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Profile
