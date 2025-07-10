import React from 'react';
import { 
  CubeIcon, 
  ExclamationTriangleIcon, 
  ChartBarIcon, 
  CurrencyDollarIcon,
  ArrowTrendingUpIcon 
} from '@heroicons/react/24/outline';
import { formatCurrency, formatNumber } from '../services/apiService';

const StatCard = ({ title, value, icon: Icon, color, subtitle, trend }) => {
  return (
    <div className="card">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <div className={`flex items-center justify-center w-12 h-12 rounded-lg ${color}`}>
            <Icon className="h-6 w-6 text-white" />
          </div>
        </div>
        <div className="ml-4 flex-1">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">{title}</p>
              <p className="text-2xl font-semibold text-gray-900">{value}</p>
              {subtitle && (
                <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
              )}
            </div>
            {trend && (
              <div className={`flex items-center ${trend.positive ? 'text-success-600' : 'text-danger-600'}`}>
                <ArrowTrendingUpIcon className={`h-4 w-4 ${trend.positive ? '' : 'transform rotate-180'}`} />
                <span className="text-sm font-medium ml-1">{trend.value}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const StatsOverview = ({ data }) => {
  if (!data) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="card animate-pulse">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
              <div className="ml-4 flex-1">
                <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
                <div className="h-6 bg-gray-200 rounded w-16"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  const stats = [
    {
      title: 'Total Products',
      value: formatNumber(data.total_products || 0),
      icon: CubeIcon,
      color: 'bg-primary-600',
      subtitle: 'SKUs in inventory'
    },
    {
      title: 'Low Stock Alerts',
      value: formatNumber(data.low_stock_products || 0),
      icon: ExclamationTriangleIcon,
      color: data.low_stock_products > 0 ? 'bg-warning-600' : 'bg-success-600',
      subtitle: 'Need reordering'
    },
    {
      title: 'Critical Alerts',
      value: formatNumber(data.critical_alerts || 0),
      icon: ExclamationTriangleIcon,
      color: data.critical_alerts > 0 ? 'bg-danger-600' : 'bg-success-600',
      subtitle: 'Require attention'
    },
    {
      title: 'Inventory Value',
      value: formatCurrency(data.total_inventory_value || 0),
      icon: CurrencyDollarIcon,
      color: 'bg-success-600',
      subtitle: 'Total value'
    },
    {
      title: 'Forecast Records',
      value: formatNumber(data.forecast_records || 0),
      icon: ChartBarIcon,
      color: 'bg-purple-600',
      subtitle: 'Future predictions'
    }
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Dashboard Overview</h2>
        <div className="text-sm text-gray-500">
          Real-time metrics
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        {stats.map((stat, index) => (
          <StatCard
            key={index}
            title={stat.title}
            value={stat.value}
            icon={stat.icon}
            color={stat.color}
            subtitle={stat.subtitle}
            trend={stat.trend}
          />
        ))}
      </div>

      {/* Quick Status Indicators */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                data.critical_alerts === 0 ? 'bg-success-400' : 'bg-danger-400'
              }`}></div>
              <span className="text-gray-600">System Status</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                data.low_stock_products === 0 ? 'bg-success-400' : 'bg-warning-400'
              }`}></div>
              <span className="text-gray-600">Stock Health</span>
            </div>
          </div>
          <div className="text-gray-500">
            {data.critical_alerts === 0 && data.low_stock_products === 0 
              ? '✅ All systems operational'
              : '⚠️ Attention required'
            }
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsOverview; 