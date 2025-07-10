import axios from 'axios';
import { supabase } from '../lib/supabase';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    
    // Add authentication token if available
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`;
      }
    } catch (error) {
      console.warn('Failed to get auth token:', error);
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  async (error) => {
    console.error(`API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
    
    // Handle 401 responses by signing out user
    if (error.response?.status === 401) {
      console.warn('Unauthorized request, signing out user');
      try {
        await supabase.auth.signOut();
      } catch (signOutError) {
        console.error('Error signing out:', signOutError);
      }
    }
    
    return Promise.reject(error);
  }
);

export const apiService = {
  // Get dashboard overview metrics
  async getOverview() {
    try {
      const response = await api.get('/api/dashboard/overview');
      return response.data;
    } catch (error) {
      console.error('Error fetching overview:', error);
      throw new Error('Failed to fetch dashboard overview');
    }
  },

  // Get current alerts
  async getAlerts() {
    try {
      const response = await api.get('/api/dashboard/alerts');
      return response.data.alerts || [];
    } catch (error) {
      console.error('Error fetching alerts:', error);
      throw new Error('Failed to fetch alerts');
    }
  },

  // Get stock status for all products
  async getStockStatus() {
    try {
      const response = await api.get('/api/dashboard/stock-status');
      return response.data.products || [];
    } catch (error) {
      console.error('Error fetching stock status:', error);
      throw new Error('Failed to fetch stock status');
    }
  },

  // Get forecast data
  async getForecasts(days = 14) {
    try {
      const response = await api.get(`/api/dashboard/forecasts?days=${days}`);
      return response.data.forecasts || [];
    } catch (error) {
      console.error('Error fetching forecasts:', error);
      throw new Error('Failed to fetch forecasts');
    }
  },

  // Get demand trends
  async getDemandTrends() {
    try {
      const response = await api.get('/api/dashboard/demand-trends');
      return response.data.trends || [];
    } catch (error) {
      console.error('Error fetching demand trends:', error);
      throw new Error('Failed to fetch demand trends');
    }
  },

  // Get detailed chart data for a specific product
  async getProductChartData(productSku) {
    try {
      const response = await api.get(`/api/dashboard/chart-data/${productSku}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching product chart data:', error);
      throw new Error('Failed to fetch product chart data');
    }
  },

  // Health check
  async healthCheck() {
    try {
      const response = await api.get('/');
      return response.data;
    } catch (error) {
      console.error('Error checking API health:', error);
      throw new Error('API health check failed');
    }
  }
};

// Utility functions
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatNumber = (number) => {
  return new Intl.NumberFormat('en-US').format(number);
};

export const formatDate = (dateString) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

export const formatDateShort = (dateString) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
  }).format(date);
};

export const getStockStatusColor = (status) => {
  switch (status) {
    case 'REORDER_NOW':
      return 'text-danger-600 bg-danger-50';
    case 'LOW_STOCK':
      return 'text-warning-600 bg-warning-50';
    case 'MONITOR':
      return 'text-warning-600 bg-warning-50';
    case 'OK':
      return 'text-success-600 bg-success-50';
    default:
      return 'text-gray-600 bg-gray-50';
  }
};

export const getAlertSeverityColor = (severity) => {
  switch (severity) {
    case 'critical':
      return 'text-danger-600 bg-danger-50 border-danger-200';
    case 'high':
      return 'text-warning-600 bg-warning-50 border-warning-200';
    case 'medium':
      return 'text-warning-600 bg-warning-50 border-warning-200';
    case 'low':
      return 'text-primary-600 bg-primary-50 border-primary-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

export default apiService; 