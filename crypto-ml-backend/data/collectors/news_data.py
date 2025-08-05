"""
News data collector for cryptocurrency sentiment analysis.
Supports multiple news APIs and real-time sentiment scoring.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from textblob import TextBlob
import re

logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """Structure for news articles"""
    title: str
    content: str
    url: str
    source: str
    published_at: datetime
    sentiment_score: float
    sentiment_label: str
    relevance_score: float
    crypto_mentions: List[str]
    article_id: str

class NewsDataCollector:
    """
    News data collector supporting multiple sources and sentiment analysis.
    Implements rate limiting and intelligent content filtering.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
        # API configurations
        self.news_apis = {
            'newsapi': {
                'base_url': 'https://newsapi.org/v2',
                'key': config.get('news_api_key'),
                'rate_limit': asyncio.Semaphore(1000)  # 1000 requests/day for free
            },
            'cryptonews': {
                'base_url': 'https://cryptonews-api.com/api/v1',
                'key': config.get('cryptonews_api_key'),
                'rate_limit': asyncio.Semaphore(100)
            },
            'tradefeeds': {
                'base_url': 'https://data.tradefeeds.com/api/v1',
                'key': config.get('tradefeeds_api_key'),
                'rate_limit': asyncio.Semaphore(50)
            }
        }
        
        # Cryptocurrency keywords for relevance scoring
        self.crypto_keywords = {
            'bitcoin': ['bitcoin', 'btc', 'satoshi'],
            'ethereum': ['ethereum', 'eth', 'ether', 'vitalik'],
            'dogecoin': ['dogecoin', 'doge', 'shiba'],
            'bonk': ['bonk', 'bonk coin'],
            'solana': ['solana', 'sol']
        }
        
        # Sentiment keywords for enhanced analysis
        self.bullish_keywords = [
            'surge', 'rally', 'bullish', 'moon', 'pump', 'breakout', 
            'adoption', 'breakthrough', 'partnership', 'upgrade'
        ]
        self.bearish_keywords = [
            'crash', 'dump', 'bearish', 'decline', 'fall', 'drop',
            'regulation', 'ban', 'hack', 'fraud', 'bubble'
        ]
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def collect_crypto_news(self, 
                                symbols: List[str], 
                                hours_back: int = 24,
                                max_articles: int = 100) -> List[NewsArticle]:
        """
        Collect cryptocurrency news from multiple sources.
        
        Args:
            symbols: Cryptocurrency symbols to search for
            hours_back: How many hours back to search
            max_articles: Maximum articles to return
            
        Returns:
            List of NewsArticle objects
        """
        logger.info(f"Collecting news for {symbols} from last {hours_back} hours")
        
        all_articles = []
        tasks = []
        
        # Create tasks for each API and symbol combination
        for api_name in self.news_apis.keys():
            for symbol in symbols:
                tasks.append(self._fetch_from_api(api_name, symbol, hours_back))
                
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and remove duplicates
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
                    
            # Remove duplicates and sort by relevance
            unique_articles = self._deduplicate_articles(all_articles)
            sorted_articles = sorted(unique_articles, 
                                   key=lambda x: (x.relevance_score, x.published_at), 
                                   reverse=True)
            
            logger.info(f"Collected {len(sorted_articles)} unique articles")
            return sorted_articles[:max_articles]
            
        except Exception as e:
            logger.error(f"Error collecting crypto news: {e}")
            return []
            
    async def _fetch_from_api(self, api_name: str, symbol: str, hours_back: int) -> List[NewsArticle]:
        """Fetch articles from a specific API"""
        api_config = self.news_apis.get(api_name)
        if not api_config or not api_config['key']:
            return []
            
        async with api_config['rate_limit']:
            try:
                if api_name == 'newsapi':
                    return await self._fetch_newsapi(symbol, hours_back)
                elif api_name == 'cryptonews':
                    return await self._fetch_cryptonews(symbol, hours_back)
                elif api_name == 'tradefeeds':
                    return await self._fetch_tradefeeds(symbol, hours_back)
                    
            except Exception as e:
                logger.error(f"Error fetching from {api_name} for {symbol}: {e}")
                
        return []
        
    async def _fetch_newsapi(self, symbol: str, hours_back: int) -> List[NewsArticle]:
        """Fetch articles from NewsAPI"""
        api_config = self.news_apis['newsapi']
        
        # Build search query
        keywords = self.crypto_keywords.get(symbol.lower(), [symbol])
        query = ' OR '.join(keywords)
        
        params = {
            'q': f'({query}) AND (cryptocurrency OR crypto OR blockchain)',
            'apiKey': api_config['key'],
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': (datetime.now() - timedelta(hours=hours_back)).isoformat(),
            'pageSize': 100
        }
        
        url = f"{api_config['base_url']}/everything"
        
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_newsapi_response(data, symbol)
            else:
                logger.warning(f"NewsAPI error {response.status}")
                
        return []
        
    async def _fetch_cryptonews(self, symbol: str, hours_back: int) -> List[NewsArticle]:
        """Fetch articles from CryptoNews API"""
        # Implementation similar to NewsAPI but with crypto-specific endpoints
        api_config = self.news_apis['cryptonews']
        
        params = {
            'tickers': symbol.upper(),
            'items': 50,
            'token': api_config['key']
        }
        
        url = f"{api_config['base_url']}/news"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_cryptonews_response(data, symbol)
        except Exception as e:
            logger.error(f"CryptoNews API error: {e}")
            
        return []
        
    async def _fetch_tradefeeds(self, symbol: str, hours_back: int) -> List[NewsArticle]:
        """Fetch articles from TradeFeeds API with sentiment"""
        api_config = self.news_apis['tradefeeds']
        
        params = {
            'key': api_config['key'],
            'ticker': symbol.upper(),
            'limit': 50
        }
        
        url = f"{api_config['base_url']}/crypto_news"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_tradefeeds_response(data, symbol)
        except Exception as e:
            logger.error(f"TradeFeeds API error: {e}")
            
        return []
        
    def _parse_newsapi_response(self, data: Dict, symbol: str) -> List[NewsArticle]:
        """Parse NewsAPI response into NewsArticle objects"""
        articles = []
        
        for article_data in data.get('articles', []):
            try:
                # Extract and clean content
                title = article_data.get('title', '')
                content = article_data.get('description', '') or article_data.get('content', '')
                
                if not title or not content:
                    continue
                    
                # Perform sentiment analysis
                sentiment_score, sentiment_label = self._analyze_sentiment(title + ' ' + content)
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance(title + ' ' + content, symbol)
                
                # Extract crypto mentions
                crypto_mentions = self._extract_crypto_mentions(title + ' ' + content)
                
                article = NewsArticle(
                    title=title,
                    content=content,
                    url=article_data.get('url', ''),
                    source=article_data.get('source', {}).get('name', 'NewsAPI'),
                    published_at=datetime.fromisoformat(
                        article_data.get('publishedAt', '').replace('Z', '+00:00')
                    ),
                    sentiment_score=sentiment_score,
                    sentiment_label=sentiment_label,
                    relevance_score=relevance_score,
                    crypto_mentions=crypto_mentions,
                    article_id=self._generate_article_id(article_data.get('url', ''))
                )
                
                articles.append(article)
                
            except Exception as e:
                logger.warning(f"Error parsing article: {e}")
                continue
                
        return articles
        
    def _parse_cryptonews_response(self, data: Dict, symbol: str) -> List[NewsArticle]:
        """Parse CryptoNews API response"""
        articles = []
        
        for article_data in data.get('data', []):
            try:
                title = article_data.get('title', '')
                content = article_data.get('text', '')
                
                sentiment_score, sentiment_label = self._analyze_sentiment(title + ' ' + content)
                relevance_score = self._calculate_relevance(title + ' ' + content, symbol)
                crypto_mentions = self._extract_crypto_mentions(title + ' ' + content)
                
                article = NewsArticle(
                    title=title,
                    content=content,
                    url=article_data.get('news_url', ''),
                    source=article_data.get('source_name', 'CryptoNews'),
                    published_at=datetime.fromisoformat(article_data.get('date', '')),
                    sentiment_score=sentiment_score,
                    sentiment_label=sentiment_label,
                    relevance_score=relevance_score,
                    crypto_mentions=crypto_mentions,
                    article_id=self._generate_article_id(article_data.get('news_url', ''))
                )
                
                articles.append(article)
                
            except Exception as e:
                logger.warning(f"Error parsing CryptoNews article: {e}")
                continue
                
        return articles
        
    def _parse_tradefeeds_response(self, data: Dict, symbol: str) -> List[NewsArticle]:
        """Parse TradeFeeds API response which includes pre-computed sentiment"""
        articles = []
        
        for article_data in data.get('data', []):
            try:
                # TradeFeeds provides sentiment analysis
                sentiment_raw = article_data.get('sentiment', 'neutral')
                sentiment_score = self._convert_sentiment_to_score(sentiment_raw)
                
                article = NewsArticle(
                    title=article_data.get('news_title', ''),
                    content=article_data.get('text', ''),
                    url=article_data.get('news_link', ''),
                    source='TradeFeeds',
                    published_at=datetime.fromisoformat(article_data.get('published_at', '')),
                    sentiment_score=sentiment_score,
                    sentiment_label=sentiment_raw,
                    relevance_score=self._calculate_relevance(
                        article_data.get('news_title', '') + ' ' + article_data.get('text', ''), 
                        symbol
                    ),
                    crypto_mentions=article_data.get('tickers', []),
                    article_id=self._generate_article_id(article_data.get('news_link', ''))
                )
                
                articles.append(article)
                
            except Exception as e:
                logger.warning(f"Error parsing TradeFeeds article: {e}")
                continue
                
        return articles
        
    def _analyze_sentiment(self, text: str) -> tuple[float, str]:
        """
        Analyze sentiment of text using enhanced cryptocurrency-specific analysis.
        
        Returns:
            Tuple of (sentiment_score, sentiment_label)
            sentiment_score: Float between -1 (bearish) and 1 (bullish)
            sentiment_label: 'bullish', 'bearish', or 'neutral'
        """
        try:
            # Basic TextBlob sentiment
            blob = TextBlob(text.lower())
            base_sentiment = blob.sentiment.polarity
            
            # Enhance with crypto-specific keywords
            bullish_matches = sum(1 for keyword in self.bullish_keywords if keyword in text.lower())
            bearish_matches = sum(1 for keyword in self.bearish_keywords if keyword in text.lower())
            
            # Weight adjustment based on crypto-specific terms
            crypto_weight = 0.3
            keyword_sentiment = (bullish_matches - bearish_matches) * crypto_weight
            
            # Combined sentiment score
            final_sentiment = base_sentiment + keyword_sentiment
            final_sentiment = max(-1.0, min(1.0, final_sentiment))  # Clamp to [-1, 1]
            
            # Convert to label
            if final_sentiment > 0.1:
                label = 'bullish'
            elif final_sentiment < -0.1:
                label = 'bearish'
            else:
                label = 'neutral'
                
            return final_sentiment, label
            
        except Exception as e:
            logger.warning(f"Error in sentiment analysis: {e}")
            return 0.0, 'neutral'
            
    def _calculate_relevance(self, text: str, symbol: str) -> float:
        """Calculate relevance score of article to specific cryptocurrency"""
        text_lower = text.lower()
        symbol_lower = symbol.lower()
        
        relevance_score = 0.0
        
        # Direct symbol mentions
        symbol_mentions = text_lower.count(symbol_lower)
        relevance_score += symbol_mentions * 0.3
        
        # Keyword mentions
        keywords = self.crypto_keywords.get(symbol_lower, [symbol_lower])
        for keyword in keywords:
            relevance_score += text_lower.count(keyword) * 0.2
            
        # General crypto relevance
        crypto_terms = ['cryptocurrency', 'bitcoin', 'blockchain', 'crypto', 'digital currency']
        for term in crypto_terms:
            if term in text_lower:
                relevance_score += 0.1
                
        return min(relevance_score, 1.0)  # Cap at 1.0
        
    def _extract_crypto_mentions(self, text: str) -> List[str]:
        """Extract all cryptocurrency mentions from text"""
        mentions = set()
        text_lower = text.lower()
        
        # Check for all known cryptocurrencies
        for crypto, keywords in self.crypto_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    mentions.add(crypto.upper())
                    
        return list(mentions)
        
    def _convert_sentiment_to_score(self, sentiment_label: str) -> float:
        """Convert sentiment label to numerical score"""
        mapping = {
            'positive': 0.7,
            'bullish': 0.8,
            'negative': -0.7,
            'bearish': -0.8,
            'neutral': 0.0
        }
        return mapping.get(sentiment_label.lower(), 0.0)
        
    def _generate_article_id(self, url: str) -> str:
        """Generate unique article ID from URL"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()
        
    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            # Simple deduplication based on title similarity
            title_key = re.sub(r'[^a-zA-Z0-9\s]', '', article.title.lower())
            title_key = ' '.join(title_key.split())
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
                
        return unique_articles
        
    async def get_sentiment_summary(self, articles: List[NewsArticle]) -> Dict[str, Any]:
        """Generate sentiment summary from collected articles"""
        if not articles:
            return {
                'overall_sentiment': 0.0,
                'sentiment_label': 'neutral',
                'total_articles': 0,
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0,
                'average_relevance': 0.0
            }
            
        sentiments = [article.sentiment_score for article in articles]
        overall_sentiment = sum(sentiments) / len(sentiments)
        
        bullish_count = sum(1 for s in sentiments if s > 0.1)
        bearish_count = sum(1 for s in sentiments if s < -0.1)
        neutral_count = len(sentiments) - bullish_count - bearish_count
        
        average_relevance = sum(article.relevance_score for article in articles) / len(articles)
        
        # Determine overall label
        if overall_sentiment > 0.1:
            sentiment_label = 'bullish'
        elif overall_sentiment < -0.1:
            sentiment_label = 'bearish'
        else:
            sentiment_label = 'neutral'
            
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_label': sentiment_label,
            'total_articles': len(articles),
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'average_relevance': average_relevance,
            'timestamp': datetime.now()
        }
