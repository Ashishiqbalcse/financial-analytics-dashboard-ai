import redis
import json
from typing import Optional, Any
from app.core.config import settings


class RedisClient:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    async def ping(self) -> bool:
        """Check if Redis connection is alive"""
        try:
            return self.redis_client.ping()
        except Exception:
            return False
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            if ttl:
                return self.redis_client.setex(key, ttl, value)
            return self.redis_client.set(key, value)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        try:
            return self.redis_client.delete(key) > 0
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis"""
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a JSON value in Redis"""
        return self.set(key, value, ttl)
    
    def get_json(self, key: str) -> Optional[Any]:
        """Get a JSON value from Redis"""
        return self.get(key)
    
    def close(self):
        """Close the Redis connection"""
        try:
            self.redis_client.close()
        except Exception as e:
            print(f"Redis close error: {e}")


# Global Redis client instance
redis_client = RedisClient()
