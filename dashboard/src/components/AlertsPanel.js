import React, { useState } from 'react';
import { 
  ExclamationTriangleIcon, 
  ExclamationCircleIcon,
  InformationCircleIcon,
  EyeIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { formatDate, getAlertSeverityColor } from '../services/apiService';

const getSeverityIcon = (severity) => {
  switch (severity) {
    case 'critical':
      return ExclamationCircleIcon;
    case 'high':
    case 'medium':
      return ExclamationTriangleIcon;
    default:
      return InformationCircleIcon;
  }
};

const AlertItem = ({ alert, compact = false }) => {
  const SeverityIcon = getSeverityIcon(alert.severity);
  const severityColors = getAlertSeverityColor(alert.severity);

  return (
    <div className={`border rounded-lg p-4 ${severityColors} transition-colors duration-200 hover:shadow-sm`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <SeverityIcon className="h-5 w-5 mt-0.5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium truncate">
              {alert.title}
            </h4>
            <span className="text-xs opacity-75">
              {alert.severity.toUpperCase()}
            </span>
          </div>
          <p className="text-sm opacity-75 mt-1">
            {alert.description}
          </p>
          {alert.product_name && (
            <div className="mt-2 flex items-center space-x-2 text-xs">
              <span className="opacity-75">Product:</span>
              <span className="font-medium">{alert.product_name}</span>
              {alert.sku && (
                <span className="opacity-50">({alert.sku})</span>
              )}
            </div>
          )}
          {!compact && (
            <div className="mt-2 flex items-center justify-between text-xs opacity-75">
              <span>Type: {alert.type}</span>
              <span>{formatDate(alert.created_at)}</span>
            </div>
          )}
        </div>
        {compact && (
          <ChevronRightIcon className="h-4 w-4 opacity-50" />
        )}
      </div>
    </div>
  );
};

const AlertsPanel = ({ alerts = [], showAll = false, onViewAll }) => {
  const [selectedSeverity, setSelectedSeverity] = useState('all');

  // Filter alerts by severity
  const filteredAlerts = selectedSeverity === 'all' 
    ? alerts 
    : alerts.filter(alert => alert.severity === selectedSeverity);

  // Limit alerts if not showing all
  const displayAlerts = showAll ? filteredAlerts : filteredAlerts.slice(0, 5);

  // Get severity counts
  const severityCounts = alerts.reduce((counts, alert) => {
    counts[alert.severity] = (counts[alert.severity] || 0) + 1;
    counts.total = (counts.total || 0) + 1;
    return counts;
  }, {});

  const severityOptions = [
    { value: 'all', label: 'All', count: severityCounts.total || 0 },
    { value: 'critical', label: 'Critical', count: severityCounts.critical || 0 },
    { value: 'high', label: 'High', count: severityCounts.high || 0 },
    { value: 'medium', label: 'Medium', count: severityCounts.medium || 0 },
    { value: 'low', label: 'Low', count: severityCounts.low || 0 }
  ].filter(option => option.count > 0 || option.value === 'all');

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center space-x-2">
          <ExclamationTriangleIcon className="h-5 w-5 text-warning-600" />
          <h3 className="card-title">
            {showAll ? 'All Alerts' : 'Recent Alerts'}
          </h3>
          {alerts.length > 0 && (
            <span className="status-badge bg-gray-100 text-gray-800">
              {alerts.length}
            </span>
          )}
        </div>
        {!showAll && onViewAll && alerts.length > 5 && (
          <button 
            onClick={onViewAll}
            className="flex items-center space-x-1 text-sm text-primary-600 hover:text-primary-700"
          >
            <span>View All</span>
            <EyeIcon className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Severity Filter */}
      {showAll && severityOptions.length > 1 && (
        <div className="mb-4">
          <div className="flex flex-wrap gap-2">
            {severityOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => setSelectedSeverity(option.value)}
                className={`px-3 py-1 text-sm rounded-full transition-colors duration-200 ${
                  selectedSeverity === option.value
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {option.label} ({option.count})
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Alerts List */}
      <div className="space-y-3">
        {displayAlerts.length === 0 ? (
          <div className="text-center py-8">
            <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-gray-300" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No alerts</h3>
            <p className="mt-1 text-sm text-gray-500">
              {selectedSeverity === 'all' 
                ? 'No active alerts to display.' 
                : `No ${selectedSeverity} severity alerts.`
              }
            </p>
          </div>
        ) : (
          displayAlerts.map((alert, index) => (
            <AlertItem 
              key={alert.id || index} 
              alert={alert} 
              compact={!showAll}
            />
          ))
        )}
      </div>

      {/* Show more indicator */}
      {!showAll && alerts.length > 5 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <button
            onClick={onViewAll}
            className="w-full text-center text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            View {alerts.length - 5} more alerts
          </button>
        </div>
      )}

      {/* Summary for full view */}
      {showAll && alerts.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-semibold text-danger-600">
                {severityCounts.critical || 0}
              </div>
              <div className="text-xs text-gray-500">Critical</div>
            </div>
            <div>
              <div className="text-2xl font-semibold text-warning-600">
                {severityCounts.high || 0}
              </div>
              <div className="text-xs text-gray-500">High</div>
            </div>
            <div>
              <div className="text-2xl font-semibold text-warning-500">
                {severityCounts.medium || 0}
              </div>
              <div className="text-xs text-gray-500">Medium</div>
            </div>
            <div>
              <div className="text-2xl font-semibold text-primary-600">
                {severityCounts.low || 0}
              </div>
              <div className="text-xs text-gray-500">Low</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertsPanel; 