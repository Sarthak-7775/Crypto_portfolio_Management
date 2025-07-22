import React from 'react';
import { motion } from 'framer-motion';

const SentimentOverview = ({ data }) => {
  if (!data) return null;

  const { positive, negative, neutral, total, trend } = data;

  const getPercentage = (value) => ((value / total) * 100).toFixed(1);

  const getTrendIcon = () => {
    if (trend > 0) return { icon: '📈', color: 'text-green-500', text: 'Bullish Sentiment' };
    if (trend < 0) return { icon: '📉', color: 'text-red-500', text: 'Bearish Sentiment' };
    return { icon: '➡️', color: 'text-yellow-500', text: 'Neutral Market' };
  };

  const trendInfo = getTrendIcon();

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Market Sentiment</h2>
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{trendInfo.icon}</span>
          <span className="text-sm opacity-90">{trendInfo.text}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Total Articles */}
        <div className="text-center">
          <div className="text-2xl font-bold">{total.toLocaleString()}</div>
          <div className="text-sm opacity-90">Total Articles</div>
        </div>

        {/* Positive Sentiment */}
        <div className="text-center">
          <div className="text-2xl font-bold text-green-300">{getPercentage(positive)}%</div>
          <div className="text-sm opacity-90">Bullish ({positive.toLocaleString()})</div>
          <div className="w-full bg-white/20 rounded-full h-2 mt-2">
            <div 
              className="bg-green-300 h-2 rounded-full transition-all duration-500"
              style={{ width: `${getPercentage(positive)}%` }}
            />
          </div>
        </div>

        {/* Negative Sentiment */}
        <div className="text-center">
          <div className="text-2xl font-bold text-red-300">{getPercentage(negative)}%</div>
          <div className="text-sm opacity-90">Bearish ({negative.toLocaleString()})</div>
          <div className="w-full bg-white/20 rounded-full h-2 mt-2">
            <div 
              className="bg-red-300 h-2 rounded-full transition-all duration-500"
              style={{ width: `${getPercentage(negative)}%` }}
            />
          </div>
        </div>

        {/* Neutral Sentiment */}
        <div className="text-center">
          <div className="text-2xl font-bold text-yellow-300">{getPercentage(neutral)}%</div>
          <div className="text-sm opacity-90">Neutral ({neutral.toLocaleString()})</div>
          <div className="w-full bg-white/20 rounded-full h-2 mt-2">
            <div 
              className="bg-yellow-300 h-2 rounded-full transition-all duration-500"
              style={{ width: `${getPercentage(neutral)}%` }}
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default SentimentOverview;