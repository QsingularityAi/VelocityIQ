import React from 'react';

const LoadingSpinner = ({ size = 'large', text = 'Loading dashboard...' }) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12'
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div className={`animate-spin rounded-full ${sizeClasses[size]} border-b-2 border-primary-600`}></div>
      {text && (
        <p className="mt-4 text-sm text-gray-500">{text}</p>
      )}
    </div>
  );
};

export default LoadingSpinner; 