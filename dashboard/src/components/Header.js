import React, { useState, useEffect, useRef } from 'react';
import { ArrowPathIcon, BoltIcon, UserCircleIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';
import { formatDate } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';

const Header = ({ onRefresh, loading, lastUpdated }) => {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const { user, signOut } = useAuth();
  const menuRef = useRef(null);

  // Demo mode detection
  const isDemoMode = process.env.REACT_APP_SUPABASE_URL === undefined || 
                     process.env.REACT_APP_SUPABASE_URL === 'https://demo.supabase.co'

  // Demo user data
  const demoUser = {
    email: 'demo@velocityiq.com',
    user_metadata: {
      full_name: 'Demo User',
      first_name: 'Demo',
      last_name: 'User'
    }
  }

  const currentUser = isDemoMode ? demoUser : user

  const handleSignOut = async () => {
    if (isDemoMode) {
      alert('This is demo mode. Please configure Supabase for real authentication.')
      return
    }
    await signOut();
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-primary-600 to-purple-600 rounded-lg">
              <BoltIcon className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">VelocityIQ</h1>
              <p className="text-sm text-gray-500">Supply Chain Forecasting Dashboard</p>
            </div>
          </div>

          {/* Status and Actions */}
          <div className="flex items-center space-x-4">
            {/* Demo Mode Badge */}
            {isDemoMode && (
              <div className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-md text-xs font-medium">
                Demo Mode
              </div>
            )}

            {/* Last Updated */}
            {lastUpdated && (
              <div className="text-sm text-gray-500">
                Last updated: {formatDate(lastUpdated)}
              </div>
            )}

            {/* Auto-refresh indicator */}
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-xs text-gray-500">Auto-refresh</span>
              </div>
            </div>

            {/* User Menu */}
            <div className="relative" ref={menuRef}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors duration-200"
              >
                <UserCircleIcon className="h-5 w-5" />
                <span className="hidden sm:block">
                  {currentUser?.user_metadata?.full_name || currentUser?.email || 'User'}
                </span>
              </button>

              {/* User Dropdown Menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                  <div className="px-4 py-2 text-sm text-gray-700 border-b border-gray-100">
                    <div className="font-medium">{currentUser?.user_metadata?.full_name || 'User'}</div>
                    <div className="text-gray-500">{currentUser?.email}</div>
                    {isDemoMode && (
                      <div className="text-xs text-yellow-600 mt-1">Demo Account</div>
                    )}
                  </div>
                  
                  <button
                    onClick={handleSignOut}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    <ArrowRightOnRectangleIcon className="h-4 w-4 mr-2" />
                    {isDemoMode ? 'Exit Demo' : 'Sign out'}
                  </button>
                </div>
              )}
            </div>

            {/* Refresh Button */}
            <button
              onClick={onRefresh}
              disabled={loading}
              className={`
                flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200
                ${loading 
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                  : 'bg-primary-600 text-white hover:bg-primary-700'
                }
              `}
            >
              <ArrowPathIcon 
                className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} 
              />
              <span>{loading ? 'Refreshing...' : 'Refresh'}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 