import React, { useState, useMemo } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  Area,
  AreaChart,
  BarChart,
  Bar
} from 'recharts';
import { ChartBarIcon, CalendarIcon } from '@heroicons/react/24/outline';
import { formatDateShort, formatNumber } from '../services/apiService';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-medium text-gray-900">{`Date: ${label}`}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }} className="text-sm">
            {`${entry.dataKey}: ${formatNumber(entry.value)}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const ForecastChart = ({ data = [], detailed = false }) => {
  const [selectedProduct, setSelectedProduct] = useState('all');
  const [chartType, setChartType] = useState('line');
  const [timeRange, setTimeRange] = useState(7);

  // Process and group data by date
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    // Filter by selected product
    const filteredData = selectedProduct === 'all' 
      ? data 
      : data.filter(item => item.product_name === selectedProduct);

    // Group by date and aggregate
    const groupedData = filteredData.reduce((acc, item) => {
      const date = formatDateShort(item.forecast_date);
      
      if (!acc[date]) {
        acc[date] = {
          date,
          predicted_demand: 0,
          confidence_lower: 0,
          confidence_upper: 0,
          count: 0
        };
      }
      
      acc[date].predicted_demand += parseFloat(item.predicted_demand || 0);
      acc[date].confidence_lower += parseFloat(item.confidence_interval_lower || 0);
      acc[date].confidence_upper += parseFloat(item.confidence_interval_upper || 0);
      acc[date].count += 1;
      
      return acc;
    }, {});

    // Convert to array and calculate averages
    const result = Object.values(groupedData)
      .map(item => ({
        date: item.date,
        predicted_demand: Math.round(item.predicted_demand),
        confidence_lower: Math.round(item.confidence_lower),
        confidence_upper: Math.round(item.confidence_upper),
        confidence_range: Math.round(item.confidence_upper - item.confidence_lower)
      }))
      .sort((a, b) => new Date(a.date) - new Date(b.date))
      .slice(0, timeRange);

    return result;
  }, [data, selectedProduct, timeRange]);

  // Get unique products for filter
  const products = useMemo(() => {
    const uniqueProducts = [...new Set(data.map(item => item.product_name))];
    return [
      { value: 'all', label: 'All Products' },
      ...uniqueProducts.map(product => ({ value: product, label: product }))
    ];
  }, [data]);

  const chartTypes = [
    { value: 'line', label: 'Line Chart' },
    { value: 'area', label: 'Area Chart' },
    { value: 'bar', label: 'Bar Chart' }
  ];

  const timeRanges = [
    { value: 7, label: '7 Days' },
    { value: 14, label: '14 Days' },
    { value: 30, label: '30 Days' }
  ];

  const renderChart = () => {
    const commonProps = {
      data: chartData,
      margin: { top: 20, right: 30, left: 20, bottom: 5 }
    };

    switch (chartType) {
      case 'area':
        return (
          <AreaChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="date" 
              stroke="#6b7280"
              tick={{ fontSize: 12 }}
            />
            <YAxis 
              stroke="#6b7280"
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area
              type="monotone"
              dataKey="confidence_upper"
              stackId="1"
              stroke="#e5e7eb"
              fill="#f3f4f6"
              fillOpacity={0.6}
              name="Confidence Upper"
            />
            <Area
              type="monotone"
              dataKey="predicted_demand"
              stackId="1"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.8}
              name="Predicted Demand"
            />
            <Area
              type="monotone"
              dataKey="confidence_lower"
              stackId="1"
              stroke="#e5e7eb"
              fill="#ffffff"
              fillOpacity={0.6}
              name="Confidence Lower"
            />
          </AreaChart>
        );
      
      case 'bar':
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="date" 
              stroke="#6b7280"
              tick={{ fontSize: 12 }}
            />
            <YAxis 
              stroke="#6b7280"
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar 
              dataKey="predicted_demand" 
              fill="#3b82f6" 
              name="Predicted Demand"
              radius={[2, 2, 0, 0]}
            />
            <Bar 
              dataKey="confidence_range" 
              fill="#e5e7eb" 
              name="Confidence Range"
              radius={[2, 2, 0, 0]}
            />
          </BarChart>
        );
      
      default: // line
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="date" 
              stroke="#6b7280"
              tick={{ fontSize: 12 }}
            />
            <YAxis 
              stroke="#6b7280"
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="predicted_demand"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
              name="Predicted Demand"
            />
            <Line
              type="monotone"
              dataKey="confidence_upper"
              stroke="#10b981"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="Upper Confidence"
            />
            <Line
              type="monotone"
              dataKey="confidence_lower"
              stroke="#f59e0b"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="Lower Confidence"
            />
          </LineChart>
        );
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center space-x-2">
          <ChartBarIcon className="h-5 w-5 text-primary-600" />
          <h3 className="card-title">
            {detailed ? 'Detailed Forecast Analysis' : 'Demand Forecast'}
          </h3>
        </div>
        <div className="flex items-center space-x-2">
          <CalendarIcon className="h-4 w-4 text-gray-400" />
          <span className="text-sm text-gray-500">
            Next {timeRange} days
          </span>
        </div>
      </div>

      {/* Controls */}
      <div className="mb-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Product Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Product
            </label>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500 text-sm"
            >
              {products.map((product) => (
                <option key={product.value} value={product.value}>
                  {product.label}
                </option>
              ))}
            </select>
          </div>

          {/* Chart Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Chart Type
            </label>
            <select
              value={chartType}
              onChange={(e) => setChartType(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500 text-sm"
            >
              {chartTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Time Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Time Range
            </label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500 text-sm"
            >
              {timeRanges.map((range) => (
                <option key={range.value} value={range.value}>
                  {range.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-80 w-full">
        {chartData.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <ChartBarIcon className="mx-auto h-12 w-12 text-gray-300" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No forecast data</h3>
              <p className="mt-1 text-sm text-gray-500">
                No forecast data available for the selected criteria.
              </p>
            </div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
          </ResponsiveContainer>
        )}
      </div>

      {/* Chart Statistics */}
      {chartData.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-sm">
            <div>
              <div className="font-semibold text-primary-600">
                {formatNumber(chartData.reduce((sum, item) => sum + item.predicted_demand, 0))}
              </div>
              <div className="text-gray-500">Total Demand</div>
            </div>
            <div>
              <div className="font-semibold text-primary-600">
                {formatNumber(Math.round(chartData.reduce((sum, item) => sum + item.predicted_demand, 0) / chartData.length))}
              </div>
              <div className="text-gray-500">Avg Daily</div>
            </div>
            <div>
              <div className="font-semibold text-primary-600">
                {formatNumber(Math.max(...chartData.map(item => item.predicted_demand)))}
              </div>
              <div className="text-gray-500">Peak Demand</div>
            </div>
            <div>
              <div className="font-semibold text-primary-600">
                {formatNumber(Math.min(...chartData.map(item => item.predicted_demand)))}
              </div>
              <div className="text-gray-500">Min Demand</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ForecastChart; 