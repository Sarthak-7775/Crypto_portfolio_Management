import React, { useState, useEffect } from 'react';
import InfiniteScroll from 'react-infinite-scroll-component';
import NewsCard from './NewsCard';
import NewsFilters from './NewsFilters';
import ArticleModal from './ArticleModal';
import LoadingSpinner from './LoadingSpinner';
import SentimentOverview from './SentimentOverview';
import useNewsFeed from './hooks/useNewsFeed';
import useDebounce from './hooks/useDebounce';

const NewsFeed = () => {
  const [filters, setFilters] = useState({
    search: '',
    category: 'all',
    sentiment: 'all',
    sources: []
  });

  const [selectedArticle, setSelectedArticle] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const debouncedSearch = useDebounce(filters.search, 500);

  const {
    articles,
    loading,
    hasMore,
    error,
    sentimentData,
    fetchMore,
    refreshFeed
  } = useNewsFeed({ ...filters, search: debouncedSearch });

  const handleCardClick = (article) => {
    setSelectedArticle(article);
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    setSelectedArticle(null);
  };

  const handleRefresh = () => {
    refreshFeed();
  };

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          Failed to load news
        </h3>
        <p className="text-gray-500 dark:text-gray-400 mb-4">{error.message}</p>
        <button
          onClick={handleRefresh}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium 
                     rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none 
                     focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Sentiment Overview */}
      <SentimentOverview data={sentimentData} />

      {/* Filters */}
      <NewsFilters 
        filters={filters} 
        onFiltersChange={setFilters}
        onRefresh={handleRefresh}
      />

      {/* News Feed */}
      <InfiniteScroll
        dataLength={articles.length}
        next={fetchMore}
        hasMore={hasMore}
        loader={<LoadingSpinner />}
        endMessage={
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">
              📰 You've reached the end of the news feed!
            </p>
          </div>
        }
        refreshFunction={handleRefresh}
        pullDownToRefresh
        pullDownToRefreshContent={
          <h3 className="text-center py-4 text-gray-600 dark:text-gray-400">
            ↓ Pull down to refresh
          </h3>
        }
        releaseToRefreshContent={
          <h3 className="text-center py-4 text-gray-600 dark:text-gray-400">
            ↑ Release to refresh
          </h3>
        }
      >
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {articles.map((article, index) => (
            <NewsCard
              key={`${article.id}-${index}`}
              article={article}
              onClick={() => handleCardClick(article)}
            />
          ))}
        </div>
      </InfiniteScroll>

      {/* Article Modal */}
      {showModal && selectedArticle && (
        <ArticleModal
          article={selectedArticle}
          isOpen={showModal}
          onClose={handleModalClose}
        />
      )}

      {/* Initial Loading */}
      {loading && articles.length === 0 && (
        <div className="text-center py-12">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">
            Loading latest crypto news...
          </p>
        </div>
      )}
    </div>
  );
};

export default NewsFeed;