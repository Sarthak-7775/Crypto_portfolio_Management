import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const PriceChart = ({ timeframe = '24h' }) => {
  const [chartData, setChartData] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState('BTC');

  const assets = ['BTC', 'ETH', 'ADA'];

  useEffect(() => {
    // Generate mock chart data
    const generateMockData = () => {
      const dataPoints = timeframe === '1h' ? 60 : timeframe === '24h' ? 24 : timeframe === '7d' ? 7 : 30;
      const basePrice = selectedAsset === 'BTC' ? 42000 : selectedAsset === 'ETH' ? 2800 : 0.85;

      return Array.from({ length: dataPoints }, (_, i) => {
        const variation = (Math.random() - 0.5) * 0.1; // ±5% variation
        const price = basePrice * (1 + variation);
        return {
          time: timeframe === '1h' 
            ? `${i}:00` 
            : timeframe === '24h' 
              ? `${i}:00`
              : timeframe === '7d'
                ? `Day ${i + 1}`
                : `Week ${i + 1}`,
          price: price.toFixed(2),
          volume: Math.random() * 1000000
        };
      });
    };

    setChartData(generateMockData());
  }, [timeframe, selectedAsset]);

  const formatPrice = (price) => {
    return selectedAsset === 'ADA' ? `$${price}` : `$${parseInt(price).toLocaleString()}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          Price Chart
        </h2>

        <div className="flex space-x-2">
          {assets.map(asset => (
            <button
              key={asset}
              onClick={() => setSelectedAsset(asset)}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                selectedAsset === asset
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {asset}
            </button>
          ))}
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
            <XAxis 
              dataKey="time" 
              stroke="#6B7280"
              fontSize={12}
              tickLine={false}
            />
            <YAxis 
              stroke="#6B7280"
              fontSize={12}
              tickLine={false}
              tickFormatter={formatPrice}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#1F2937',
                border: 'none',
                borderRadius: '8px',
                color: '#F9FAFB'
              }}
              formatter={(value) => [formatPrice(value), 'Price']}
            />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke="#3B82F6" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#3B82F6' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 flex items-center justify-between text-sm">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
            <span className="text-gray-600 dark:text-gray-400">{selectedAsset}</span>
          </div>
          <div className="text-gray-600 dark:text-gray-400">
            Timeframe: {timeframe}
          </div>
        </div>
        <button className="text-blue-600 dark:text-blue-400 hover:underline">
          View Detailed Chart →
        </button>
      </div>
    </motion.div>
  );
};

export default PriceChart;