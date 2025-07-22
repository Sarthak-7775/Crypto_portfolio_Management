import React, { useState } from 'react';
import { motion } from 'framer-motion';

const NewsFilters = ({ filters, onFiltersChange, onRefresh }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const categories = [
    { value: 'all', label: 'All News', icon: '📰' },
    { value: 'bitcoin', label: 'Bitcoin', icon: '₿' },
    { value: 'ethereum', label: 'Ethereum', icon: '◈' },
    { value: 'defi', label: 'DeFi', icon: '🏦' },
    { value: 'nft', label: 'NFTs', icon: '🖼️' },
    { value: 'regulation', label: 'Regulation', icon: '⚖️' },
    { value: 'market', label: 'Market Analysis', icon: '📈' }
  ];

  const sentiments = [
    { value: 'all', label: 'All Sentiment', color: 'gray' },
    { value: 'positive', label: 'Positive', color: 'green' },
    { value: 'negative', label: 'Negative', color: 'red' },
    { value: 'neutral', label: 'Neutral', color: 'blue' }
  ];

  const sources = [
    'CoinDesk',
    'Cointelegraph',
    'Decrypt',
    'The Block',
    'Bitcoin Magazine',
    'CryptoNews'
  ];

  const handleSearchChange = (e) => {
    onFiltersChange({
      ...filters,
      search: e.target.value
    });
  };

  const handleCategoryChange = (category) => {
    onFiltersChange({
      ...filters,
      category
    });
  };

  const handleSentimentChange = (sentiment) => {
    onFiltersChange({
      ...filters,
      sentiment
    });
  };

  const handleSourceToggle = (source) => {
    const updatedSources = filters.sources.includes(source)
      ? filters.sources.filter(s => s !== source)
      : [...filters.sources, source];

    onFiltersChange({
      ...filters,
      sources: updatedSources
    });
  };

  const clearFilters = () => {
    onFiltersChange({
      search: '',
      category: 'all',
      sentiment: 'all',
      sources: []
    });
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      {/* Search Bar */}
      <div className="flex items-center space-x-4 mb-6">
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            placeholder="Search crypto news..."
            value={filters.search}
            onChange={handleSearchChange}
            className="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 
                       rounded-lg leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white 
                       placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 
                       focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <button
          onClick={onRefresh}
          className="p-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 
                     bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 
                     dark:hover:bg-gray-600 transition-colors"
          title="Refresh news"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 
                     bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 
                     dark:hover:bg-gray-600 transition-colors"
        >
          <svg className={`w-5 h-5 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
               fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {/* Categories */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Categories</h3>
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category.value}
              onClick={() => handleCategoryChange(category.value)}
              className={`inline-flex items-center px-3 py-2 rounded-full text-sm font-medium transition-colors
                ${filters.category === category.value
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                }`}
            >
              <span className="mr-2">{category.icon}</span>
              {category.label}
            </button>
          ))}
        </div>
      </div>

      {/* Advanced Filters */}
      <motion.div
        initial={false}
        animate={{ height: isExpanded ? 'auto' : 0, opacity: isExpanded ? 1 : 0 }}
        transition={{ duration: 0.2 }}
        className="overflow-hidden"
      >
        <div className="space-y-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          {/* Sentiment Filter */}
          <div>
            <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Sentiment</h3>
            <div className="flex flex-wrap gap-2">
              {sentiments.map((sentiment) => (
                <button
                  key={sentiment.value}
                  onClick={() => handleSentimentChange(sentiment.value)}
                  className={`inline-flex items-center px-3 py-2 rounded-full text-sm font-medium transition-colors
                    ${filters.sentiment === sentiment.value
                      ? `bg-${sentiment.color}-100 text-${sentiment.color}-800 dark:bg-${sentiment.color}-900 dark:text-${sentiment.color}-200`
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                    }`}
                >
                  {sentiment.label}
                </button>
              ))}
            </div>
          </div>

          {/* Sources Filter */}
          <div>
            <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Sources</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {sources.map((source) => (
                <label key={source} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.sources.includes(source)}
                    onChange={() => handleSourceToggle(source)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{source}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Clear Filters */}
          <div className="flex justify-end">
            <button
              onClick={clearFilters}
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 
                         dark:hover:text-blue-300 font-medium"
            >
              Clear all filters
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default NewsFilters;