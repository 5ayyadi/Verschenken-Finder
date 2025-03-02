"""
    This module will be responsible for the worker which will
    run periodically to find the offers from the websites.

"""
from core.celery_client import CeleryClient
from core.mongo_client import MongoDBClient
from core.redis_client import RedisClient
from core.constants import (
    GET_OFFERS_TASK,
    SEND_OFFERS_TASK,
)
from utils.scraper import find_offers
from utils.offer_sender import offer_sender
from utils.format_prefs import split_preferences
import logging
import asyncio

app = CeleryClient.app

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

@app.task(name=GET_OFFERS_TASK)
def get_offers():
    """
        This function will be called periodically by the celery
        worker to find the offers from the websites. Then save it
        into mongodb database.
    """
    logging.info("Getting offers from the websites")
    preferences = RedisClient.get_all_preferences()
    logging.info(f"Preferences: {preferences}")
    results = list()
    for pref_str in preferences:
        pref = split_preferences(pref_str)
        category_id = pref.get("sub_category_id") if pref.get(
            "sub_category_id") else pref.get("category_id")
        city_id = pref.get("city_id") if pref.get(
            "city_id") else pref.get("state_id")
        offers = find_offers(category_id, city_id)
        logging.info(f"{len(offers)} offers found for {pref_str}")
        if offers:
            results.append(MongoDBClient.create_offers(offers))
    logging.info(f"Overall {len(results)} offers found and saved to the database")
    
    

@app.task(name=SEND_OFFERS_TASK)
def send_offers():
    """
        This function will be called periodically by the Celery
        worker to send offers to the users.
    """
    logging.info("Sending offers to the users")
    preferences = RedisClient.get_all_preferences()
    logging.info(f"Preferences: {preferences}")
    
    for item in preferences:
        pref = split_preferences(item)
        pref["users"] = RedisClient.get_chat_ids(item)
        logging.info(f"Sending offers to {len(pref['users'])} users for {item}")
        asyncio.run(offer_sender(pref))