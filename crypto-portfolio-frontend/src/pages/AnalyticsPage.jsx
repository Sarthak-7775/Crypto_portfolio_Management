import React, { useState } from 'react';
import { motion } from 'framer-motion';
import AdvancedCharts from '../components/analytics/AdvancedCharts';
import TechnicalIndicators from '../components/analytics/TechnicalIndicators';
import MarketOverview from '../components/analytics/MarketOverview';
import PerformanceAnalysis from '../components/analytics/PerformanceAnalysis';
import RiskMetrics from '../components/analytics/RiskMetrics';
import BacktestingTool from '../components/analytics/BacktestingTool';

const AnalyticsPage = () => {
  const [selectedAsset, setSelectedAsset] = useState('BTC');
  const [analysisType, setAnalysisType] = useState('technical');
  const [timeRange, setTimeRange] = useState('30d');

  const assets = ['BTC', 'ETH', 'ADA', 'SOL', 'DOT', 'MATIC'];
  const analysisTypes = [
    { value: 'technical', label: 'Technical Analysis' },
    { value: 'fundamental', label: 'Fundamental Analysis' },
    { value: 'sentiment', label: 'Sentiment Analysis' },
    { value: 'risk', label: 'Risk Analysis' }
  ];

  const timeRanges = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' }
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
            Advanced Analytics
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Deep insights and technical analysis for informed trading decisions
          </p>
        </div>

        {/* Controls */}
        <div className="flex flex-col sm:flex-row gap-3">
          <select
            value={selectedAsset}
            onChange={(e) => setSelectedAsset(e.target.value)}
            className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            {assets.map(asset => (
              <option key={asset} value={asset}>{asset}</option>
            ))}
          </select>

          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            {timeRanges.map(range => (
              <option key={range.value} value={range.value}>{range.label}</option>
            ))}
          </select>

          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            📊 Export Analysis
          </button>
        </div>
      </motion.div>

      {/* Analysis Type Selector */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700"
      >
        <div className="flex flex-wrap gap-2">
          {analysisTypes.map(type => (
            <button
              key={type.value}
              onClick={() => setAnalysisType(type.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                analysisType === type.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {type.label}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2">
          <AdvancedCharts 
            asset={selectedAsset}
            timeRange={timeRange}
            analysisType={analysisType}
          />
        </div>
        <div>
          <TechnicalIndicators 
            asset={selectedAsset}
            timeRange={timeRange}
          />
        </div>
      </div>

      {/* Analysis Content based on type */}
      {analysisType === 'technical' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <MarketOverview asset={selectedAsset} />
          <PerformanceAnalysis asset={selectedAsset} timeRange={timeRange} />
        </div>
      )}

      {analysisType === 'risk' && (
        <RiskMetrics asset={selectedAsset} timeRange={timeRange} />
      )}

      {analysisType === 'fundamental' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Fundamental Analysis - {selectedAsset}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">8.5/10</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Technology Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">7.8/10</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Adoption Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">6.9/10</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Community Score</div>
            </div>
          </div>
        </motion.div>
      )}

      {analysisType === 'sentiment' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Market Sentiment - {selectedAsset}
          </h3>
          <div className="flex items-center justify-center space-x-8">
            <div className="text-center">
              <div className="text-4xl mb-2">😊</div>
              <div className="text-lg font-semibold text-green-600">Bullish</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">72% Positive</div>
            </div>
            <div className="w-32 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
              <div className="w-3/4 h-2 bg-green-600 rounded-full"></div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Backtesting Tool */}
      <BacktestingTool 
        asset={selectedAsset}
        timeRange={timeRange}
      />
    </div>
  );
};

export default AnalyticsPage;