import redis
from redis.client import Redis
from threading import Lock
import os 
import logging

#TODO: make constants for the db numbers

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
        
    
    @classmethod
    def add_user_preference(cls, user_id: str, category_id: str, city_id: str) -> set:
        if category_id is None:
            category_id = ""
        if city_id is None:
            city_id = ""
        value = f"{category_id}#{city_id}"
        cls.get_db(0).sadd(name=user_id, value=value)
        return cls.get_db(0).smembers(name=user_id)

    @classmethod
    def get_user_preference(cls, user_id: str) -> set:
        return cls.get_db(0).smembers(name=user_id)
    
    
    # a function to store category and city id as key and 
    # related chat_ids list as value
    @classmethod
    def set_chat_ids(cls, category_id: str, city_id: str, chat_id: str):
        if category_id is None:
            category_id = ""
        if city_id is None:
            city_id = ""
        key = f"{category_id}#{city_id}"
        # get the values set from redis
        existing_value = cls.get_db(1).get(name=key)
        if existing_value is None:
            # create a new value
            existing_value = set(chat_id)
        else:
            existing_value = set(existing_value)
            existing_value.add(chat_id)
        # set the new value
        cls.get_db(1).set(name=key, value=existing_value)
        
    @classmethod
    def get_chat_ids(cls, category_id: str, city_id: str):
        if category_id is None:
            category_id = ""
        if city_id is None:
            city_id = ""
        key = f"{category_id}#{city_id}"
        return set(cls.get_db(1).get(name=key))
    
    
    @classmethod
    def get_all_preferences(cls):
        """
            Returns dictionary of all user preferences
            Keys: category_id#city_id
            Values: set of chat_ids
        """
        db = cls.get_db(1)
        keys = db.keys()
        if not keys:
            return {}
        values = db.mget(keys)
        return dict(zip(keys, values))