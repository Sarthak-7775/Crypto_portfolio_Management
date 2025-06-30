import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { usePortfolio } from '../contexts/PortfolioContext';
import { useWebSocket } from '../contexts/WebSocketContext';
import PortfolioSummary from '../components/dashboard/PortfolioSummary';
import AssetAllocation from '../components/dashboard/AssetAllocation';
import PriceChart from '../components/dashboard/PriceChart';
import RecentTransactions from '../components/dashboard/RecentTransactions';
import MarketOverview from '../components/dashboard/MarketOverview';
import QuickActions from '../components/dashboard/QuickActions';

const DashboardPage = () => {
  const { portfolio } = usePortfolio();
  const { priceData, isConnected } = useWebSocket();
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h');

  const timeframes = [
    { value: '1h', label: '1H' },
    { value: '24h', label: '24H' },
    { value: '7d', label: '7D' },
    { value: '30d', label: '30D' }
  ];

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Dashboard Overview
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Track your portfolio performance and market trends
          </p>
        </div>

        {/* Timeframe selector */}
        <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
          {timeframes.map((timeframe) => (
            <button
              key={timeframe.value}
              onClick={() => setSelectedTimeframe(timeframe.value)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                selectedTimeframe === timeframe.value
                  ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              {timeframe.label}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <PortfolioSummary />
        <div className="lg:col-span-2">
          <PriceChart timeframe={selectedTimeframe} />
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          <MarketOverview />
          <RecentTransactions />
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <AssetAllocation />
          <QuickActions />
        </div>
      </div>

      {/* Connection Status Alert */}
      {!isConnected && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed bottom-4 right-4 bg-red-600 text-white px-4 py-2 rounded-lg shadow-lg"
        >
          ⚠️ Connection lost - Reconnecting...
        </motion.div>
      )}
    </div>
  );
};

export default DashboardPage;