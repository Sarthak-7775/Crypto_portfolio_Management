
import React from 'react';
import { motion } from 'framer-motion';
import moment from 'moment';
import SentimentBadge from './SentimentBadge';


const NewsCard = ({ article, onClick }) => {
  const {
    title,
    description,
    imageUrl,
    source,
    publishedAt,
    sentiment,
    url,
    author
  } = article;

  const timeAgo = moment(publishedAt).fromNow();

  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, boxShadow: "0 10px 25px rgba(0,0,0,0.1)" }}
      transition={{ duration: 0.2 }}
      className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 
                 dark:border-gray-700 overflow-hidden cursor-pointer group"
      onClick={onClick}
    >
      {/* Image */}
      {imageUrl && (
        <div className="aspect-video overflow-hidden">
          <img
            src={imageUrl}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        </div>
      )}

      {/* Content */}
      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-blue-600 dark:text-blue-400 bg-blue-50 
                           dark:bg-blue-900/30 px-2 py-1 rounded-full">
              {source}
            </span>
            <SentimentBadge sentiment={sentiment} size="sm" />
          </div>
          <time className="text-xs text-gray-500 dark:text-gray-400">
            {timeAgo}
          </time>
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white line-clamp-2 
                       group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
          {title}
        </h3>

        {/* Description */}
        {description && (
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-300 line-clamp-3">
            {description}
          </p>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          {author && (
            <span className="text-xs text-gray-500 dark:text-gray-400">
              By {author}
            </span>
          )}
          <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            Read more
          </div>
        </div>
      </div>
    </motion.article>
  );
};

export default NewsCard;