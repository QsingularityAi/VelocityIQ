import React, { createContext, useContext, useEffect, useState } from 'react'
import { authService } from '../lib/supabase'

const AuthContext = createContext({})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Demo mode detection
  const isDemoMode = process.env.REACT_APP_SUPABASE_URL === undefined || 
                     process.env.REACT_APP_SUPABASE_URL === 'https://demo.supabase.co'

  useEffect(() => {
    // If in demo mode, just set loading to false, don't auto-login
    if (isDemoMode) {
      setLoading(false)
      return
    }

    // Get initial session
    const getInitialSession = async () => {
      try {
        const { data: { session }, error } = await authService.getCurrentSession()
        if (error) {
          console.error('Error getting initial session:', error)
          setError(error.message)
        } else {
          setSession(session)
          setUser(session?.user ?? null)
        }
      } catch (err) {
        console.error('Error in getInitialSession:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    getInitialSession()

    // Listen for auth changes
    const { data: { subscription } } = authService.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email)
        setSession(session)
        setUser(session?.user ?? null)
        setLoading(false)
        setError(null)
      }
    )

    return () => {
      subscription?.unsubscribe()
    }
  }, [isDemoMode])

  // Sign up function
  const signUp = async (email, password, metadata = {}) => {
    if (isDemoMode) {
      // Demo signup - simulate successful registration
      setUser({
        id: 'demo-user-' + Date.now(),
        email: email,
        user_metadata: {
          full_name: metadata.full_name || `${metadata.first_name} ${metadata.last_name}`.trim() || 'Demo User',
          first_name: metadata.first_name || 'Demo',
          last_name: metadata.last_name || 'User',
          company: metadata.company || ''
        }
      })
      setSession({ access_token: 'demo-token-' + Date.now() })
      return { 
        success: true, 
        message: 'Demo account created successfully! In real mode, you would receive an email verification.',
        data: { user: { email } }
      }
    }

    setLoading(true)
    setError(null)
    
    try {
      const { data, error } = await authService.signUp(email, password, metadata)
      
      if (error) {
        setError(error.message)
        return { success: false, error: error.message }
      }
      
      return { success: true, data }
    } catch (err) {
      const errorMessage = err.message || 'An unexpected error occurred'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  // Sign in function
  const signIn = async (email, password) => {
    if (isDemoMode) {
      // Demo login - simulate successful authentication
      setUser({
        id: 'demo-user-' + Date.now(),
        email: email,
        user_metadata: {
          full_name: 'Demo User',
          first_name: 'Demo',
          last_name: 'User'
        }
      })
      setSession({ access_token: 'demo-token-' + Date.now() })
      return { 
        success: true,
        message: 'Demo login successful!',
        data: { user: { email } }
      }
    }

    setLoading(true)
    setError(null)
    
    try {
      const { data, error } = await authService.signIn(email, password)
      
      if (error) {
        setError(error.message)
        return { success: false, error: error.message }
      }
      
      return { success: true, data }
    } catch (err) {
      const errorMessage = err.message || 'An unexpected error occurred'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  // Sign out function
  const signOut = async () => {
    if (isDemoMode) {
      setUser(null)
      setSession(null)
      return { success: true }
    }

    setLoading(true)
    setError(null)
    
    try {
      const { error } = await authService.signOut()
      
      if (error) {
        setError(error.message)
        return { success: false, error: error.message }
      }
      
      return { success: true }
    } catch (err) {
      const errorMessage = err.message || 'An unexpected error occurred'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  // Reset password function
  const resetPassword = async (email) => {
    if (isDemoMode) {
      return { 
        success: true, 
        message: 'Demo mode: Password reset email would be sent to ' + email + ' in real authentication.' 
      }
    }

    setLoading(true)
    setError(null)
    
    try {
      const { data, error } = await authService.resetPassword(email)
      
      if (error) {
        setError(error.message)
        return { success: false, error: error.message }
      }
      
      return { success: true, data }
    } catch (err) {
      const errorMessage = err.message || 'An unexpected error occurred'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  // Update password function
  const updatePassword = async (password) => {
    if (isDemoMode) {
      return { success: false, error: 'Please configure Supabase for real authentication' }
    }

    setLoading(true)
    setError(null)
    
    try {
      const { data, error } = await authService.updatePassword(password)
      
      if (error) {
        setError(error.message)
        return { success: false, error: error.message }
      }
      
      return { success: true, data }
    } catch (err) {
      const errorMessage = err.message || 'An unexpected error occurred'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  // Enter demo mode function
  const enterDemoMode = () => {
    if (isDemoMode) {
      setUser({
        id: 'demo-user',
        email: 'demo@velocityiq.com',
        user_metadata: {
          full_name: 'Demo User',
          first_name: 'Demo',
          last_name: 'User'
        }
      })
      setSession({ access_token: 'demo-token' })
      return { success: true }
    }
    return { success: false, error: 'Not in demo mode' }
  }

  const value = {
    user,
    session,
    loading,
    error,
    signUp,
    signIn,
    signOut,
    resetPassword,
    updatePassword,
    enterDemoMode,
    isAuthenticated: !!user,
    isDemoMode
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthContext 