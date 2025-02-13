import redis
from config import Config
import logging
from functools import wraps
from typing import Optional, Callable
import time

logger = logging.getLogger(__name__)

class RateLimiter:
    """Класс для управления ограничением частоты запросов"""
    
    def __init__(self):
        self._redis = None
        self._default_limits = {
            'registration': (5, 3600),      # 5 попыток в час
            'connection_request': (3, 3600),# 3 запроса в час
            'message': (10, 3600),          # 10 сообщений в час
            'api_call': (100, 86400)        # 100 вызовов API в сутки
        }
        
    @property
    def redis(self):
        """Ленивая инициализация соединения с Redis"""
        if not self._redis or self._redis.ping() is False:
            try:
                self._redis = redis.Redis.from_url(Config.REDIS_URL)
                self._redis.ping()  # Проверка соединения
            except redis.RedisError as e:
                logger.error(f"Ошибка подключения к Redis: {e}")
                raise
        return self._redis

    def check(
        self, 
        user_id: int, 
        action: str, 
        custom_limit: Optional[tuple] = None
    ) -> bool:
        """
        Проверяет не превышен ли лимит запросов для указанного действия
        
        Args:
            user_id: Идентификатор пользователя
            action: Тип действия (регистрация, запрос связи и т.д.)
            custom_limit: Кастомный лимит (количество, время в секундах)
        
        Returns:
            bool: True если лимит не превышен, False если превышен
        """
        try:
            limit, period = custom_limit or self._default_limits.get(
                action, 
                (5, 3600)  # Дефолтный лимит
            )
            
            key = f"rate_limit:{user_id}:{action}"
            current = self.redis.incr(key)
            
            if current == 1:
                self.redis.expire(key, period)
                return True
                
            return current <= limit
            
        except redis.RedisError as e:
            logger.error(f"RateLimiter error: {e}")
            return True  # Разрешаем запросы при проблемах с Redis

    def get_remaining(self, user_id: int, action: str) -> int:
        """Возвращает оставшееся количество доступных запросов"""
        try:
            limit, _ = self._default_limits.get(action, (5, 3600))
            current = int(self.redis.get(f"rate_limit:{user_id}:{action}") or 0)
            return max(limit - current, 0)
        except redis.RedisError as e:
            logger.error(f"Ошибка получения остатка: {e}")
            return limit  # Возвращаем полный лимит при ошибках

    def reset_limit(self, user_id: int, action: str) -> None:
        """Сбрасывает счетчик запросов для указанного действия"""
        try:
            self.redis.delete(f"rate_limit:{user_id}:{action}")
        except redis.RedisError as e:
            logger.error(f"Ошибка сброса лимита: {e}")

    @staticmethod
    def limit_action(action: str, **limiter_kwargs):
        """
        Декоратор для применения лимитера к обработчикам
        
        Пример использования:
        @RateLimiter.limit_action('registration')
        async def handler(update, context):
            ...
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
                user_id = update.effective_user.id
                limiter = RateLimiter()
                
                if not limiter.check(user_id, action, **limiter_kwargs):
                    await update.message.reply_text(
                        f"🚨 Превышен лимит запросов ({action}). Попробуйте позже."
                    )
                    return
                return await func(update, context)
            return wrapper
        return decorator