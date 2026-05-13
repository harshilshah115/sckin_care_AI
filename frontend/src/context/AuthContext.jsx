import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on mount
    const checkAuth = async () => {
      if (authAPI.isAuthenticated()) {
        try {
          const { ok, data } = await authAPI.getProfile()
          if (ok) {
            setUser(data)
          } else {
            // Token invalid, clear it
            authAPI.clearAuth()
          }
        } catch (error) {
          console.error('Auth check failed:', error)
          authAPI.clearAuth()
        }
      }
      setLoading(false)
    }
    
    checkAuth()
  }, [])

  const login = async (email, password) => {
    const { ok, data } = await authAPI.login(email, password)
    
    if (ok) {
      setUser(data.user)
      return { success: true, user: data.user }
    }
    
    return { success: false, error: data.detail || data.error || 'Login failed' }
  }

  const register = async (userData) => {
    const { ok, data } = await authAPI.register(userData)
    
    if (ok) {
      setUser(data.user)
      return { success: true, user: data.user }
    }
    
    // Extract error message from validation errors
    let errorMsg = 'Registration failed'
    
    if (data.password_confirm) {
      errorMsg = Array.isArray(data.password_confirm) ? data.password_confirm[0] : data.password_confirm
    } else if (data.password) {
      errorMsg = Array.isArray(data.password) ? data.password[0] : data.password
    } else if (data.email) {
      errorMsg = Array.isArray(data.email) ? data.email[0] : data.email
    } else if (data.detail) {
      errorMsg = data.detail
    } else if (data.error) {
      errorMsg = data.error
    } else if (typeof data === 'object') {
      // Get first error from any field
      const firstError = Object.values(data)[0]
      errorMsg = Array.isArray(firstError) ? firstError[0] : firstError
    }
    
    return { success: false, error: errorMsg }
  }

  const logout = async () => {
    await authAPI.logout()
    setUser(null)
  }

  const updateUser = async (profileData) => {
    const { ok, data } = await authAPI.updateProfile(profileData)
    
    if (ok) {
      setUser(data)
      return { success: true, user: data }
    }
    
    return { success: false, error: data.detail || 'Update failed' }
  }

  const isAuthenticated = !!user && authAPI.isAuthenticated()

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    updateUser,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
