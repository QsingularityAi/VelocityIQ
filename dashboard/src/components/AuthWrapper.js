import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import Login from './Login'
import Register from './Register'
import LoadingSpinner from './LoadingSpinner'
import LandingPage from './LandingPage'

const AuthWrapper = ({ children }) => {
  const [authMode, setAuthMode] = useState('landing') // 'landing', 'login', 'register', 'forgot-password'
  const { user, loading, isAuthenticated, enterDemoMode } = useAuth()

  // Demo mode bypass - if no proper Supabase setup, show demo user
  const isDemoMode = process.env.REACT_APP_SUPABASE_URL === undefined || 
                     process.env.REACT_APP_SUPABASE_URL === 'https://demo.supabase.co'

  const handleSwitchToRegister = () => {
    setAuthMode('register')
  }

  const handleSwitchToLogin = () => {
    setAuthMode('login')
  }

  const handleForgotPassword = () => {
    setAuthMode('forgot-password')
  }

  const handleEnterDashboard = () => {
    // If demo mode, create demo user and go to dashboard
    if (isDemoMode) {
      enterDemoMode()
      setAuthMode('dashboard')
    } else {
      // Otherwise, require authentication
      setAuthMode('login')
    }
  }

  const handleBackToLanding = () => {
    setAuthMode('landing')
  }

  const handleLogin = () => {
    setAuthMode('login')
  }

  // Show loading spinner while checking authentication
  if (loading && !isDemoMode) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner />
          <p className="mt-4 text-sm text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // Demo mode or authenticated user - show the main app
  if ((isDemoMode && authMode === 'dashboard') || (isAuthenticated && user)) {
    return children
  }

  // Show landing page first
  if (authMode === 'landing') {
    return (
      <LandingPage 
        onEnterDashboard={handleEnterDashboard}
        onLogin={handleLogin}
        isDemoMode={isDemoMode}
      />
    )
  }

  // Show authentication screens
  if (authMode === 'register') {
    return (
      <Register 
        onSwitchToLogin={handleSwitchToLogin}
        onBackToLanding={handleBackToLanding}
      />
    )
  }

  if (authMode === 'forgot-password') {
    return (
      <ForgotPassword 
        onSwitchToLogin={handleSwitchToLogin}
        onBackToLanding={handleBackToLanding}
      />
    )
  }

  // Show login
  return (
    <Login 
      onSwitchToRegister={handleSwitchToRegister}
      onForgotPassword={handleForgotPassword}
      onBackToLanding={handleBackToLanding}
    />
  )
}

// Forgot Password Component (existing code)
const ForgotPassword = ({ onSwitchToLogin, onBackToLanding }) => {
  const [email, setEmail] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const { resetPassword } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsSubmitting(true)

    if (!email) {
      setError('Please enter your email address')
      setIsSubmitting(false)
      return
    }

    if (!email.includes('@')) {
      setError('Please enter a valid email address')
      setIsSubmitting(false)
      return
    }

    try {
      const result = await resetPassword(email)
      
      if (!result.success) {
        setError(result.error || 'Failed to send reset email')
      } else {
        setSuccess('Password reset email sent! Please check your inbox and follow the instructions.')
        setEmail('')
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100">
            <svg
              className="h-8 w-8 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
              />
            </svg>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Reset your password
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Enter your email address and we'll send you a link to reset your password
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-red-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    {error}
                  </h3>
                </div>
              </div>
            </div>
          )}

          {success && (
            <div className="rounded-md bg-green-50 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-green-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-800">
                    {success}
                  </h3>
                </div>
              </div>
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
              placeholder="Enter your email address"
              disabled={isSubmitting}
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <div className="flex items-center">
                  <LoadingSpinner size="sm" />
                  <span className="ml-2">Sending...</span>
                </div>
              ) : (
                'Send Reset Link'
              )}
            </button>
          </div>

          <div className="flex items-center justify-between text-sm">
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="font-medium text-primary-600 hover:text-primary-500"
              disabled={isSubmitting}
            >
              ← Back to Sign in
            </button>
            <button
              type="button"
              onClick={onBackToLanding}
              className="font-medium text-gray-600 hover:text-gray-500"
              disabled={isSubmitting}
            >
              Back to Home
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AuthWrapper 