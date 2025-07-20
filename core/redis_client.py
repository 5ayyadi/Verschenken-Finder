from redis.client import Redis
from threading import Lock
import os
import logging

from core.constants import (
    USER_PREFERENCES_DB,
    CHAT_IDS_DB,
    SENT_OFFERS_TRACKER_DB,
    NO_OFFERS_NOTIFICATION_DB
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


class RedisClient:
    _instance = None
    _lock = Lock()
    _redis_url = os.getenv('REDIS_URL', 'redis://redis:6379')

    @classmethod
    def initialize(cls, redis_url: str) -> bool:
        with cls._lock:
            if cls._instance is None:
                cls._redis_url = redis_url
                cls._instance = Redis.from_url(
                    url=redis_url, decode_responses=True)
        return True

    @classmethod
    def get_instance(cls) -> Redis:
        if cls._instance is None:
            cls._instance = Redis.from_url(
                url=cls._redis_url, decode_responses=True)
        return cls._instance

    @classmethod
    def get_db(cls, db=0):
        instance = cls.get_instance()
        instance.select(db)
        return instance

    @classmethod
    async def start_redis(cls):
        redis_url = os.getenv("REDIS_URL")
        cls.initialize(redis_url)
        logging.info("Redis connection is started")

    @classmethod
    async def stop_redis(cls):
        client = cls.get_instance()
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
        return cls.get_user_preference(user_id)

    @classmethod
    def get_user_preference(cls, user_id: str) -> dict[str, str]:
        result = cls.get_db(USER_PREFERENCES_DB).smembers(user_id)
        preferences = list()
        for item in result:
            state_city, category_subcategory = item.split("#")
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

            # Clean up "no offers" notification for this specific preference
            cls._cleanup_no_offers_notification_for_preference(
                user_id, preference)

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
        """Remove all preferences for a user and clean up related data."""
        try:
            # Get current preferences before deletion for cleanup
            current_preferences = cls.get_user_preference(user_id)

            # Remove user from all chat_ids mappings
            for pref in current_preferences:
                try:
                    # Construct the key format: state_city#category_subcategory
                    state_city_parts = []
                    if pref.get('state_id'):
                        state_city_parts.append(pref['state_id'])
                    if pref.get('city_id'):
                        state_city_parts.append(pref['city_id'])

                    category_subcategory_parts = []
                    if pref.get('category_id'):
                        category_subcategory_parts.append(pref['category_id'])
                    if pref.get('sub_category_id'):
                        category_subcategory_parts.append(
                            pref['sub_category_id'])

                    # Remove user from chat_ids mappings
                    state_city = "_".join(state_city_parts)
                    category_subcategory = "_".join(category_subcategory_parts)

                    # Call remove_chat_id with correct parameter order
                    cls.remove_chat_id(category_subcategory,
                                       state_city, user_id)

                except Exception as e:
                    logging.error(
                        f"Error removing user {user_id} from chat_ids for preference {pref}: {e}")

            # Delete all user preferences
            cls.get_db(USER_PREFERENCES_DB).delete(user_id)

            # Clean up "no offers" notifications for this user
            cls._cleanup_no_offers_notifications_for_user(user_id)

            logging.info(f"Removed all preferences for user {user_id}")

        except Exception as e:
            logging.error(
                f"Error removing all preferences for user {user_id}: {e}")

    # a function to store category and city id as key and
    # related chat_ids list as value
    @classmethod
    def set_chat_ids(cls, user_id: str, **kwargs):
        # this function will add the stateId_cityId#categoryId_subCategoryId keys and chat_id
        # as values
        value = user_id
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

        key = "_".join(state_city) + "#" + "_".join(category_subcategory)
        # user sadd funciton to complete this funciton
        cls.get_db(CHAT_IDS_DB).sadd(key, value)

    @classmethod
    def remove_chat_id(cls, category_subcategory_id: str, state_id: str, chat_id: str):
        """Remove a chat_id from the chat_ids set for a given preference key."""
        try:
            if category_subcategory_id is None:
                category_subcategory_id = ""
            if state_id is None:
                state_id = ""
            key = f"{state_id}#{category_subcategory_id}"

            # Use srem to remove from set (not get and set)
            removed_count = cls.get_db(CHAT_IDS_DB).srem(key, chat_id)

            if removed_count > 0:
                logging.info(f"Removed chat_id {chat_id} from key {key}")
            else:
                logging.warning(
                    f"Chat_id {chat_id} was not found in key {key}")

        except Exception as e:
            logging.error(
                f"Error removing chat_id {chat_id} from key {key}: {e}")

    @classmethod
    def get_chat_ids(cls, location_category_id: str) -> set[str]:
        return set(cls.get_db(CHAT_IDS_DB).smembers(name=location_category_id))

    @classmethod
    def get_all_preferences(cls) -> set[str]:
        db = cls.get_db(CHAT_IDS_DB)
        keys = db.keys()
        if not keys:
            return {}
        values = db.mget(keys)
        return keys

    # add an offer_id to the list of sent offers for a user
    @classmethod
    def add_sent_offer_id(cls, user_id: str, offer_id: str):
        db = cls.get_db(SENT_OFFERS_TRACKER_DB)
        db.sadd(user_id, offer_id)

    # get all sent offer_ids for a user
    @classmethod
    def get_sent_offer_ids(cls, user_id: str):
        return cls.get_db(SENT_OFFERS_TRACKER_DB).smembers(user_id)

    # remove an offer_id from the list of sent offers for a user
    @classmethod
    def remove_sent_offer_id(cls, user_id: str, offer_id: str):
        db = cls.get_db(SENT_OFFERS_TRACKER_DB)
        if db.sismember(user_id, offer_id):
            db.srem(user_id, offer_id)
        else:
            raise ValueError(
                f"Offer {offer_id} does not exist for user {user_id}")

    # Methods for managing "no offers" notifications
    @classmethod
    def set_no_offers_notification_time(cls, user_id: str, preference_key: str, timestamp: int):
        """Set the timestamp when a 'no offers' notification was sent for a specific user preference."""
        db = cls.get_db(NO_OFFERS_NOTIFICATION_DB)
        key = f"{user_id}:{preference_key}"
        db.set(key, timestamp)

    @classmethod
    def get_no_offers_notification_time(cls, user_id: str, preference_key: str) -> int:
        """Get the timestamp when a 'no offers' notification was last sent for a specific user preference."""
        db = cls.get_db(NO_OFFERS_NOTIFICATION_DB)
        key = f"{user_id}:{preference_key}"
        timestamp = db.get(key)
        return int(timestamp) if timestamp else 0

    @classmethod
    def should_send_no_offers_notification(cls, user_id: str, preference_key: str, hours_interval: int = 24) -> bool:
        """Check if enough time has passed since the last 'no offers' notification for a user preference."""
        import time
        current_time = int(time.time())
        last_notification_time = cls.get_no_offers_notification_time(
            user_id, preference_key)

        # If never sent notification or enough time has passed (default 24 hours)
        time_difference = current_time - last_notification_time
        return time_difference >= (hours_interval * 3600)

    @classmethod
    def _cleanup_no_offers_notifications_for_user(cls, user_id: str):
        """Remove all 'no offers' notification timestamps for a user."""
        try:
            db = cls.get_db(NO_OFFERS_NOTIFICATION_DB)
            # Get all keys that start with user_id:
            pattern = f"{user_id}:*"
            keys = db.keys(pattern)
            if keys:
                db.delete(*keys)
                logging.info(
                    f"Cleaned up {len(keys)} 'no offers' notification entries for user {user_id}")
        except Exception as e:
            logging.error(
                f"Error cleaning up 'no offers' notifications for user {user_id}: {e}")

    @classmethod
    def _cleanup_no_offers_notification_for_preference(cls, user_id: str, preference_key: str):
        """Remove 'no offers' notification timestamp for a specific user preference."""
        try:
            db = cls.get_db(NO_OFFERS_NOTIFICATION_DB)
            key = f"{user_id}:{preference_key}"
            if db.exists(key):
                db.delete(key)
                logging.info(
                    f"Cleaned up 'no offers' notification for user {user_id}, preference {preference_key}")
        except Exception as e:
            logging.error(
                f"Error cleaning up 'no offers' notification for user {user_id}, preference {preference_key}: {e}")
