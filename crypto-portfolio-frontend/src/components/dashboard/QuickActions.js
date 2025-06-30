import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const QuickActions = () => {
  const actions = [
    {
      title: 'Buy Crypto',
      description: 'Purchase cryptocurrencies',
      icon: '💰',
      link: '/trading',
      color: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
    },
    {
      title: 'Portfolio Analysis',
      description: 'View detailed analytics',
      icon: '📊',
      link: '/analytics',
      color: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
    },
    {
      title: 'Set Alerts',
      description: 'Price & news notifications',
      icon: '🔔',
      link: '/settings',
      color: 'bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800'
    },
    {
      title: 'Latest News',
      description: 'Market updates & insights',
      icon: '📰',
      link: '/news',
      color: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700"
    >
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Quick Actions
      </h2>

      <div className="space-y-3">
        {actions.map((action, index) => (
          <motion.div
            key={action.title}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 * index }}
          >
            <Link
              to={action.link}
              className={`block p-4 border rounded-lg hover:shadow-md transition-all duration-200 ${action.color}`}
            >
              <div className="flex items-center space-x-3">
                <div className="text-2xl">{action.icon}</div>
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {action.title}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {action.description}
                  </div>
                </div>
                <div className="ml-auto">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <button className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transform hover:scale-105 transition-all duration-200">
          🚀 Explore More Features
        </button>
      </div>
    </motion.div>
  );
};

export default QuickActions;