"""
Cryptocurrency market data collector supporting CoinGecko, Binance, and other major APIs.
Provides real-time and historical data collection with async support.
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass
import hashlib
import hmac
import json

logger = logging.getLogger(__name__)

@dataclass 
class MarketData:
    """Structure for cryptocurrency market data"""
    symbol: str
    price: float
    volume_24h: float
    market_cap: float
    price_change_24h: float
    timestamp: datetime
    exchange: str
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    
class CryptoDataCollector:
    """
    Comprehensive cryptocurrency data collector supporting multiple exchanges.
    Handles rate limiting, error recovery, and data normalization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.binance_base = "https://api.binance.com/api/v3"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # API keys from environment
        self.binance_api_key = config.get('binance_api_key')
        self.binance_secret_key = config.get('binance_secret_key')
        self.coingecko_api_key = config.get('coingecko_api_key')
        
        # Rate limiting
        self.rate_limits = {
            'coingecko': asyncio.Semaphore(50),  # 50 calls/minute for free tier
            'binance': asyncio.Semaphore(1200),  # 1200 requests/minute
        }
        
        # Data cache for deduplication
        self.data_cache = {}
        self.cache_ttl = 60  # 60 seconds
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    def _create_binance_signature(self, params: Dict[str, Any]) -> str:
        """Create HMAC SHA256 signature for Binance API"""
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return hmac.new(
            self.binance_secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
    async def collect_market_data(self, symbols: List[str]) -> Dict[str, List[MarketData]]:
        """
        Collect comprehensive market data for multiple cryptocurrencies.
        
        Args:
            symbols: List of cryptocurrency symbols (e.g., ['BTC', 'ETH', 'DOGE'])
            
        Returns:
            Dictionary mapping symbols to their market data
        """
        logger.info(f"Collecting market data for {len(symbols)} symbols")
        
        tasks = []
        for symbol in symbols:
            # Collect from multiple sources concurrently
            tasks.extend([
                self._get_coingecko_data(symbol),
                self._get_binance_data(symbol),
                self._get_historical_data(symbol, days=365)
            ])
            
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return self._process_market_results(results, symbols)
        except Exception as e:
            logger.error(f"Error collecting market data: {e}")
            return {}
            
    async def _get_coingecko_data(self, symbol: str) -> Optional[MarketData]:
        """Get current market data from CoinGecko API"""
        async with self.rate_limits['coingecko']:
            try:
                url = f"{self.coingecko_base}/simple/price"
                params = {
                    'ids': symbol.lower(),
                    'vs_currencies': 'usd',
                    'include_market_cap': 'true',
                    'include_24hr_vol': 'true',
                    'include_24hr_change': 'true',
                    'include_last_updated_at': 'true'
                }
                
                if self.coingecko_api_key:
                    params['x_cg_demo_api_key'] = self.coingecko_api_key
                    
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_coingecko_response(data, symbol)
                    else:
                        logger.warning(f"CoinGecko API error {response.status} for {symbol}")
                        
            except Exception as e:
                logger.error(f"Error fetching CoinGecko data for {symbol}: {e}")
                
        return None
        
    async def _get_binance_data(self, symbol: str) -> Optional[MarketData]:
        """Get current market data from Binance API"""
        async with self.rate_limits['binance']:
            try:
                # Convert symbol format (BTC -> BTCUSDT)
                binance_symbol = f"{symbol}USDT"
                url = f"{self.binance_base}/ticker/24hr"
                params = {'symbol': binance_symbol}
                
                headers = {}
                if self.binance_api_key:
                    headers['X-MBX-APIKEY'] = self.binance_api_key
                    
                async with self.session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_binance_response(data, symbol)
                    else:
                        logger.warning(f"Binance API error {response.status} for {symbol}")
                        
            except Exception as e:
                logger.error(f"Error fetching Binance data for {symbol}: {e}")
                
        return None
        
    async def _get_historical_data(self, symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
        """Get historical price data for technical analysis"""
        async with self.rate_limits['coingecko']:
            try:
                url = f"{self.coingecko_base}/coins/{symbol.lower()}/market_chart"
                params = {
                    'vs_currency': 'usd',
                    'days': days,
                    'interval': 'daily' if days > 30 else 'hourly'
                }
                
                if self.coingecko_api_key:
                    params['x_cg_demo_api_key'] = self.coingecko_api_key
                    
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_historical_data(data, symbol)
                        
            except Exception as e:
                logger.error(f"Error fetching historical data for {symbol}: {e}")
                
        return None
        
    def _parse_coingecko_response(self, data: Dict, symbol: str) -> MarketData:
        """Parse CoinGecko API response into MarketData object"""
        symbol_data = data.get(symbol.lower(), {})
        
        return MarketData(
            symbol=symbol.upper(),
            price=symbol_data.get('usd', 0.0),
            volume_24h=symbol_data.get('usd_24h_vol', 0.0),
            market_cap=symbol_data.get('usd_market_cap', 0.0),
            price_change_24h=symbol_data.get('usd_24h_change', 0.0),
            timestamp=datetime.fromtimestamp(symbol_data.get('last_updated_at', time.time())),
            exchange='coingecko'
        )
        
    def _parse_binance_response(self, data: Dict, symbol: str) -> MarketData:
        """Parse Binance API response into MarketData object"""
        return MarketData(
            symbol=symbol.upper(),
            price=float(data.get('lastPrice', 0.0)),
            volume_24h=float(data.get('volume', 0.0)),
            market_cap=0.0,  # Not available in Binance 24hr ticker
            price_change_24h=float(data.get('priceChangePercent', 0.0)),
            high_24h=float(data.get('highPrice', 0.0)),
            low_24h=float(data.get('lowPrice', 0.0)),
            timestamp=datetime.now(),
            exchange='binance'
        )
        
    def _parse_historical_data(self, data: Dict, symbol: str) -> pd.DataFrame:
        """Parse historical data into pandas DataFrame"""
        prices = data.get('prices', [])
        volumes = data.get('total_volumes', [])
        
        df = pd.DataFrame([
            {
                'timestamp': datetime.fromtimestamp(price[0] / 1000),
                'price': price[1],
                'volume': volume[1] if idx < len(volumes) else 0,
                'symbol': symbol.upper()
            }
            for idx, price in enumerate(prices)
        ])
        
        return df.set_index('timestamp')
        
    def _process_market_results(self, results: List, symbols: List[str]) -> Dict[str, List[MarketData]]:
        """Process and organize collected market data"""
        processed_data = {}
        
        for symbol in symbols:
            processed_data[symbol] = []
            
        # Group results by symbol and filter successful responses
        for result in results:
            if isinstance(result, MarketData):
                if result.symbol not in processed_data:
                    processed_data[result.symbol] = []
                processed_data[result.symbol].append(result)
                
        logger.info(f"Successfully collected data for {len(processed_data)} symbols")
        return processed_data
        
    async def stream_real_time_data(self, symbols: List[str], callback):
        """
        Stream real-time price updates via WebSocket.
        
        Args:
            symbols: List of symbols to stream
            callback: Async function to call with new data
        """
        import websockets
        
        try:
            # Binance WebSocket streams
            streams = [f"{symbol.lower()}usdt@ticker" for symbol in symbols]
            stream_url = f"wss://stream.binance.com:9443/ws/{'/'.join(streams)}"
            
            logger.info(f"Connecting to WebSocket for {len(symbols)} symbols")
            
            async with websockets.connect(stream_url) as websocket:
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        processed_data = self._process_websocket_data(data)
                        if processed_data:
                            await callback(processed_data)
                    except Exception as e:
                        logger.error(f"Error processing WebSocket message: {e}")
                        
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            
    def _process_websocket_data(self, data: Dict) -> Optional[MarketData]:
        """Process WebSocket data into MarketData object"""
        try:
            symbol = data.get('s', '').replace('USDT', '')
            
            return MarketData(
                symbol=symbol,
                price=float(data.get('c', 0.0)),
                volume_24h=float(data.get('v', 0.0)),
                market_cap=0.0,
                price_change_24h=float(data.get('P', 0.0)),
                high_24h=float(data.get('h', 0.0)),
                low_24h=float(data.get('l', 0.0)),
                timestamp=datetime.now(),
                exchange='binance_ws'
            )
        except Exception as e:
            logger.error(f"Error processing WebSocket data: {e}")
            return None
            
    async def get_onchain_metrics(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Collect on-chain metrics for cryptocurrencies.
        This is crucial for ML features as on-chain data strongly correlates with price movements.
        """
        metrics = {}
        
        for symbol in symbols:
            try:
                # This would integrate with blockchain explorers or specialized APIs
                # For demonstration, showing the structure
                metrics[symbol] = {
                    'active_addresses': await self._get_active_addresses(symbol),
                    'transaction_volume': await self._get_transaction_volume(symbol),
                    'network_hash_rate': await self._get_network_hash_rate(symbol),
                    'new_addresses': await self._get_new_addresses(symbol),
                    'timestamp': datetime.now()
                }
            except Exception as e:
                logger.error(f"Error collecting on-chain metrics for {symbol}: {e}")
                
        return metrics
        
    async def _get_active_addresses(self, symbol: str) -> int:
        """Get active addresses count - placeholder implementation"""
        # Implementation would connect to blockchain explorers
        return 0
        
    async def _get_transaction_volume(self, symbol: str) -> float:
        """Get transaction volume - placeholder implementation"""
        return 0.0
        
    async def _get_network_hash_rate(self, symbol: str) -> float:
        """Get network hash rate - placeholder implementation"""
        return 0.0
        
    async def _get_new_addresses(self, symbol: str) -> int:
        """Get new addresses count - placeholder implementation"""
        return 0
