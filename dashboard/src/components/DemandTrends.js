import React, { useState, useMemo } from 'react';
import { 
  ArrowTrendingUpIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon
} from '@heroicons/react/24/outline';
import { formatNumber, formatDateShort } from '../services/apiService';

const TrendIndicator = ({ change, size = 'small' }) => {
  if (!change || change === 0) {
    return (
      <div className={`flex items-center ${size === 'large' ? 'space-x-2' : 'space-x-1'}`}>
        <MinusIcon className={`${size === 'large' ? 'h-5 w-5' : 'h-4 w-4'} text-gray-400`} />
        {size === 'large' && <span className="text-gray-600">No change</span>}
      </div>
    );
  }

  const isPositive = change > 0;
  const absChange = Math.abs(change);
  const Icon = isPositive ? ArrowUpIcon : ArrowDownIcon;
  const colorClass = isPositive ? 'text-success-600' : 'text-danger-600';
  const bgClass = isPositive ? 'bg-success-50' : 'bg-danger-50';

  return (
    <div className={`flex items-center ${size === 'large' ? 'space-x-2' : 'space-x-1'}`}>
      <div className={`p-1 rounded-full ${bgClass}`}>
        <Icon className={`${size === 'large' ? 'h-4 w-4' : 'h-3 w-3'} ${colorClass}`} />
      </div>
      <span className={`${size === 'large' ? 'text-sm' : 'text-xs'} font-medium ${colorClass}`}>
        {absChange.toFixed(1)}%
      </span>
    </div>
  );
};

