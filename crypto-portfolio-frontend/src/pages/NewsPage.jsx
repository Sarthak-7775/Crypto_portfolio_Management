import React from 'react';
import NewsFeed from '../components/news/NewsFeed';

const NewsPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Crypto News
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Stay updated with the latest cryptocurrency news and market insights from trusted sources
          </p>
        </div>
        <NewsFeed />
      </div>
    </div>
  );
};

export default NewsPage;