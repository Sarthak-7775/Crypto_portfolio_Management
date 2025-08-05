"""
Rate limiting middleware for API protection.
"""

import time
import asyncio
from typing import Dict, Any
from collections import defaultdict, deque

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Max calls per period
        self.period = period  # Period in seconds
        self.clients = defaultdict(deque)  # Store client request timestamps
        
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address or API key)
        client_id = self._get_client_id(request)
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/redoc"]:
            return await call_next(request)
            
        # Check rate limit
        if self._is_rate_limited(client_id):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.calls} requests per {self.period} seconds",
                    "retry_after": self.period
                },
                headers={"Retry-After": str(self.period)}
            )
            
        # Record the request
        self._record_request(client_id)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.period)
        
        return response
        
    def _get_client_id(self, request: Request) -> str:
        """Extract client identifier from request"""
        # Try to get API key from header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
            
        # Fall back to IP address
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
            
        return f"ip:{client_ip}"
        
    def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        now = time.time()
        client_requests = self.clients[client_id]
        
        # Remove old requests outside the time window
        while client_requests and client_requests[0] <= now - self.period:
            client_requests.popleft()
            
        # Check if limit exceeded
        return len(client_requests) >= self.calls
        
    def _record_request(self, client_id: str):
        """Record a new request for the client"""
        now = time.time()
        self.clients[client_id].append(now)
        
    def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client"""
        client_requests = self.clients[client_id]
        return max(0, self.calls - len(client_requests))
