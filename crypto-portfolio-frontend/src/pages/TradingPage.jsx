import React, { useState } from 'react';
import { motion } from 'framer-motion';
import TradingInterface from '../components/trading/TradingInterface';
import OrderBook from '../components/trading/OrderBook';
import TradeHistory from '../components/trading/TradeHistory';
import QuickTrade from '../components/trading/QuickTrade';
import MarketDepth from '../components/trading/MarketDepth';
import TradingChart from '../components/trading/TradingChart';

const TradingPage = () => {
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [tradeType, setTradeType] = useState('buy');

  const tradingPairs = [
    'BTC/USDT',
    'ETH/USDT', 
    'ADA/USDT',
    'SOL/USDT',
    'DOT/USDT'
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
            Trading Terminal
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Professional trading interface with real-time data
          </p>
        </div>

        {/* Trading Pair Selector */}
        <div className="flex items-center space-x-4">
          <select
            value={selectedPair}
            onChange={(e) => setSelectedPair(e.target.value)}
            className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            {tradingPairs.map(pair => (
              <option key={pair} value={pair}>{pair}</option>
            ))}
          </select>

          <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setTradeType('buy')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                tradeType === 'buy'
                  ? 'bg-green-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              Buy
            </button>
            <button
              onClick={() => setTradeType('sell')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                tradeType === 'sell'
                  ? 'bg-red-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              Sell
            </button>
          </div>
        </div>
      </motion.div>

      {/* Main Trading Interface */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* Chart Section */}
        <div className="xl:col-span-3">
          <TradingChart pair={selectedPair} />
        </div>

        {/* Quick Trade Panel */}
        <div>
          <QuickTrade 
            pair={selectedPair}
            tradeType={tradeType}
          />
        </div>
      </div>

      {/* Lower Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Book */}
        <div>
          <OrderBook pair={selectedPair} />
        </div>

        {/* Market Depth */}
        <div>
          <MarketDepth pair={selectedPair} />
        </div>

        {/* Trade History */}
        <div>
          <TradeHistory pair={selectedPair} />
        </div>
      </div>

      {/* Advanced Trading Interface */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <TradingInterface 
          selectedPair={selectedPair}
          tradeType={tradeType}
        />
      </motion.div>

      {/* Keyboard Shortcuts Help */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4"
      >
        <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">
          ⌨️ Keyboard Shortcuts
        </h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-blue-800 dark:text-blue-400">
          <div><kbd className="bg-blue-100 dark:bg-blue-800 px-2 py-1 rounded">B</kbd> Buy</div>
          <div><kbd className="bg-blue-100 dark:bg-blue-800 px-2 py-1 rounded">S</kbd> Sell</div>
          <div><kbd className="bg-blue-100 dark:bg-blue-800 px-2 py-1 rounded">Esc</kbd> Cancel Orders</div>
          <div><kbd className="bg-blue-100 dark:bg-blue-800 px-2 py-1 rounded">Tab</kbd> Switch Pairs</div>
        </div>
      </motion.div>
    </div>
  );
};

export default TradingPage;