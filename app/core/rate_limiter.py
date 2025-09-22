from fastapi import Request, HTTPException
from typing import Optional
import time
from app.db.redis_client import RedisClient


class RateLimiter:
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
    
    def is_rate_limited(
        self, 
        key: str, 
        limit: int, 
        window: int = 60
    ) -> bool:
        """
        Check if a key has exceeded the rate limit
        
        Args:
            key: Unique identifier for rate limiting (e.g., IP address)
            limit: Maximum number of requests allowed
            window: Time window in seconds
        
        Returns:
            True if rate limited, False otherwise
        """
        current_time = int(time.time())
        window_start = current_time - window
        
        # Use sliding window approach
        pipe = self.redis.redis_client.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current entries
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiration
        pipe.expire(key, window)
        
        results = pipe.execute()
        current_count = results[1]
        
        return current_count >= limit
    
    def get_rate_limit_info(self, key: str, window: int = 60) -> dict:
        """Get rate limit information for a key"""
        current_time = int(time.time())
        window_start = current_time - window
        
        # Clean old entries and count current ones
        self.redis.redis_client.zremrangebyscore(key, 0, window_start)
        current_count = self.redis.redis_client.zcard(key)
        
        return {
            "current_requests": current_count,
            "window_seconds": window,
            "reset_time": current_time + window
        }


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers first (for reverse proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection IP
    return request.client.host if request.client else "unknown"


def rate_limit_middleware(
    limit: int = 100,
    window: int = 60,
    redis_client: Optional[RedisClient] = None
):
    """Rate limiting middleware factory"""
    def middleware(request: Request, call_next):
        if redis_client:
            limiter = RateLimiter(redis_client)
            client_ip = get_client_ip(request)
            rate_limit_key = f"rate_limit:{client_ip}"
            
            if limiter.is_rate_limited(rate_limit_key, limit, window):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later.",
                    headers={"Retry-After": str(window)}
                )
        
        response = call_next(request)
        return response
    
    return middleware