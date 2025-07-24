const API_ENDPOINTS = {
  NEWSAPI: 'https://newsapi.org/v2/everything',
  NEWSDATA: 'https://newsdata.io/api/1/news',
  CRYPTOPANIC: 'https://cryptopanic.com/api/v1/posts/'
};

class NewsService {
  constructor() {
    this.apiKey = process.env.REACT_APP_NEWS_API_KEY;
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
  }

  async fetchCryptoNews(params) {
    const {
      search = '',
      category = 'all',
      sentiment = 'all',
      sources = [],
      page = 1,
      pageSize = 2,
      signal
    } = params;

    // Create cache key
    const cacheKey = JSON.stringify({ search, category, sentiment, sources, page, pageSize });

    // Check cache
    const cached = this.cache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    try {
      // Use NewsAPI as primary source
      const response = await this.fetchFromNewsAPI({
        search,
        category,
        sources,
        page,
        pageSize,
        signal
      });

      // Add sentiment analysis
      const articlesWithSentiment = await this.addSentimentAnalysis(response.articles);

      // Calculate sentiment overview
      const sentimentOverview = this.calculateSentimentOverview(articlesWithSentiment);

      const result = {
        articles: articlesWithSentiment,
        hasMore: response.hasMore,
        sentiment: sentimentOverview
      };

      // Cache the result
      this.cache.set(cacheKey, {
        data: result,
        timestamp: Date.now()
      });

      return result;

    } catch (error) {
      console.error('Failed to fetch crypto news:', error);
      throw error;
    }
  }

  async fetchFromNewsAPI({ search, category, sources, page, pageSize, signal }) {
    const params = new URLSearchParams({
      apiKey: this.apiKey,
      language: 'en',
      sortBy: 'publishedAt',
      pageSize: pageSize.toString(),
      page: page.toString()
    });

    // Build search query
    let query = 'cryptocurrency OR bitcoin OR ethereum OR crypto OR blockchain';

    if (search.trim()) {
      query += ` AND (${search.trim()})`;
    }

    if (category && category !== 'all') {
      const categoryTerms = this.getCategorySearchTerms(category);
      query += ` AND (${categoryTerms})`;
    }

    params.append('q', query);

    // Add sources filter
    if (sources.length > 0) {
      params.append('domains', sources.map(s => this.getSourceDomain(s)).join(','));
    }

    // Add a small delay to avoid hitting NewsAPI rate limits (1 req/sec for free tier)
    await new Promise(resolve => setTimeout(resolve, 1200));
    const response = await fetch(`${API_ENDPOINTS.NEWSAPI}?${params}`, { signal });

    if (!response.ok) {
      throw new Error(`NewsAPI error: ${response.status}`);
    }

    const data = await response.json();

    return {
      articles: data.articles.map(this.normalizeArticle).filter(article => article.title),
      hasMore: data.articles.length === pageSize,
      totalResults: data.totalResults
    };
  }

  getCategorySearchTerms(category) {
    const categoryMap = {
      bitcoin: 'bitcoin OR BTC',
      ethereum: 'ethereum OR ETH OR ether',
      defi: 'DeFi OR "decentralized finance" OR yield OR staking',
      nft: 'NFT OR "non-fungible token" OR OpenSea OR collectibles',
      regulation: 'regulation OR SEC OR law OR legal OR government',
      market: 'market OR price OR trading OR analysis OR bull OR bear'
    };

    return categoryMap[category] || category;
  }

  getSourceDomain(source) {
    const domainMap = {
      'CoinDesk': 'coindesk.com',
      'Cointelegraph': 'cointelegraph.com',
      'Decrypt': 'decrypt.co',
      'The Block': 'theblockcrypto.com',
      'Bitcoin Magazine': 'bitcoinmagazine.com',
      'CryptoNews': 'cryptonews.com'
    };

    return domainMap[source] || source.toLowerCase().replace(' ', '') + '.com';
  }

  normalizeArticle(article) {
    return {
      id: article.url,
      title: article.title,
      description: article.description,
      content: article.content,
      url: article.url,
      imageUrl: article.urlToImage,
      source: article.source.name,
      author: article.author,
      publishedAt: article.publishedAt,
      sentiment: null, // Will be filled by sentiment analysis
      tags: this.extractTags(article.title + ' ' + (article.description || ''))
    };
  }

  extractTags(text) {
    const cryptoTerms = [
      'bitcoin', 'btc', 'ethereum', 'eth', 'blockchain', 'crypto', 'defi',
      'nft', 'dao', 'web3', 'metaverse', 'trading', 'mining', 'staking',
      'yield', 'bull', 'bear', 'hodl', 'altcoin', 'regulation', 'sec'
    ];

    const lowerText = text.toLowerCase();
    return cryptoTerms.filter(term => lowerText.includes(term));
  }

  async addSentimentAnalysis(articles) {
    // Simple rule-based sentiment analysis
    // In production, you'd use a proper NLP service
    return articles.map(article => ({
      ...article,
      sentiment: this.analyzeSentiment(article.title + ' ' + (article.description || ''))
    }));
  }

  analyzeSentiment(text) {
    const lowerText = text.toLowerCase();

    const positiveWords = [
      'bullish', 'surge', 'rally', 'gains', 'growth', 'rise', 'up', 'increase',
      'adoption', 'breakthrough', 'success', 'positive', 'optimistic', 'green'
    ];

    const negativeWords = [
      'bearish', 'crash', 'fall', 'drop', 'decline', 'loss', 'down', 'decrease',
      'fear', 'panic', 'crisis', 'negative', 'risk', 'warning', 'red'
    ];

    let positiveScore = 0;
    let negativeScore = 0;

    positiveWords.forEach(word => {
      if (lowerText.includes(word)) positiveScore++;
    });

    negativeWords.forEach(word => {
      if (lowerText.includes(word)) negativeScore++;
    });

    if (positiveScore > negativeScore) return 'positive';
    if (negativeScore > positiveScore) return 'negative';
    return 'neutral';
  }

  calculateSentimentOverview(articles) {
    const sentiment = {
      positive: 0,
      negative: 0,
      neutral: 0,
      total: articles.length,
      trend: 0
    };

    articles.forEach(article => {
      if (article.sentiment === 'positive') sentiment.positive++;
      else if (article.sentiment === 'negative') sentiment.negative++;
      else sentiment.neutral++;
    });

    // Calculate trend (-1 to 1)
    sentiment.trend = (sentiment.positive - sentiment.negative) / sentiment.total;

    return sentiment;
  }

  clearCache() {
    this.cache.clear();
  }
}

export const newsService = new NewsService();