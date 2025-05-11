import os
import aioredis
from fastapi import Request

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 5))
RATE_WINDOW = int(os.getenv("RATE_WINDOW", 60))  # seconds

class RateLimiter:
    def __init__(self, redis_url=REDIS_URL, rate_limit=RATE_LIMIT, rate_window=RATE_WINDOW):
        self.redis_url = redis_url
        self.rate_limit = rate_limit
        self.rate_window = rate_window
        self._redis = None

    async def get_redis(self):
        if self._redis is None:
            self._redis = await aioredis.from_url(self.redis_url, encoding="utf-8", decode_responses=True)
        return self._redis

    async def is_allowed(self, key: str) -> bool:
        redis = await self.get_redis()
        count = await redis.get(key)
        if count is None:
            await redis.set(key, 1, ex=self.rate_window)
            return True
        elif int(count) < self.rate_limit:
            await redis.incr(key)
            return True
        else:
            return False

def get_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host 