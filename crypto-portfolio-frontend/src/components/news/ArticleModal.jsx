import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import SentimentBadge from './SentimentBadge';

const ArticleModal = ({ article, isOpen, onClose }) => {
  if (!isOpen || !article) return null;

  const timeAgo = formatDistanceToNow(new Date(article.publishedAt), { addSuffix: true });

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleReadFullArticle = () => {
    window.open(article.url, '_blank', 'noopener,noreferrer');
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 overflow-hidden"
        onClick={handleBackdropClick}
      >
        {/* Backdrop */}
        <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

        {/* Modal */}
        <div className="relative z-10 h-full flex items-center justify-center p-4">
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            transition={{ type: "spring", duration: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden"
          >
            {/* Header */}
            <div className="relative">
              {article.imageUrl && (
                <div className="aspect-video w-full">
                  <img
                    src={article.imageUrl}
                    alt={article.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
                </div>
              )}

              {/* Close Button */}
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 bg-white/90 dark:bg-gray-800/90 
                           rounded-full text-gray-600 dark:text-gray-400 hover:text-gray-800 
                           dark:hover:text-gray-200 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Content */}
            <div className="p-6 max-h-[60vh] overflow-y-auto">
              {/* Meta Information */}
              <div className="flex flex-wrap items-center gap-3 mb-4">
                <span className="text-sm font-medium text-blue-600 dark:text-blue-400 
                               bg-blue-50 dark:bg-blue-900/30 px-3 py-1 rounded-full">
                  {article.source}
                </span>
                <SentimentBadge sentiment={article.sentiment} />
                <time className="text-sm text-gray-500 dark:text-gray-400">
                  {timeAgo}
                </time>
                {article.author && (
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    By {article.author}
                  </span>
                )}
              </div>

              {/* Title */}
              <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-4">
                {article.title}
              </h1>

              {/* Description */}
              {article.description && (
                <p className="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed">
                  {article.description}
                </p>
              )}

              {/* Content */}
              {article.content && (
                <div className="prose dark:prose-dark max-w-none">
                  <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                    {article.content}
                  </p>
                </div>
              )}

              {/* Tags */}
              {article.tags && article.tags.length > 0 && (
                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {article.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 
                                 text-gray-700 dark:text-gray-300 rounded-full"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="px-6 py-4 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={onClose}
                    className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 
                             dark:hover:text-gray-200 transition-colors"
                  >
                    Close
                  </button>
                </div>

                <button
                  onClick={handleReadFullArticle}
                  className="inline-flex items-center px-6 py-2 bg-blue-600 hover:bg-blue-700 
                           text-white rounded-lg transition-colors"
                >
                  <span>Read Full Article</span>
                  <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ArticleModal;