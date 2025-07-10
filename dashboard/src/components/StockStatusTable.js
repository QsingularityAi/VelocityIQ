import React, { useState, useMemo } from 'react';
import { 
  CubeIcon, 
  MagnifyingGlassIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { formatNumber, formatCurrency, getStockStatusColor } from '../services/apiService';

const StockStatusBadge = ({ status }) => {
  const colorClasses = getStockStatusColor(status);
  const displayText = status.replace('_', ' ');
  
  const getIcon = () => {
    switch (status) {
      case 'REORDER_NOW':
        return <ExclamationTriangleIcon className="h-3 w-3" />;
      case 'LOW_STOCK':
        return <ExclamationTriangleIcon className="h-3 w-3" />;
      case 'OK':
        return <CheckCircleIcon className="h-3 w-3" />;
      default:
        return null;
    }
  };

  return (
    <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${colorClasses}`}>
      {getIcon()}
      <span>{displayText}</span>
    </span>
  );
};

const SortButton = ({ field, currentSort, onSort, children }) => {
  const isActive = currentSort.field === field;
  const isAsc = isActive && currentSort.direction === 'asc';
  
  return (
    <button
      onClick={() => onSort(field)}
      className="flex items-center space-x-1 text-left font-medium text-gray-900 hover:text-primary-600 transition-colors duration-200"
    >
      <span>{children}</span>
      {isActive && (
        isAsc ? (
          <ArrowUpIcon className="h-4 w-4" />
        ) : (
          <ArrowDownIcon className="h-4 w-4" />
        )
      )}
    </button>
  );
};

const StockStatusTable = ({ data = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortConfig, setSortConfig] = useState({ field: 'product_name', direction: 'asc' });

  // Filter and search data
  const filteredData = useMemo(() => {
    return data.filter(product => {
      const matchesSearch = 
        product.product_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.sku?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.category?.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesStatus = statusFilter === 'all' || product.stock_status === statusFilter;
      
      return matchesSearch && matchesStatus;
    });
  }, [data, searchTerm, statusFilter]);

  // Sort data
  const sortedData = useMemo(() => {
    return [...filteredData].sort((a, b) => {
      const aVal = a[sortConfig.field];
      const bVal = b[sortConfig.field];
      
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;
      
      if (typeof aVal === 'string') {
        const result = aVal.localeCompare(bVal);
        return sortConfig.direction === 'asc' ? result : -result;
      }
      
      const result = aVal - bVal;
      return sortConfig.direction === 'asc' ? result : -result;
    });
  }, [filteredData, sortConfig]);

  const handleSort = (field) => {
    setSortConfig(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  // Get unique statuses for filter
  const statusOptions = useMemo(() => {
    const statuses = [...new Set(data.map(product => product.stock_status))];
    return [
      { value: 'all', label: 'All Status', count: data.length },
      ...statuses.map(status => ({
        value: status,
        label: status.replace('_', ' '),
        count: data.filter(p => p.stock_status === status).length
      }))
    ];
  }, [data]);

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center space-x-2">
          <CubeIcon className="h-5 w-5 text-primary-600" />
          <h3 className="card-title">Inventory Status</h3>
          <span className="status-badge bg-gray-100 text-gray-800">
            {sortedData.length} products
          </span>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="mb-6 space-y-4">
        {/* Search */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search products, SKUs, or categories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        {/* Status Filter */}
        <div className="flex flex-wrap gap-2">
          {statusOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setStatusFilter(option.value)}
              className={`px-3 py-1 text-sm rounded-full transition-colors duration-200 ${
                statusFilter === option.value
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {option.label} ({option.count})
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortButton field="product_name" currentSort={sortConfig} onSort={handleSort}>
                  Product
                </SortButton>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortButton field="current_stock" currentSort={sortConfig} onSort={handleSort}>
                  Current Stock
                </SortButton>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortButton field="reorder_point" currentSort={sortConfig} onSort={handleSort}>
                  Reorder Point
                </SortButton>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortButton field="days_until_stockout" currentSort={sortConfig} onSort={handleSort}>
                  Days Left
                </SortButton>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <SortButton field="avg_daily_demand" currentSort={sortConfig} onSort={handleSort}>
                  Daily Demand
                </SortButton>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Supplier
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedData.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-12 text-center">
                  <CubeIcon className="mx-auto h-12 w-12 text-gray-300" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No products found</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Try adjusting your search or filter criteria.
                  </p>
                </td>
              </tr>
            ) : (
              sortedData.map((product, index) => (
                <tr key={product.id || index} className="hover:bg-gray-50 transition-colors duration-150">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {product.product_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {product.sku} • {product.category}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {formatNumber(product.current_stock)}
                    </div>
                    {product.unit_cost && (
                      <div className="text-sm text-gray-500">
                        Value: {formatCurrency(product.current_stock * product.unit_cost)}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatNumber(product.reorder_point)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {product.days_until_stockout ? (
                      <div className={`text-sm font-medium ${
                        product.days_until_stockout <= 3 ? 'text-danger-600' :
                        product.days_until_stockout <= 7 ? 'text-warning-600' :
                        'text-gray-900'
                      }`}>
                        {product.days_until_stockout} days
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">—</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StockStatusBadge status={product.stock_status} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {product.avg_daily_demand ? 
                      `${formatNumber(product.avg_daily_demand)}/day` : 
                      '—'
                    }
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {product.supplier_name || 'N/A'}
                    </div>
                    {product.lead_time_days && (
                      <div className="text-sm text-gray-500">
                        Lead time: {product.lead_time_days} days
                      </div>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      {data.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-sm">
            <div>
              <div className="font-semibold text-danger-600">
                {data.filter(p => p.stock_status === 'REORDER_NOW').length}
              </div>
              <div className="text-gray-500">Reorder Now</div>
            </div>
            <div>
              <div className="font-semibold text-warning-600">
                {data.filter(p => p.stock_status === 'LOW_STOCK').length}
              </div>
              <div className="text-gray-500">Low Stock</div>
            </div>
            <div>
              <div className="font-semibold text-warning-500">
                {data.filter(p => p.stock_status === 'MONITOR').length}
              </div>
              <div className="text-gray-500">Monitor</div>
            </div>
            <div>
              <div className="font-semibold text-success-600">
                {data.filter(p => p.stock_status === 'OK').length}
              </div>
              <div className="text-gray-500">Healthy</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockStatusTable; 