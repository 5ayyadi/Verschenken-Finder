"""
    This module will be responsible for the worker which will
    run periodically to find the offers from the websites.

"""
from core.celery_client import CeleryClient
from core.mongo_client import MongoDBClient
from core.redis_client import RedisClient
from core.constants import LOGGER
from utils.scraper import find_offers
from utils.offer_sender import send_offers
from utils.format_prefs import split_preferences
import os

ADMIN_ID = os.getenv("ADMIN_ID")

app = CeleryClient.app

# @app.task(name='get_offers_task')
def get_offers():
    """
        This function will be called periodically by the celery
        worker to find the offers from the websites. Then save it
        into mongodb database.
    """
    LOGGER.info("Getting offers from the websites")
    preferences = RedisClient.get_user_preference(user_id=ADMIN_ID)
    for pref in preferences:
        category_id = pref.get("sub_category_id") if pref.get("sub_category_id") else pref.get("category_id")
        city_id = pref.get("city_id") if pref.get("city_id") else pref.get("state_id")
        offers = find_offers(category_id, city_id)
        MongoDBClient.create_offers(offers)
    return True
        
        
# @app.task
def send_offers_task():
    """
        This function will be called periodically by the celery
        worker to send the offers to the users.
    """
    LOGGER.info("Sending offers to the users")
    preferences = RedisClient.get_all_preferences()
    for location_category in preferences:
        pref = split_preferences(location_category)
        pref["users"] = preferences[location_category]
        send_offers(pref)
                