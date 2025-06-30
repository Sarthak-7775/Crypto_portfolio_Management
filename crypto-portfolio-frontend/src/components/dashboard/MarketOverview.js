import React from 'react';
import { motion } from 'framer-motion';

const MarketOverview = () => {
  const marketData = [
    {
      name: 'Bitcoin',
      symbol: 'BTC',
      price: 42000,
      change: 2.5,
      marketCap: 825.6,
      volume: 28.4
    },
    {
      name: 'Ethereum',
      symbol: 'ETH',
      price: 2800,
      change: -1.2,
      marketCap: 336.5,
      volume: 15.2
    },
    {
      name: 'Cardano',
      symbol: 'ADA',
      price: 0.85,
      change: 5.8,
      marketCap: 28.4,
      volume: 2.1
    },
    {
      name: 'Solana',
      symbol: 'SOL',
      price: 98.45,
      change: 3.2,
      marketCap: 42.1,
      volume: 1.8
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Market Overview
        </h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">Live</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="text-left text-sm font-medium text-gray-600 dark:text-gray-400 pb-2">Asset</th>
              <th className="text-right text-sm font-medium text-gray-600 dark:text-gray-400 pb-2">Price</th>
              <th className="text-right text-sm font-medium text-gray-600 dark:text-gray-400 pb-2">24h %</th>
              <th className="text-right text-sm font-medium text-gray-600 dark:text-gray-400 pb-2">Market Cap</th>
            </tr>
          </thead>
          <tbody>
            {marketData.map((asset, index) => (
              <motion.tr
                key={asset.symbol}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                className="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <td className="py-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-bold text-xs">{asset.symbol.charAt(0)}</span>
                    </div>
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">{asset.symbol}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">{asset.name}</div>
                    </div>
                  </div>
                </td>
                <td className="py-3 text-right">
                  <div className="font-semibold text-gray-900 dark:text-white">
                    ${asset.price.toLocaleString()}
                  </div>
                </td>
                <td className="py-3 text-right">
                  <div className={`font-semibold ${
                    asset.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {asset.change >= 0 ? '+' : ''}{asset.change}%
                  </div>
                </td>
                <td className="py-3 text-right">
                  <div className="text-gray-900 dark:text-white">
                    ${asset.marketCap}B
                  </div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-lg font-bold text-green-600">+2.4%</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Market</div>
          </div>
          <div>
            <div className="text-lg font-bold text-blue-600">$1.2T</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Market Cap</div>
          </div>
          <div>
            <div className="text-lg font-bold text-purple-600">$48B</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">24h Volume</div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default MarketOverview;