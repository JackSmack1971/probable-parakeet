import asyncio
import aioredis
from typing import Any, Optional


class AsyncCache:
    """
    A class that represents an asynchronous cache and provides methods for
    setting, getting, and deleting cache items.
    """ 

    def __init__(self, url: str, expire_time: int):
        self.url = url
        self.expire_time = expire_time
        self._connection = None 

    async def _get_connection(self):
        """
        Get the Redis connection. If it does not exist, create it. 

        :return: The Redis connection.
        """
        if self._connection is None or self._connection.closed:
            self._connection = await aioredis.from_url(self.url)
        return self._connection 

    async def set(self, key: str, value: Any) -> None:
        """
        Set a key-value pair in the cache with an expiration time. 

        :param key: The key for the cache item.
        :param value: The value to be stored in the cache.
        """
        redis = await self._get_connection()
        await redis.set(key, value, expire=self.expire_time) 

    async def get(self, key: str) -> Optional[Any]:
        """
        Get the value associated with a key in the cache. 

        :param key: The key for the cache item.
        :return: The value associated with the key or None if the key does not exist.
        """
        redis = await self._get_connection()
        return await redis.get(key) 

    async def delete(self, key: str) -> None:
        """
        Delete a key-value pair from the cache. 

        :param key: The key for the cache item.
        """
        redis = await self._get_connection()
        await redis.delete(key) 

    async def close(self) -> None:
        """
        Close the Redis connection.
        """
        if self._connection is not None and not self._connection.closed:
            self._connection.close()
            await self._connection.wait_closed()
