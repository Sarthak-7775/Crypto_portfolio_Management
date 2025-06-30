import React from 'react';
import { motion } from 'framer-motion';

const RecentTransactions = () => {
  const transactions = [
    {
      id: 1,
      type: 'buy',
      asset: 'BTC',
      amount: 0.25,
      price: 42000,
      total: 10500,
      time: '2 hours ago',
      status: 'completed'
    },
    {
      id: 2,
      type: 'sell',
      asset: 'ETH',
      amount: 2.5,
      price: 2800,
      total: 7000,
      time: '4 hours ago',
      status: 'completed'
    },
    {
      id: 3,
      type: 'buy',
      asset: 'ADA',
      amount: 500,
      price: 0.85,
      total: 425,
      time: '6 hours ago',
      status: 'pending'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Recent Transactions
        </h2>
        <button className="text-blue-600 dark:text-blue-400 hover:underline text-sm">
          View All
        </button>
      </div>

      <div className="space-y-3">
        {transactions.map((tx, index) => (
          <motion.div
            key={tx.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 * index }}
            className="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                tx.type === 'buy' ? 'bg-green-600' : 'bg-red-600'
              }`}>
                {tx.type === 'buy' ? '↗' : '↙'}
              </div>
              <div>
                <div className="font-medium text-gray-900 dark:text-white">
                  {tx.type === 'buy' ? 'Bought' : 'Sold'} {tx.amount} {tx.asset}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  ${tx.price.toLocaleString()} • {tx.time}
                </div>
              </div>
            </div>

            <div className="text-right">
              <div className={`font-semibold ${
                tx.type === 'buy' ? 'text-red-600' : 'text-green-600'
              }`}>
                {tx.type === 'buy' ? '-' : '+'}${tx.total.toLocaleString()}
              </div>
              <div className={`text-xs px-2 py-1 rounded-full ${
                tx.status === 'completed' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
              }`}>
                {tx.status}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <button className="w-full mt-4 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
        📊 View Transaction History
      </button>
    </motion.div>
  );
};

export default RecentTransactions;