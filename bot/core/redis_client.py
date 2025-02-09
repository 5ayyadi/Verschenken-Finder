import redis
from redis.client import Redis
from threading import Lock
import os
import logging
import json

# TODO: make constants for the db numbers
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
            raise ValueError(
                "RedisClient has not been initialized. Call `initialize` first.")
        return cls._instance

    @classmethod
    def get_db(cls, db: int) -> Redis:
        if cls._instance is None:
            redis_url = os.getenv("REDIS_URL")
            cls.initialize(redis_url)
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
        state_city = []
        category_subcategory = []
        for key in keys_order:
            if kwargs[key] is not None:
                if key in ['state_id', 'city_id']:
                    state_city.append(kwargs[key])
                else:
                    category_subcategory.append(kwargs[key])

        value = "_".join(state_city) + "#" + "_".join(category_subcategory)
        cls.get_db(USER_PREFERENCES_DB).sadd(user_id, value)
        # add the user to the chat_ids db
        cls.set_chat_ids(state_id="_".join(state_city), category_subcategory_id="_".join(
            category_subcategory), chat_id=user_id,)
        return cls.get_user_preference(user_id)

    @classmethod
    def get_user_preference(cls, user_id: str) -> dict[str, str]:
        result = cls.get_db(USER_PREFERENCES_DB).smembers(user_id)
        preferences = list()
        for item in result:
            state_city, category_subcategory = item.decode().split("#")
            state_city_parts = state_city.split("_")
            category_subcategory_parts = category_subcategory.split("_")
            res_dict = {
                "state_id": state_city_parts[0] if len(state_city_parts) > 0 else None,
                "city_id": state_city_parts[1] if len(state_city_parts) > 1 else None,
                "category_id": category_subcategory_parts[0] if len(category_subcategory_parts) > 0 else None,
                "sub_category_id": category_subcategory_parts[1] if len(category_subcategory_parts) > 1 else None,
            }
            preferences.append(res_dict)
        return preferences

    @classmethod
    def remove_user_preference(cls, user_id: str, preference: str):
        db = cls.get_db(USER_PREFERENCES_DB)
        if db.sismember(user_id, preference):
            state_city, category_subcategory = preference.split("#")
            cls.remove_chat_id(category_subcategory, state_city, user_id)
            db.srem(user_id, preference)

        else:
            raise ValueError(
                f"Preference {preference} does not exist for user {user_id}")

    @classmethod
    def update_user_preference(cls, user_id: str, old_preference: str, new_preference: str):
        db = cls.get_db(USER_PREFERENCES_DB)
        if db.sismember(user_id, old_preference):
            db.srem(user_id, old_preference)
            db.sadd(user_id, new_preference)
            # TODO remove user id from old prefrence and then add it into the new prefrence
        else:
            raise ValueError(
                f"Preference {old_preference} does not exist for user {user_id}")

    @classmethod
    def remove_all_user_preferences(cls, user_id: str):
        cls.get_db(USER_PREFERENCES_DB).delete(user_id)
        cls.add_user_preference(user_id)
        # TODO get user prefrences and remove the user id from the chat ids db

    # a function to store category and city id as key and
    # related chat_ids list as value
    @classmethod
    def set_chat_ids(cls, category_subcategory_id: str, state_id: str, chat_id: str):
        if category_subcategory_id is None:
            category_subcategory_id = ""
        if state_id is None:
            state_id = ""
        key = f"{state_id}#{category_subcategory_id}"
        # get the values set from redis
        existing_value = cls.get_db(CHAT_IDS_DB).get(name=key)
        if existing_value is None:
            # create a new value
            existing_value = {chat_id}
        else:
            existing_value = set(existing_value)
            existing_value.add(chat_id)
        # set the new value
        cls.get_db(CHAT_IDS_DB).set(
            name=key, value=json.dumps(list(existing_value)))

    @classmethod
    def remove_chat_id(cls, category_subcategory_id: str, state_id: str, chat_id: str):
        if category_subcategory_id is None:
            category_subcategory_id = ""
        if state_id is None:
            state_id = ""
        key = f"{state_id}#{category_subcategory_id}"
        existing_value = cls.get_db(CHAT_IDS_DB).get(name=key)
        if existing_value is not None:
            chat_ids = set(existing_value)
            print(chat_id in chat_ids)
            print(chat_ids)
            print(chat_id)
            if chat_id in chat_ids:
                chat_ids.remove(chat_id)
                cls.get_db(CHAT_IDS_DB).set(name=key, value=chat_ids)

    @classmethod
    def get_chat_ids(cls, category_id: str, city_id: str):
        if category_id is None:
            category_id = ""
        if city_id is None:
            city_id = ""
        key = f"{category_id}#{city_id}"
        return set(cls.get_db(CHAT_IDS_DB).get(name=key))

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
