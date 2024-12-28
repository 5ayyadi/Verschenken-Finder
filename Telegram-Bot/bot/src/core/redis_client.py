import redis
from redis.client import Redis
from threading import Lock
import os 
import logging

class RedisClient:
    _instance = None
    _lock = Lock()
    _redis_url = None

    @classmethod
    def initialize(cls, redis_url: str) -> bool:
        with cls._lock:
            if cls._instance is None:
                cls._redis_url = redis_url
                cls._instance = redis.from_url(url=redis_url)
        return True

    @classmethod
    def get_client(cls) -> Redis:
        if cls._instance is None:
            raise ValueError("RedisClient has not been initialized. Call `initialize` first.")
        return cls._instance
    
    @classmethod
    def get_db(cls, db: int) -> Redis:
        if cls._redis_url is None:
            raise ValueError("RedisClient has not been initialized. Call `initialize` first.")
        return redis.from_url(url=cls._redis_url, db=db)

    @classmethod
    async def start_redis(cls):
        redis_url = os.getenv("REDIS_URL")
        cls.initialize(redis_url)
        logging.info("Redis connection is started")

    @classmethod
    async def stop_redis(cls):
        client = cls.get_client()
        client.close()
        logging.info("Redis connection is stopped")