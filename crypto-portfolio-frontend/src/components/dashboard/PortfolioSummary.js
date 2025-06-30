import React from 'react';
import { motion } from 'framer-motion';
import { usePortfolio } from '../../contexts/PortfolioContext';

const PortfolioSummary = () => {
  const { portfolio } = usePortfolio();

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatPercentage = (percentage) => {
    return `${percentage >= 0 ? '+' : ''}${percentage.toFixed(2)}%`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700"
    >
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Portfolio Summary
      </h2>

      <div className="space-y-4">
        {/* Total Value */}
        <div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {formatCurrency(portfolio.totalValue)}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Total Portfolio Value
          </div>
        </div>

        {/* 24h Change */}
        <div className="flex items-center justify-between">
          <div>
            <div className={`text-lg font-semibold ${
              portfolio.totalChange >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {formatCurrency(Math.abs(portfolio.totalChange))}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              24h Change
            </div>
          </div>
          <div className={`px-2 py-1 rounded-lg text-sm font-medium ${
            portfolio.totalChangePercent >= 0 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            {formatPercentage(portfolio.totalChangePercent)}
          </div>
        </div>

        {/* Holdings Count */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            Holdings
          </div>
          <div className="font-semibold text-gray-900 dark:text-white">
            {portfolio.holdings.length} assets
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4 pt-2">
          <div className="text-center">
            <div className="text-lg font-semibold text-blue-600 dark:text-blue-400">
              🔥 3
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">
              Top Performers
            </div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-purple-600 dark:text-purple-400">
              📈 85%
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">
              Success Rate
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default PortfolioSummary;