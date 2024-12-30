"""
    This module will be responsible for the worker which will
    run periodically to find the offers from the websites.

"""
from core.celery_client import CeleryClient
from core.mongo_client import MongoDBClient
from core.redis_client import RedisClient
from core.constants import LOGGER
from utils.scraper import find_offers
import os

ADMIN_ID = os.getenv("ADMIN_ID")

app = CeleryClient.app

@app.task(name='get_offers_task')
def get_offers():
    """
        This function will be called periodically by the celery
        worker to find the offers from the websites. Then save it
        into mongodb database.
    """
    LOGGER.info("Getting offers from the websites")
    preferences = RedisClient.get_user_preference(user_id=ADMIN_ID)
    for category_city in preferences:
        category_id, city_id = category_city.split("#")
        offers = find_offers(category_id, city_id)
        MongoDBClient.create_offers(offers)
        
        
@app.task
def send_offers():
    """
        This function will be called periodically by the celery
        worker to send the offers to the users.
    """
    LOGGER.info("Sending offers to the users")
    preferences = RedisClient.get_all_preferences()
    for category_city in preferences:
        category_id = category_city.split("#")[0]
        city_id = category_city.split("#")[1]
        offers = MongoDBClient.get_offers(category_id, city_id)
        