import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import NewsPage from '../components/news/NewsPage';
import SentimentAnalysis from '../components/news/SentimentAnalysis';
import SocialFeed from '../components/news/SocialFeed';
import TrendingTopics from '../components/news/TrendingTopics';

const NewsPageContainer = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sentimentFilter, setSentimentFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [news, setNews] = useState([]);

  const categories = [
    { value: 'all', label: 'All News', icon: '📰' },
    { value: 'market', label: 'Market Updates', icon: '📊' },
    { value: 'technology', label: 'Technology', icon: '⚡' },
    { value: 'regulation', label: 'Regulation', icon: '⚖️' },
    { value: 'adoption', label: 'Adoption', icon: '🌐' },
    { value: 'defi', label: 'DeFi', icon: '🔗' }
  ];

  const sentimentOptions = [
    { value: 'all', label: 'All Sentiment' },
    { value: 'positive', label: 'Positive' },
    { value: 'neutral', label: 'Neutral' },
    { value: 'negative', label: 'Negative' }
  ];

  // Mock news data
  useEffect(() => {
    const mockNews = [
      {
        id: 1,
        title: 'Bitcoin Reaches New All-Time High as Institutional Adoption Surges',
        summary: 'Major corporations continue to add Bitcoin to their treasury reserves, driving prices to unprecedented levels.',
        category: 'market',
        sentiment: 'positive',
        source: 'CryptoNews',
        timestamp: '2 hours ago',
        readTime: '3 min read',
        image: '/api/placeholder/400/200'
      },
      {
        id: 2,
        title: 'Ethereum 2.0 Staking Rewards Hit Record Levels',
        summary: 'The transition to proof-of-stake has resulted in higher yields for validators and reduced energy consumption.',
        category: 'technology',
        sentiment: 'positive',
        source: 'ETH Today',
        timestamp: '4 hours ago',
        readTime: '5 min read',
        image: '/api/placeholder/400/200'
      },
      {
        id: 3,
        title: 'New Regulatory Framework Proposed for DeFi Protocols',
        summary: 'Regulators outline comprehensive guidelines for decentralized finance platforms.',
        category: 'regulation',
        sentiment: 'neutral',
        source: 'Regulatory Watch',
        timestamp: '6 hours ago',
        readTime: '7 min read',
        image: '/api/placeholder/400/200'
      }
    ];
    setNews(mockNews);
  }, []);

  const filteredNews = news.filter(article => {
    const matchesCategory = selectedCategory === 'all' || article.category === selectedCategory;
    const matchesSentiment = sentimentFilter === 'all' || article.sentiment === sentimentFilter;
    const matchesSearch = searchTerm === '' || 
      article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      article.summary.toLowerCase().includes(searchTerm.toLowerCase());

    return matchesCategory && matchesSentiment && matchesSearch;
  });

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
            Crypto News & Sentiment
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Stay updated with the latest crypto news and market sentiment
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            🔔 Setup Alerts
          </button>
          <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
            📱 Subscribe to Newsletter
          </button>
        </div>
      </motion.div>

      {/* Sentiment Overview */}
      <SentimentAnalysis />

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700 space-y-4"
      >
        {/* Search */}
        <div className="relative">
          <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search news..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap gap-2">
          {categories.map(category => (
            <button
              key={category.value}
              onClick={() => setSelectedCategory(category.value)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-all flex items-center space-x-2 ${
                selectedCategory === category.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              <span>{category.icon}</span>
              <span>{category.label}</span>
            </button>
          ))}
        </div>

        {/* Sentiment Filter */}
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filter by sentiment:</span>
          <select
            value={sentimentFilter}
            onChange={(e) => setSentimentFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            {sentimentOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* News Articles */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Latest News ({filteredNews.length} articles)
            </h2>
            <div className="space-y-4">
              {filteredNews.map((article, index) => (
                <motion.article
                  key={article.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                  className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer"
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 w-24 h-16 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          article.sentiment === 'positive' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                          article.sentiment === 'negative' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                          'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                        }`}>
                          {article.sentiment}
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">{article.category}</span>
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                        {article.title}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                        {article.summary}
                      </p>
                      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                        <div className="flex items-center space-x-4">
                          <span>{article.source}</span>
                          <span>{article.timestamp}</span>
                          <span>{article.readTime}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button className="hover:text-blue-600 dark:hover:text-blue-400">🔗 Share</button>
                          <button className="hover:text-blue-600 dark:hover:text-blue-400">💾 Save</button>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.article>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <TrendingTopics />
          <SocialFeed />
        </div>
      </div>
    </div>
  );
};

export default NewsPageContainer;