import { useState, useEffect, useCallback, useRef } from 'react';
import { newsService } from '../services/newsService';

const useNewsFeed = (filters) => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const [sentimentData, setSentimentData] = useState(null);

  const abortControllerRef = useRef(null);
  const filtersRef = useRef(filters);

  // Update filters ref when filters change
  useEffect(() => {
    filtersRef.current = filters;
  }, [filters]);

  const fetchNews = useCallback(async (pageNum = 1, isRefresh = false) => {
    try {
      // Cancel previous request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller
      abortControllerRef.current = new AbortController();

      if (isRefresh) {
        setLoading(true);
        setError(null);
      }

      const response = await newsService.fetchCryptoNews({
        ...filtersRef.current,
        page: pageNum,
        signal: abortControllerRef.current.signal
      });

      const { articles: newArticles, hasMore: moreAvailable, sentiment } = response;

      if (isRefresh || pageNum === 1) {
        setArticles(newArticles);
        setSentimentData(sentiment);
      } else {
        setArticles(prev => [...prev, ...newArticles]);
      }

      setHasMore(moreAvailable);
      setPage(pageNum);
      setError(null);

    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err);
        console.error('Failed to fetch news:', err);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load and filter changes
  useEffect(() => {
    setPage(1);
    setHasMore(true);
    fetchNews(1, true);
  }, [filters, fetchNews]);

  // Fetch more articles (infinite scroll)
  const fetchMore = useCallback(() => {
    if (!loading && hasMore) {
      fetchNews(page + 1);
    }
  }, [loading, hasMore, page, fetchNews]);

  // Refresh feed
  const refreshFeed = useCallback(() => {
    setPage(1);
    setHasMore(true);
    fetchNews(1, true);
  }, [fetchNews]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    articles,
    loading,
    error,
    hasMore,
    sentimentData,
    fetchMore,
    refreshFeed
  };
};

export default useNewsFeed;