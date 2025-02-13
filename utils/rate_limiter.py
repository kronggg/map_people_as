import redis
from config import Config
from contextlib import asynccontextmanager

class RateLimiter:
    def __init__(self):
        self.redis = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            decode_responses=True
        )

    @asynccontextmanager
    async def limit(self, user_id: int, action: str, limit: int, period: int):
        """
        Использование:
        async with rate_limiter.limit(user_id, 'registration', 5, 3600) as allowed:
            if not allowed:
                raise RateLimitExceeded()
        """
        key = f"ratelimit:{user_id}:{action}"
        current = self.redis.incr(key)
        
        if current == 1:
            self.redis.expire(key, period)
        
        yield current <= limit
        
        # Точная настройка счетчика
        if current > limit:
            ttl = self.redis.ttl(key)
            self.redis.set(key, limit + 1, ex=ttl)