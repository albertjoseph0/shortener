import redis
from typing import Optional
from app.core.config import settings


class RedisClient:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    
    def get(self, key: str) -> Optional[str]:
        return self.redis_client.get(key)
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        return self.redis_client.set(key, value, ex=ex)
    
    def delete(self, key: str) -> bool:
        return bool(self.redis_client.delete(key))
    
    def exists(self, key: str) -> bool:
        return bool(self.redis_client.exists(key))
    
    def increment(self, key: str) -> int:
        return self.redis_client.incr(key)
    
    def expire(self, key: str, seconds: int) -> bool:
        return bool(self.redis_client.expire(key, seconds))


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client