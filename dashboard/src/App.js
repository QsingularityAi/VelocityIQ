import React, { useState, useEffect } from 'react';
import { ChartBarIcon, ExclamationTriangleIcon, CubeIcon, ArrowTrendingUpIcon } from '@heroicons/react/24/outline';
import './index.css';

// Import components
import Header from './components/Header';
import StatsOverview from './components/StatsOverview';
import AlertsPanel from './components/AlertsPanel';
import StockStatusTable from './components/StockStatusTable';
import ForecastChart from './components/ForecastChart';
import DemandTrends from './components/DemandTrends';
import LoadingSpinner from './components/LoadingSpinner';
import AuthWrapper from './components/AuthWrapper';

// Import API service
import { apiService } from './services/apiService';

// Import Auth Provider
import { AuthProvider } from './contexts/AuthContext';

// Dashboard component (main app content)
const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    overview: null,
    alerts: [],
    stockStatus: [],
    forecasts: [],
    trends: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [overview, alerts, stockStatus, forecasts, trends] = await Promise.all([
        apiService.getOverview(),
        apiService.getAlerts(),
        apiService.getStockStatus(),
        apiService.getForecasts(),
        apiService.getDemandTrends()
      ]);

      setDashboardData({
        overview,
        alerts,
        stockStatus,
        forecasts,
        trends
      });
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data. Please check your API connection.');
    } finally {
      setLoading(false);
    }
  };

  // Initial data load
  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Auto-refresh setup
  useEffect(() => {
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 30000); // Refresh every 30 seconds

    return () => {
      clearInterval(interval);
    };
  }, []);

  // Manual refresh
  const handleRefresh = () => {
    fetchDashboardData();
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'alerts', name: 'Alerts', icon: ExclamationTriangleIcon },
    { id: 'inventory', name: 'Inventory', icon: CubeIcon },
    { id: 'forecasts', name: 'Forecasts', icon: ArrowTrendingUpIcon }
  ];

  if (loading && !dashboardData.overview) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-danger-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading dashboard</h3>
          <p className="mt-1 text-sm text-gray-500">{error}</p>
          <div className="mt-6">
            <button
              onClick={handleRefresh}
              className="btn-primary"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        onRefresh={handleRefresh} 
        loading={loading}
        lastUpdated={dashboardData.overview?.last_updated}
      />

      {/* Navigation Tabs */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto">
          <nav className="-mb-px flex space-x-8 px-4 sm:px-6 lg:px-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors duration-200`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6 animate-fade-in">
            <StatsOverview data={dashboardData.overview} />
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <ForecastChart data={dashboardData.forecasts} />
              </div>
              <div>
                <AlertsPanel 
                  alerts={dashboardData.alerts} 
                  showAll={false}
                  onViewAll={() => setActiveTab('alerts')}
                />
              </div>
            </div>

            <DemandTrends data={dashboardData.trends} />
          </div>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <div className="animate-fade-in">
            <AlertsPanel 
              alerts={dashboardData.alerts} 
              showAll={true}
            />
          </div>
        )}

        {/* Inventory Tab */}
        {activeTab === 'inventory' && (
          <div className="animate-fade-in">
            <StockStatusTable data={dashboardData.stockStatus} />
          </div>
        )}

        {/* Forecasts Tab */}
        {activeTab === 'forecasts' && (
          <div className="space-y-6 animate-fade-in">
            <ForecastChart data={dashboardData.forecasts} detailed={true} />
            <DemandTrends data={dashboardData.trends} detailed={true} />
          </div>
        )}
      </main>

      {/* Loading overlay */}
      {loading && dashboardData.overview && (
        <div className="fixed top-0 right-0 m-4 z-50">
          <div className="bg-white rounded-lg shadow-lg p-3 flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
            <span className="text-sm text-gray-600">Updating...</span>
          </div>
        </div>
      )}
    </div>
  );
};

// Main App component with authentication
function App() {
  return (
    <AuthProvider>
      <AuthWrapper>
        <Dashboard />
      </AuthWrapper>
    </AuthProvider>
  );
}

export default App; 