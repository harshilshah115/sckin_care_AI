import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'
import { useAuth } from '../../context/AuthContext'
import Sidebar from '../../components/Sidebar/Sidebar'
import './Settings.css'

function Settings() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { theme, toggleTheme } = useTheme()
  const { user, logout, updateUser } = useAuth()
  const navigate = useNavigate()

  const [settings, setSettings] = useState({
    notifications: {
      routineReminders: true,
      scanReminders: true,
      productUpdates: false,
      weeklyReport: true,
    },
    privacy: {
      shareProgress: false,
      analyticsEnabled: true,
    },
    display: {
      compactMode: false,
      showTips: true,
    },
  })

  useEffect(() => {
    if (user) {
      setSettings({
        notifications: {
          routineReminders: user.notifications?.routine_reminders !== undefined ? user.notifications.routine_reminders : true,
          scanReminders: user.notifications?.scan_reminders !== undefined ? user.notifications.scan_reminders : true,
          productUpdates: user.notifications?.product_updates !== undefined ? user.notifications.product_updates : false,
          weeklyReport: user.notifications?.weekly_report !== undefined ? user.notifications.weekly_report : true,
        },
        privacy: {
          shareProgress: user.privacy?.share_progress !== undefined ? user.privacy.share_progress : false,
          analyticsEnabled: user.privacy?.analytics_enabled !== undefined ? user.privacy.analytics_enabled : true,
        },
        display: {
          compactMode: user.display?.compact_mode !== undefined ? user.display.compact_mode : false,
          showTips: user.display?.show_tips !== undefined ? user.display.show_tips : true,
        },
      })
    }
  }, [user])

  const handleToggle = async (category, setting) => {
    const newSettings = {
      ...settings,
      [category]: {
        ...settings[category],
        [setting]: !settings[category][setting]
      }
    }
    
    setSettings(newSettings)
    
    // Save to backend
    try {
      await updateUser({
        notifications: {
          routine_reminders: newSettings.notifications.routineReminders,
          scan_reminders: newSettings.notifications.scanReminders,
          product_updates: newSettings.notifications.productUpdates,
          weekly_report: newSettings.notifications.weeklyReport,
        },
        privacy: {
          share_progress: newSettings.privacy.shareProgress,
          analytics_enabled: newSettings.privacy.analyticsEnabled,
        },
        display: {
          compact_mode: newSettings.display.compactMode,
          show_tips: newSettings.display.showTips,
        },
      })
    } catch (error) {
      console.error('Error updating settings:', error)
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="dashboard-layout">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main className="dashboard-main">
        <header className="dashboard-header">
          <button className="mobile-menu-toggle" onClick={() => setSidebarOpen(true)}>
            <span className="material-symbols-outlined">menu</span>
          </button>

          <div className="page-title">
            <span className="material-symbols-outlined">settings</span>
            <h1>Settings</h1>
          </div>
        </header>

        <div className="settings-content">
          {/* Account Section */}
          <section className="settings-section">
            <h2 className="section-header">
              <span className="material-symbols-outlined">account_circle</span>
              Account
            </h2>
            
            <div className="settings-list">
              <Link to="/profile" className="settings-item link">
                <div className="item-info">
                  <span className="item-label">Profile Settings</span>
                  <span className="item-description">Manage your personal information</span>
                </div>
                <span className="material-symbols-outlined">chevron_right</span>
              </Link>
              
              <Link to="/profile?section=skin" className="settings-item link">
                <div className="item-info">
                  <span className="item-label">Skin Profile</span>
                  <span className="item-description">Update your skin type and concerns</span>
                </div>
                <span className="material-symbols-outlined">chevron_right</span>
              </Link>
              
              <Link to="/profile?section=security" className="settings-item link">
                <div className="item-info">
                  <span className="item-label">Security</span>
                  <span className="item-description">Password and account security</span>
                </div>
                <span className="material-symbols-outlined">chevron_right</span>
              </Link>
            </div>
          </section>

          {/* Appearance Section */}
          <section className="settings-section">
            <h2 className="section-header">
              <span className="material-symbols-outlined">palette</span>
              Appearance
            </h2>
            
            <div className="settings-list">
              <div className="settings-item">
                <div className="item-info">
                  <span className="item-label">Dark Mode</span>
                  <span className="item-description">Use dark theme throughout the app</span>
                </div>
                <label className="switch">
                  <input 
                    type="checkbox"
                    checked={theme === 'dark'}
                    onChange={toggleTheme}
                  />
                  <span className="slider"></span>
                </label>
              </div>
              
              <div className="settings-item">
                <div className="item-info">
                  <span className="item-label">Compact Mode</span>
                  <span className="item-description">Reduce spacing for more content</span>
                </div>
                <label className="switch">
                  <input 
                    type="checkbox"
                    checked={settings.display.compactMode}
                    onChange={() => handleToggle('display', 'compactMode')}
                  />
                  <span className="slider"></span>
                </label>
              </div>
              
              <div className="settings-item">
                <div className="item-info">
                  <span className="item-label">Show Tips</span>
                  <span className="item-description">Display helpful tips and suggestions</span>
                </div>
                <label className="switch">
                  <input 
                    type="checkbox"
                    checked={settings.display.showTips}
                    onChange={() => handleToggle('display', 'showTips')}
                  />
                  <span className="slider"></span>
                </label>
              </div>
            </div>
          </section>

          {/* Notifications Section */}
          <section className="settings-section">
            <h2 className="section-header">
              <span className="material-symbols-outlined">notifications</span>
              Notifications
            </h2>
            
            <div className="settings-list">
              <div className="settings-item">
                <div className="item-info">
                  <span className="item-label">Routine Reminders</span>
                  <span className="item-description">Get reminded about your skincare routine</span>
                </div>
                <label className="switch">
                  <input 
                    type="checkbox"
                    checked={settings.notifications.routineReminders}
                    onChange={() => handleToggle('notifications', 'routineReminders')}
                  />
                  <span className="slider"></span>
                </label>
              </div>
              
              <div className="settings-item">
                <div className="item-info">
                  <span className="item-label">Scan Reminders</span>
                  <span className="item-description">Reminders to track your skin progress</span>
                </div>
                <label className="switch">
                  <input 
                    type="checkbox"
                    checked={settings.notifications.scanReminders}
                    onChange={() => handleToggle('notifications', 'scanReminders')}
                  />
                  <span className="slider"></span>
                </label>
              </div>
              
              <div className="settings-item">
                <div className="item-info">
                  <span className="item-label">Product Updates</span>
                  <span className="item-description">Get notified about new product recommendations</span>
                </div>
                <label className="switch">
                  <input 
                    type="checkbox"
                    checked={settings.notifications.productUpdates}
                    onChange={() => handleToggle('notifications', 'productUpdates')}
                  />
                  <span className="slider"></span>
                </label>
              </div>
              
              <div className="settings-item">
                <div className="item-info">
                  <span className="item-label">Weekly Report</span>
                  <span className="item-description">Receive weekly skin health summary</span>
                </div>
                <label className="switch">
                  <input 
                    type="checkbox"
                    checked={settings.notifications.weeklyReport}
                    onChange={() => handleToggle('notifications', 'weeklyReport')}
                  />
                  <span className="slider"></span>
                </label>
              </div>
            </div>
          </section>

          {/* Privacy Section */}
          <section className="settings-section">
            <h2 className="section-header">
              <span className="material-symbols-outlined">lock</span>
              Privacy
            </h2>
            
            <div className="settings-list">
              <div className="settings-item">
                <div className="item-info">
                  <span className="item-label">Share Progress</span>
                  <span className="item-description">Allow anonymous data for research</span>
                </div>
                <label className="switch">
                  <input 
                    type="checkbox"
                    checked={settings.privacy.shareProgress}
                    onChange={() => handleToggle('privacy', 'shareProgress')}
                  />
                  <span className="slider"></span>
                </label>
              </div>
              
              <div className="settings-item">
                <div className="item-info">
                  <span className="item-label">Analytics</span>
                  <span className="item-description">Help improve the app with usage data</span>
                </div>
                <label className="switch">
                  <input 
                    type="checkbox"
                    checked={settings.privacy.analyticsEnabled}
                    onChange={() => handleToggle('privacy', 'analyticsEnabled')}
                  />
                  <span className="slider"></span>
                </label>
              </div>
            </div>
          </section>

          {/* Support Section */}
          <section className="settings-section">
            <h2 className="section-header">
              <span className="material-symbols-outlined">help</span>
              Support
            </h2>
            
            <div className="settings-list">
              <a href="#" className="settings-item link">
                <div className="item-info">
                  <span className="item-label">Help Center</span>
                  <span className="item-description">FAQs and support articles</span>
                </div>
                <span className="material-symbols-outlined">chevron_right</span>
              </a>
              
              <a href="#" className="settings-item link">
                <div className="item-info">
                  <span className="item-label">Contact Support</span>
                  <span className="item-description">Get help from our team</span>
                </div>
                <span className="material-symbols-outlined">chevron_right</span>
              </a>
              
              <a href="#" className="settings-item link">
                <div className="item-info">
                  <span className="item-label">Privacy Policy</span>
                  <span className="item-description">How we handle your data</span>
                </div>
                <span className="material-symbols-outlined">chevron_right</span>
              </a>
              
              <a href="#" className="settings-item link">
                <div className="item-info">
                  <span className="item-label">Terms of Service</span>
                  <span className="item-description">Our terms and conditions</span>
                </div>
                <span className="material-symbols-outlined">chevron_right</span>
              </a>
            </div>
          </section>

          {/* App Info */}
          <section className="settings-section">
            <h2 className="section-header">
              <span className="material-symbols-outlined">info</span>
              About
            </h2>
            
            <div className="app-info">
              <div className="app-logo">
                <span className="material-symbols-outlined">spa</span>
              </div>
              <h3>Lumière Clinical</h3>
              <p>AI-Powered Skincare Assistant</p>
              <span className="version">Version 1.0.0</span>
            </div>
          </section>

          {/* Logout */}
          <button className="logout-btn" onClick={handleLogout}>
            <span className="material-symbols-outlined">logout</span>
            Sign Out
          </button>
        </div>
      </main>
    </div>
  )
}

export default Settings
