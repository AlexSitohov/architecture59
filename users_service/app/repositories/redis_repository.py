# redis_repository.py
from redis.asyncio import ConnectionPool, Redis
import hashlib
import logging

logger = logging.getLogger(__name__)


class RedisRepository:
    def __init__(self, redis_url):
        self.redis_url = redis_url
        print(f"Connecting to Redis with URL: {self.redis_url}")
        try:
            self.redis = Redis(
                connection_pool=ConnectionPool.from_url(self.redis_url),
                encoding="utf-8",
            )
            print("Redis connection created successfully")
        except Exception as e:
            print(f"Error creating Redis connection: {e}")
            raise

    async def ping(self):
        try:
            result = await self.redis.ping()
            print(f"Redis ping result: {result}")
            return result
        except Exception as e:
            print(f"Redis ping error: {e}")
            return False

    async def get(self, key):
        try:
            data = await self.redis.get(key)
            print(f"Redis GET: key={key}, data={'found' if data else 'not found'}")
            if data:
                result = data.decode("utf-8")
                print(
                    f"Decoded data: {result[:100]}{'...' if len(result) > 100 else ''}"
                )
                return result
            return None
        except Exception as e:
            print(f"Error in Redis GET operation: {e}")
            return None

    async def set(self, key, value, ttl=None):
        try:
            encoded_value = value
            if not isinstance(value, bytes):
                encoded_value = value.encode("utf-8")

            print(
                f"Redis SET: key={key}, ttl={ttl}, value_length={len(encoded_value)} bytes"
            )

            if ttl is not None:
                result = await self.redis.setex(key, ttl, encoded_value)
            else:
                result = await self.redis.set(key, encoded_value)

            print(f"Redis SET result: {result}")
            return result
        except Exception as e:
            print(f"Error in Redis SET operation: {e}")
            return False

    async def delete(self, key):
        try:
            print(f"Redis DEL: key={key}")
            result = await self.redis.delete(key)
            print(f"Redis DEL result: {result}")
            return bool(result)
        except Exception as e:
            print(f"Error in Redis DEL operation: {e}")
            return False

    # Новые методы для работы с JWT токенами
    @staticmethod
    def _get_jwt_fingerprint(token: str) -> str:
        """Generate SHA-256 fingerprint for JWT token."""
        return hashlib.sha256(token.encode()).hexdigest()

    async def cache_jwt_token(self, token: str, ttl: int = 60) -> bool:
        """Cache JWT token in Redis."""
        cache_key = f"jwt:{self._get_jwt_fingerprint(token)}"
        return await self.set(key=cache_key, value=token, ttl=ttl)

    async def get_cached_jwt_token(self, token: str) -> str:
        """Get cached JWT token from Redis."""
        cache_key = f"jwt:{self._get_jwt_fingerprint(token)}"
        return await self.get(cache_key)

    async def delete_cached_jwt_token(self, token: str) -> bool:
        """Delete cached JWT token from Redis."""
        cache_key = f"jwt:{self._get_jwt_fingerprint(token)}"
        return await self.delete(cache_key)

    async def blacklist_jwt_token(self, token: str, ttl: int = 300) -> bool:
        """Add JWT token to blacklist in Redis."""
        cache_key = f"black_list_jwt:{self._get_jwt_fingerprint(token)}"
        return await self.set(key=cache_key, value=token, ttl=ttl)

    async def is_jwt_token_blacklisted(self, token: str) -> bool:
        """Check if JWT token is blacklisted."""
        cache_key = f"black_list_jwt:{self._get_jwt_fingerprint(token)}"
        return await self.get(cache_key) is not None
