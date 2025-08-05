"""
Social media data collector for cryptocurrency sentiment analysis.
Supports Twitter, Reddit, and other social platforms with advanced sentiment processing.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import re
import tweepy
import praw
from textblob import TextBlob
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class SocialPost:
    """Structure for social media posts"""
    post_id: str
    platform: str
    content: str
    author: str
    timestamp: datetime
    sentiment_score: float
    sentiment_label: str
    engagement_metrics: Dict[str, int]  # likes, retweets, comments, etc.
    crypto_mentions: List[str]
    influence_score: float
    hashtags: List[str]
    url: Optional[str] = None

class SocialDataCollector:
    """
    Social media data collector with advanced sentiment analysis and influence scoring.
    Supports Twitter API v2, Reddit API, and other social platforms.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Twitter API v2 setup
        self.twitter_bearer_token = config.get('twitter_bearer_token')
        self.twitter_client = None
        if self.twitter_bearer_token:
            self.twitter_client = tweepy.Client(bearer_token=self.twitter_bearer_token)
            
        # Reddit API setup
        self.reddit_client = None
        reddit_config = config.get('reddit', {})
        if all(reddit_config.get(key) for key in ['client_id', 'client_secret', 'user_agent']):
            self.reddit_client = praw.Reddit(
                client_id=reddit_config['client_id'],
                client_secret=reddit_config['client_secret'],
                user_agent=reddit_config['user_agent']
            )
            
        # Rate limiting
        self.rate_limits = {
            'twitter': asyncio.Semaphore(300),  # 300 requests per 15 minutes
            'reddit': asyncio.Semaphore(60),    # 60 requests per minute
        }
        
        # Crypto-related hashtags and keywords
        self.crypto_hashtags = {
            'bitcoin': ['#bitcoin', '#btc', '#bitcoins'],
            'ethereum': ['#ethereum', '#eth', '#ether'],
            'dogecoin': ['#dogecoin', '#doge', '#shibainu'],
            'bonk': ['#bonk', '#bonkcoin'],
            'solana': ['#solana', '#sol']
        }
        
        # Influence scoring factors
        self.influence_weights = {
            'follower_count': 0.3,
            'engagement_rate': 0.4,
            'account_age': 0.1,
            'verified_status': 0.2
        }
        
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
            
    async def collect_social_sentiment(self, 
                                     symbols: List[str], 
                                     hours_back: int = 24,
                                     max_posts: int = 1000) -> List[SocialPost]:
        """
        Collect social media posts mentioning cryptocurrencies.
        
        Args:
            symbols: Cryptocurrency symbols to search for
            hours_back: How many hours back to search
            max_posts: Maximum posts to return
            
        Returns:
            List of SocialPost objects
        """
        logger.info(f"Collecting social sentiment for {symbols} from last {hours_back} hours")
        
        all_posts = []
        tasks = []
        
        # Collect from Twitter
        if self.twitter_client:
            for symbol in symbols:
                tasks.append(self._collect_twitter_posts(symbol, hours_back, max_posts // len(symbols) // 2))
                
        # Collect from Reddit
        if self.reddit_client:
            for symbol in symbols:
                tasks.append(self._collect_reddit_posts(symbol, hours_back, max_posts // len(symbols) // 2))
                
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_posts.extend(result)
                    
            # Sort by influence score and timestamp
            sorted_posts = sorted(all_posts, 
                                key=lambda x: (x.influence_score, x.timestamp), 
                                reverse=True)
            
            logger.info(f"Collected {len(sorted_posts)} social media posts")
            return sorted_posts[:max_posts]
            
        except Exception as e:
            logger.error(f"Error collecting social sentiment: {e}")
            return []
            
    async def _collect_twitter_posts(self, symbol: str, hours_back: int, limit: int) -> List[SocialPost]:
        """Collect tweets mentioning a specific cryptocurrency"""
        async with self.rate_limits['twitter']:
            try:
                # Build search query
                hashtags = self.crypto_hashtags.get(symbol.lower(), [f'#{symbol}'])
                search_terms = [symbol, f'${symbol}'] + hashtags
                query = ' OR '.join(search_terms) + ' -is:retweet lang:en'
                
                # Calculate time range
                start_time = datetime.utcnow() - timedelta(hours=hours_back)
                
                # Search tweets using Twitter API v2
                tweets = tweepy.Paginator(
                    self.twitter_client.search_recent_tweets,
                    query=query,
                    start_time=start_time,
                    tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                    user_fields=['followers_count', 'verified', 'created_at'],
                    expansions=['author_id'],
                    max_results=min(limit, 100)
                ).flatten(limit=limit)
                
                posts = []
                for tweet in tweets:
                    try:
                        # Get user info
                        user_info = self._get_user_info(tweet.author_id, tweets.includes.get('users', []))
                        
                        # Calculate sentiment
                        sentiment_score, sentiment_label = self._analyze_sentiment(tweet.text)
                        
                        # Extract crypto mentions and hashtags
                        crypto_mentions = self._extract_crypto_mentions(tweet.text)
                        hashtags = self._extract_hashtags(tweet.text)
                        
                        # Calculate influence score
                        influence_score = self._calculate_influence_score(user_info, tweet.public_metrics)
                        
                        post = SocialPost(
                            post_id=tweet.id,
                            platform='twitter',
                            content=tweet.text,
                            author=user_info.get('username', 'unknown'),
                            timestamp=tweet.created_at,
                            sentiment_score=sentiment_score,
                            sentiment_label=sentiment_label,
                            engagement_metrics={
                                'likes': tweet.public_metrics.get('like_count', 0),
                                'retweets': tweet.public_metrics.get('retweet_count', 0),
                                'replies': tweet.public_metrics.get('reply_count', 0),
                                'quotes': tweet.public_metrics.get('quote_count', 0)
                            },
                            crypto_mentions=crypto_mentions,
                            influence_score=influence_score,
                            hashtags=hashtags,
                            url=f"https://twitter.com/i/status/{tweet.id}"
                        )
                        
                        posts.append(post)
                        
                    except Exception as e:
                        logger.warning(f"Error processing tweet {tweet.id}: {e}")
                        continue
                        
                return posts
                
            except Exception as e:
                logger.error(f"Error collecting Twitter posts for {symbol}: {e}")
                return []
                
    async def _collect_reddit_posts(self, symbol: str, hours_back: int, limit: int) -> List[SocialPost]:
        """Collect Reddit posts and comments mentioning a specific cryptocurrency"""
        async with self.rate_limits['reddit']:
            try:
                posts = []
                
                # Search in crypto-related subreddits
                crypto_subreddits = [
                    'cryptocurrency', 'bitcoin', 'ethereum', 'dogecoin', 
                    'cryptomarkets', 'altcoin', 'defi', 'solana'
                ]
                
                cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
                
                for subreddit_name in crypto_subreddits:
                    try:
                        subreddit = self.reddit_client.subreddit(subreddit_name)
                        
                        # Search recent posts
                        for submission in subreddit.search(symbol, sort='new', time_filter='day', limit=limit // len(crypto_subreddits)):
                            if datetime.fromtimestamp(submission.created_utc) < cutoff_time:
                                continue
                                
                            # Process submission
                            sentiment_score, sentiment_label = self._analyze_sentiment(
                                submission.title + ' ' + (submission.selftext or '')
                            )
                            
                            crypto_mentions = self._extract_crypto_mentions(
                                submission.title + ' ' + (submission.selftext or '')
                            )
                            
                            # Calculate influence based on Reddit metrics
                            influence_score = self._calculate_reddit_influence(submission)
                            
                            post = SocialPost(
                                post_id=submission.id,
                                platform='reddit',
                                content=submission.title + ' ' + (submission.selftext or ''),
                                author=str(submission.author) if submission.author else 'deleted',
                                timestamp=datetime.fromtimestamp(submission.created_utc),
                                sentiment_score=sentiment_score,
                                sentiment_label=sentiment_label,
                                engagement_metrics={
                                    'upvotes': submission.score,
                                    'comments': submission.num_comments,
                                    'upvote_ratio': submission.upvote_ratio
                                },
                                crypto_mentions=crypto_mentions,
                                influence_score=influence_score,
                                hashtags=[],
                                url=f"https://reddit.com{submission.permalink}"
                            )
                            
                            posts.append(post)
                            
                    except Exception as e:
                        logger.warning(f"Error processing subreddit {subreddit_name}: {e}")
                        continue
                        
                return posts
                
            except Exception as e:
                logger.error(f"Error collecting Reddit posts for {symbol}: {e}")
                return []
                
    def _get_user_info(self, author_id: str, users_data: List) -> Dict:
        """Extract user information from Twitter API response"""
        for user in users_data:
            if user.id == author_id:
                return {
                    'username': user.username,
                    'followers_count': user.followers_count,
                    'verified': user.verified,
                    'created_at': user.created_at
                }
        return {}
        
    def _analyze_sentiment(self, text: str) -> tuple[float, str]:
        """Analyze sentiment with crypto-specific enhancements"""
        try:
            # Clean text
            cleaned_text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            cleaned_text = re.sub(r'@\w+|#\w+', '', cleaned_text)
            
            # Basic sentiment analysis
            blob = TextBlob(cleaned_text.lower())
            base_sentiment = blob.sentiment.polarity
            
            # Crypto-specific sentiment keywords
            bullish_terms = ['moon', 'pump', 'hodl', 'diamond hands', 'to the moon', 'bullish', 'rally']
            bearish_terms = ['dump', 'crash', 'bear', 'rekt', 'paper hands', 'bearish', 'sell']
            
            bullish_count = sum(1 for term in bullish_terms if term in cleaned_text.lower())
            bearish_count = sum(1 for term in bearish_terms if term in cleaned_text.lower())
            
            # Adjust sentiment based on crypto terms
            crypto_adjustment = (bullish_count - bearish_count) * 0.2
            final_sentiment = base_sentiment + crypto_adjustment
            final_sentiment = max(-1.0, min(1.0, final_sentiment))
            
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
            
    def _extract_crypto_mentions(self, text: str) -> List[str]:
        """Extract cryptocurrency mentions from text"""
        mentions = set()
        text_lower = text.lower()
        
        # Common crypto symbols and names
        crypto_patterns = {
            'bitcoin': r'\b(bitcoin|btc|₿)\b',
            'ethereum': r'\b(ethereum|eth|ether)\b',
            'dogecoin': r'\b(dogecoin|doge)\b',
            'bonk': r'\bbonk\b',
            'solana': r'\b(solana|sol)\b'
        }
        
        for crypto, pattern in crypto_patterns.items():
            if re.search(pattern, text_lower):
                mentions.add(crypto.upper())
                
        return list(mentions)
        
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        hashtags = re.findall(r'#\w+', text.lower())
        return hashtags
        
    def _calculate_influence_score(self, user_info: Dict, engagement_metrics: Dict) -> float:
        """Calculate influence score for Twitter user"""
        try:
            followers = user_info.get('followers_count', 0)
            total_engagement = sum(engagement_metrics.values())
            
            # Normalize follower count (log scale)
            follower_score = min(1.0, np.log10(max(1, followers)) / 6)  # Max at 1M followers
            
            # Engagement rate
            engagement_rate = total_engagement / max(1, followers) if followers > 0 else 0
            engagement_score = min(1.0, engagement_rate * 100)  # Scale to 0-1
            
            # Verified status bonus
            verified_bonus = 0.2 if user_info.get('verified', False) else 0
            
            # Account age (older = more credible)
            created_at = user_info.get('created_at')
            age_score = 0
            if created_at:
                account_age_days = (datetime.utcnow() - created_at).days
                age_score = min(1.0, account_age_days / 365)  # Max score at 1 year
                
            # Weighted combination
            influence_score = (
                follower_score * self.influence_weights['follower_count'] +
                engagement_score * self.influence_weights['engagement_rate'] +
                age_score * self.influence_weights['account_age'] +
                verified_bonus * self.influence_weights['verified_status']
            )
            
            return min(1.0, influence_score)
            
        except Exception as e:
            logger.warning(f"Error calculating influence score: {e}")
            return 0.1  # Default low influence
            
    def _calculate_reddit_influence(self, submission) -> float:
        """Calculate influence score for Reddit post"""
        try:
            # Score based on upvotes, comments, and upvote ratio
            upvotes = max(0, submission.score)
            comments = submission.num_comments
            upvote_ratio = submission.upvote_ratio
            
            # Normalize scores
            upvote_score = min(1.0, upvotes / 1000)  # Max at 1000 upvotes
            comment_score = min(1.0, comments / 100)  # Max at 100 comments
            
            # Weighted combination
            influence_score = (
                upvote_score * 0.4 +
                comment_score * 0.3 +
                upvote_ratio * 0.3
            )
            
            return influence_score
            
        except Exception as e:
            logger.warning(f"Error calculating Reddit influence: {e}")
            return 0.1
            
    async def get_trending_topics(self, symbols: List[str]) -> Dict[str, Any]:
        """Get trending topics and hashtags for cryptocurrencies"""
        trending_data = {}
        
        for symbol in symbols:
            try:
                # Collect recent posts
                posts = await self._collect_twitter_posts(symbol, hours_back=6, limit=100)
                
                # Analyze hashtags
                all_hashtags = []
                for post in posts:
                    all_hashtags.extend(post.hashtags)
                    
                # Count hashtag frequency
                hashtag_counts = {}
                for hashtag in all_hashtags:
                    hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
                    
                # Get top hashtags
                top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                
                # Calculate sentiment momentum
                recent_sentiments = [post.sentiment_score for post in posts[-20:]]  # Last 20 posts
                sentiment_momentum = sum(recent_sentiments) / len(recent_sentiments) if recent_sentiments else 0
                
                trending_data[symbol] = {
                    'top_hashtags': top_hashtags,
                    'total_posts': len(posts),
                    'sentiment_momentum': sentiment_momentum,
                    'average_influence': sum(post.influence_score for post in posts) / len(posts) if posts else 0,
                    'timestamp': datetime.utcnow()
                }
                
            except Exception as e:
                logger.error(f"Error getting trending topics for {symbol}: {e}")
                
        return trending_data
        
    async def stream_social_mentions(self, symbols: List[str], callback):
        """Stream real-time social media mentions"""
        # This would implement Twitter's streaming API
        # For demonstration, showing the structure
        try:
            # Twitter Stream API v2 would be implemented here
            # Real-time processing of mentions and sentiment
            pass
        except Exception as e:
            logger.error(f"Error in social media streaming: {e}")
