import React from 'react';
import { 
  ChartBarIcon, 
  ExclamationTriangleIcon, 
  CubeIcon, 
  ArrowTrendingUpIcon,
  SparklesIcon,
  ClockIcon,
  ShieldCheckIcon,
  ArrowRightIcon,
  EyeIcon,
  BellIcon,
  UserIcon
} from '@heroicons/react/24/outline';

const LandingPage = ({ onEnterDashboard, onLogin, isDemoMode }) => {
  const features = [
    {
      icon: ChartBarIcon,
      title: 'Real-time Analytics',
      description: 'Monitor your inventory performance with live data updates and comprehensive analytics.',
      color: 'text-primary-600 bg-primary-50'
    },
    {
      icon: ExclamationTriangleIcon,
      title: 'Smart Alerts',
      description: 'Get notified instantly about stock shortages, demand spikes, and critical inventory events.',
      color: 'text-warning-600 bg-warning-50'
    },
    {
      icon: ArrowTrendingUpIcon,
      title: 'Demand Forecasting',
      description: 'Predict future demand with AI-powered forecasting models and stay ahead of market trends.',
      color: 'text-success-600 bg-success-50'
    },
    {
      icon: CubeIcon,
      title: 'Inventory Management',
      description: 'Track stock levels, manage product lifecycle, and optimize inventory across all locations.',
      color: 'text-purple-600 bg-purple-50'
    },
    {
      icon: ClockIcon,
      title: 'Automated Updates',
      description: 'Continuous data synchronization ensures you always have the most current information.',
      color: 'text-indigo-600 bg-indigo-50'
    },
    {
      icon: ShieldCheckIcon,
      title: 'Data Security',
      description: 'Enterprise-grade security and compliance to protect your sensitive business data.',
      color: 'text-gray-600 bg-gray-50'
    }
  ];

  const stats = [
    { label: 'Data Points Processed', value: '10M+', icon: SparklesIcon },
    { label: 'Average Response Time', value: '<100ms', icon: ClockIcon },
    { label: 'Uptime Guarantee', value: '99.9%', icon: ShieldCheckIcon },
    { label: 'Real-time Updates', value: '24/7', icon: EyeIcon }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      {/* Header */}
      <header className="relative bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <div className="h-10 w-10 bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg flex items-center justify-center">
                  <ChartBarIcon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-3">
                  <h1 className="text-2xl font-bold text-gray-900">VelocityIQ</h1>
                  <p className="text-sm text-gray-500">Inventory Intelligence Platform</p>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {isDemoMode && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                  Demo Mode
                </span>
              )}
              <div className="flex items-center gap-2">
                <button
                  onClick={onLogin}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200"
                >
                  Sign In
                </button>
                <button
                  onClick={onEnterDashboard}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 transition-colors duration-200"
                >
                  {isDemoMode ? 'Demo Dashboard' : 'Enter Dashboard'}
                  <ArrowRightIcon className="ml-2 h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-28">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center px-4 py-2 bg-primary-50 text-primary-700 rounded-full text-sm font-medium mb-8">
              <SparklesIcon className="h-4 w-4 mr-2" />
              Powered by Advanced AWS Chronos TimeLLM Language Model
            </div>
            <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6">
              Transform Your
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-purple-600">
                Inventory Intelligence
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
              VelocityIQ empowers businesses with real-time inventory insights, predictive analytics, 
              and intelligent forecasting to optimize operations and drive growth.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={onEnterDashboard}
                className="inline-flex items-center justify-center px-8 py-4 border border-transparent text-lg font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 transition-colors duration-200 shadow-lg hover:shadow-xl"
              >
                <EyeIcon className="mr-2 h-5 w-5" />
                {isDemoMode ? 'Try Demo Dashboard' : 'View Live Dashboard'}
              </button>
              <button 
                onClick={onLogin}
                className="inline-flex items-center justify-center px-8 py-4 border border-gray-300 text-lg font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200 shadow-lg hover:shadow-xl"
              >
                <UserIcon className="mr-2 h-5 w-5" />
                Sign In / Register
              </button>
            </div>
          </div>
        </div>

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 opacity-20">
          <div className="w-72 h-72 bg-gradient-to-r from-primary-400 to-purple-400 rounded-full blur-3xl"></div>
        </div>
        <div className="absolute bottom-20 right-10 opacity-20">
          <div className="w-96 h-96 bg-gradient-to-r from-success-400 to-primary-400 rounded-full blur-3xl"></div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div key={index} className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-50 rounded-lg mb-4">
                    <Icon className="h-8 w-8 text-primary-600" />
                  </div>
                  <div className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
                  <div className="text-sm text-gray-600">{stat.label}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Powerful Features for Modern Businesses
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to manage, analyze, and optimize your inventory operations in one intelligent platform.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div 
                  key={index} 
                  className="bg-white rounded-xl p-8 shadow-sm hover:shadow-lg transition-shadow duration-300"
                >
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg mb-4 ${feature.color}`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-primary-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">
            Ready to Transform Your Operations?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Join thousands of businesses already using VelocityIQ to optimize their inventory and drive growth.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={onEnterDashboard}
              className="inline-flex items-center justify-center px-8 py-4 border border-transparent text-lg font-medium rounded-lg text-primary-600 bg-white hover:bg-gray-50 transition-colors duration-200 shadow-lg hover:shadow-xl"
            >
              <BellIcon className="mr-2 h-5 w-5" />
              {isDemoMode ? 'Try Demo Dashboard' : 'Access Dashboard'}
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </button>
            <button
              onClick={onLogin}
              className="inline-flex items-center justify-center px-8 py-4 border border-white text-lg font-medium rounded-lg text-white bg-primary-500 hover:bg-primary-400 transition-colors duration-200 shadow-lg hover:shadow-xl"
            >
              <UserIcon className="mr-2 h-5 w-5" />
              Sign In to Your Account
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="h-8 w-8 bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg flex items-center justify-center">
                <ChartBarIcon className="h-5 w-5 text-white" />
              </div>
              <span className="ml-3 text-white font-semibold">VelocityIQ</span>
            </div>
            <div className="text-gray-400 text-sm">
              © 2025 VelocityIQ. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage; 