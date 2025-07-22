import React from 'react';

const SentimentBadge = ({ sentiment, size = 'md', showIcon = true }) => {
  const getSentimentConfig = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
      case 'bullish':
        return {
          color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
          icon: '📈',
          label: 'Bullish'
        };
      case 'negative':
      case 'bearish':
        return {
          color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
          icon: '📉',
          label: 'Bearish'
        };
      case 'neutral':
        return {
          color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
          icon: '➡️',
          label: 'Neutral'
        };
      default:
        return {
          color: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
          icon: '📊',
          label: 'Unknown'
        };
    }
  };

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  };

  const config = getSentimentConfig(sentiment);

  return (
    <span className={`inline-flex items-center rounded-full font-medium ${config.color} ${sizeClasses[size]}`}>
      {showIcon && <span className="mr-1">{config.icon}</span>}
      {config.label}
    </span>
  );
};

export default SentimentBadge;