const TrendCard = ({ product, trend, detailed = false }) => {
  const latestTrend = trend[trend.length - 1] || {};
  const change = latestTrend.change_percentage || 0;
  const isSignificant = Math.abs(change) >= 15; // 15% threshold for significance

  return (
    <div className={`border rounded-lg p-4 transition-all duration-200 hover:shadow-sm ${
      isSignificant 
        ? change > 0 
          ? 'border-success-200 bg-success-50' 
          : 'border-danger-200 bg-danger-50'
        : 'border-gray-200 bg-white'
    }`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-gray-900 truncate">
            {product}
          </h4>
          <p className="text-xs text-gray-500 mt-1">
            7-day trend analysis
          </p>
        </div>
        <TrendIndicator change={change} size="large" />
      </div>

      {detailed && trend.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs text-gray-600">
            Recent demand pattern:
          </div>
          <div className="grid grid-cols-7 gap-1">
            {trend.slice(-7).map((item, index) => {
              const intensity = Math.min(Math.abs(item.change_percentage || 0) / 30, 1);
              const isPositive = (item.change_percentage || 0) > 0;
              return (
                <div
                  key={index}
                  className={`h-8 rounded text-xs flex items-center justify-center ${
                    isPositive
                      ? 'bg-success-100 text-success-800'
                      : intensity > 0.3
                      ? 'bg-danger-100 text-danger-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                  style={{
                    opacity: Math.max(0.3, intensity)
                  }}
                  title={`${formatDateShort(item.date)}: ${item.change_percentage?.toFixed(1) || 0}%`}
                >
                  {formatDateShort(item.date).slice(-2)}
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
        <div className="flex justify-between">
          <span>Current demand:</span>
          <span className="font-medium">
            {formatNumber(latestTrend.predicted_demand || 0)}
          </span>
        </div>
      </div>
    </div>
  );
};

const DemandTrends = ({ data = [], detailed = false }) => {
  const [sortBy, setSortBy] = useState('change');
  const [filterSignificant, setFilterSignificant] = useState(false);

  // Process trends data
  const trendsData = useMemo(() => {
    if (!data || data.length === 0) return [];

    // Group by product
    const productTrends = data.reduce((acc, item) => {
      if (!acc[item.product_name]) {
        acc[item.product_name] = [];
      }
      acc[item.product_name].push(item);
      return acc;
    }, {});

    // Calculate trend metrics for each product
    const trends = Object.entries(productTrends).map(([product, trends]) => {
      const sortedTrends = trends
        .filter(item => item.change_percentage !== null)
        .sort((a, b) => new Date(a.date) - new Date(b.date));

      if (sortedTrends.length === 0) {
        return { product, trend: [], latestChange: 0, avgChange: 0, volatility: 0 };
      }

      const latestChange = sortedTrends[sortedTrends.length - 1]?.change_percentage || 0;
      const changes = sortedTrends.map(item => item.change_percentage || 0);
      const avgChange = changes.reduce((sum, change) => sum + change, 0) / changes.length;
      const volatility = Math.sqrt(
        changes.reduce((sum, change) => sum + Math.pow(change - avgChange, 2), 0) / changes.length
      );

      return {
        product,
        trend: sortedTrends,
        latestChange,
        avgChange,
        volatility
      };
    });

    // Filter significant trends if requested
    const filteredTrends = filterSignificant 
      ? trends.filter(item => Math.abs(item.latestChange) >= 15)
      : trends;

    // Sort trends
    return filteredTrends.sort((a, b) => {
      switch (sortBy) {
        case 'change':
          return Math.abs(b.latestChange) - Math.abs(a.latestChange);
        case 'volatility':
          return b.volatility - a.volatility;
        case 'product':
          return a.product.localeCompare(b.product);
        default:
          return 0;
      }
    });
  }, [data, sortBy, filterSignificant]);

  const sortOptions = [
    { value: 'change', label: 'Trend Change' },
    { value: 'volatility', label: 'Volatility' },
    { value: 'product', label: 'Product Name' }
  ];

  // Calculate summary statistics
  const summary = useMemo(() => {
    if (trendsData.length === 0) return null;

    const totalTrends = trendsData.length;
    const increasingTrends = trendsData.filter(item => item.latestChange > 0).length;
    const decreasingTrends = trendsData.filter(item => item.latestChange < 0).length;
    const significantTrends = trendsData.filter(item => Math.abs(item.latestChange) >= 15).length;

    return {
      totalTrends,
      increasingTrends,
      decreasingTrends,
      significantTrends
    };
  }, [trendsData]);

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center space-x-2">
          <ArrowTrendingUpIcon className="h-5 w-5 text-primary-600" />
          <h3 className="card-title">
            {detailed ? 'Detailed Demand Trends' : 'Demand Trends'}
          </h3>
          {summary && (
            <span className="status-badge bg-gray-100 text-gray-800">
              {summary.totalTrends} products
            </span>
          )}
        </div>
      </div>

      {/* Summary Statistics */}
      {summary && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-lg font-semibold text-success-600">
                {summary.increasingTrends}
              </div>
              <div className="text-xs text-gray-500">Increasing</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-danger-600">
                {summary.decreasingTrends}
              </div>
              <div className="text-xs text-gray-500">Decreasing</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-warning-600">
                {summary.significantTrends}
              </div>
              <div className="text-xs text-gray-500">Significant</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-gray-600">
                {summary.totalTrends - summary.increasingTrends - summary.decreasingTrends}
              </div>
              <div className="text-xs text-gray-500">Stable</div>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="mb-6 flex flex-wrap items-center gap-4">
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Sort by:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-primary-500 focus:border-primary-500"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="significant-filter"
            checked={filterSignificant}
            onChange={(e) => setFilterSignificant(e.target.checked)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <label htmlFor="significant-filter" className="text-sm text-gray-700">
            Show only significant trends (≥15%)
          </label>
        </div>
      </div>

      {/* Trends Grid */}
      <div className="space-y-4">
        {trendsData.length === 0 ? (
          <div className="text-center py-12">
            <ArrowTrendingUpIcon className="mx-auto h-12 w-12 text-gray-300" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No trend data</h3>
            <p className="mt-1 text-sm text-gray-500">
              {filterSignificant 
                ? 'No significant trends found. Try removing the filter.'
                : 'No trend data available for analysis.'
              }
            </p>
          </div>
        ) : (
          <div className={`grid gap-4 ${
            detailed 
              ? 'grid-cols-1 md:grid-cols-2' 
              : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
          }`}>
            {trendsData.map((item, index) => (
              <TrendCard
                key={item.product}
                product={item.product}
                trend={item.trend}
                detailed={detailed}
              />
            ))}
          </div>
        )}
      </div>

      {/* Trend Insights */}
      {trendsData.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Trend Insights</h4>
          <div className="space-y-2 text-sm text-gray-600">
            {summary.significantTrends > 0 && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-warning-400 rounded-full"></div>
                <span>
                  {summary.significantTrends} product(s) showing significant demand changes
                </span>
              </div>
            )}
            {summary.increasingTrends > summary.decreasingTrends && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-success-400 rounded-full"></div>
                <span>
                  Overall demand trend is positive across {summary.increasingTrends} products
                </span>
              </div>
            )}
            {summary.decreasingTrends > summary.increasingTrends && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-danger-400 rounded-full"></div>
                <span>
                  Overall demand trend is declining across {summary.decreasingTrends} products
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DemandTrends; 