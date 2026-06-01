from core.config import settings
import time
from dataclasses import dataclass
from typing import Optional

import redis.asyncio as redis


@dataclass(frozen=True)
class CacheConfig:
    ttl_seconds: int
    max_items: int
    lru_zset_key: str = "cities:lru"
    key_prefix: str = "city:"


def cache_config() -> CacheConfig:
    return CacheConfig(
        ttl_seconds=settings.CACHE_TTL,
        max_items=settings.CACHE_MAX_ITEMS,
    )


class CityCountryCodeCache:

    def __init__(self, client: redis.Redis, config: CacheConfig) -> None:
        self._r = client
        self._cfg = config

    def _city_norm(self, city: str) -> str:
        return city.strip().lower()

    def _data_key(self, city_norm: str) -> str:
        return f"{self._cfg.key_prefix}{city_norm}"

    async def get(self, city: str) -> Optional[str]:
        c = self._city_norm(city)
        val = await self._r.get(self._data_key(c))
        if val is None:
            return None

        await self._touch_lru(c)
        return val

    async def set(self, city: str, countrycode: str) -> None:
        c = self._city_norm(city)

        await self._r.set(self._data_key(c), countrycode, ex=self._cfg.ttl_seconds)

        await self._touch_lru(c)
        await self._evict_if_needed()

    async def _touch_lru(self, city_norm: str) -> None:
        now = time.time()
        await self._r.zadd(self._cfg.lru_zset_key, {city_norm: now})

    async def _evict_if_needed(self) -> None:
        count = await self._r.zcard(self._cfg.lru_zset_key)
        if count <= self._cfg.max_items:
            return

        excess = count - self._cfg.max_items

        oldest = await self._r.zrange(self._cfg.lru_zset_key, 0, excess - 1)
        if not oldest:
            return

        pipe = self._r.pipeline()
        for city_norm in oldest:
            pipe.delete(self._data_key(city_norm))
            pipe.zrem(self._cfg.lru_zset_key, city_norm)
        await pipe.execute()
