import redis
from redis.client import Redis
from threading import Lock
import os 
import logging

#TODO: make constants for the db numbers
from core.constants import USER_PREFERENCES_DB, CHAT_IDS_DB

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
    def add_user_preference(
        cls, 
        user_id: str,
        **kwargs):
        value = ""
        # Ensure the order: state_id, city_id, category_id, sub_category_id
        keys_order = ['state_id', 'city_id', 'category_id', 'sub_category_id']
        for key in keys_order:
            if kwargs[key] is not None:
                value += f"{kwargs[key]}"
                if key != keys_order[-1]:
                    value += "#"
        cls.get_db(USER_PREFERENCES_DB).sadd(user_id, value)
        return cls.get_user_preference(user_id)

    @classmethod
    def get_user_preference(cls, user_id: str) -> list[str]:
        result = cls.get_db(USER_PREFERENCES_DB).smembers(user_id)
        return list(r.decode('utf-8') for r in result)
    
    @classmethod
    def update_user_preference(cls, user_id: str, old_preference: str, new_preference: str):
        db = cls.get_db(USER_PREFERENCES_DB)
        if db.sismember(user_id, old_preference):
            db.srem(user_id, old_preference)
            db.sadd(user_id, new_preference)
        else:
            raise ValueError(f"Preference {old_preference} does not exist for user {user_id}")
    @classmethod
    def remove_all_user_preferences(cls, user_id: str):
        cls.get_db(USER_PREFERENCES_DB).delete(user_id)
        cls.add_user_preference(user_id)
    
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
        existing_value = cls.get_db(CHAT_IDS_DB).get(name=key)
        if existing_value is None:
            # create a new value
            existing_value = set(chat_id)
        else:
            existing_value = set(existing_value)
            existing_value.add(chat_id)
        # set the new value
        cls.get_db(CHAT_IDS_DB).set(name=key, value=existing_value)
        
    @classmethod
    def get_chat_ids(cls, category_id: str, city_id: str):
        if category_id is None:
            category_id = ""
        if city_id is None:
            city_id = ""
        key = f"{category_id}#{city_id}"
        return set(cls.get_db(CHAT_IDS_DB  ).get(name=key))
    
    
    @classmethod
    def get_all_preferences(cls):
        """
            Returns dictionary of all user preferences
            Keys: category_id#city_id
            Values: set of chat_ids
        """
        db = cls.get_db(CHAT_IDS_DB)
        keys = db.keys()
        if not keys:
            return {}
        values = db.mget(keys)
        return dict(zip(keys, values))