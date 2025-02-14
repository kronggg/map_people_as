import redis
from config import Config

class RateLimiter:
    def __init__(self):
        self.redis = redis.from_url(Config.REDIS_URL)

    def check(self, user_id: int, action: str) -> bool:
        """Проверка лимитов запросов"""
        key = f"rate_limit:{user_id}:{action}"
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, 3600)  # Лимит на 1 час
        return current <= 5  # Макс. 5 запросов в час