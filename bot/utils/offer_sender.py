from core.mongo_client import MongoDBClient
from core.redis_client import RedisClient
from models.offer import Offer
from telegram import Bot
from core.constants import TOKEN

bot = Bot(token=TOKEN)

def send_offer_to_user(user_id: str, offer: Offer):
    """
        This function will send the offer to the user.
    """
    message = offer.model_dump_json()
    bot.send_message(chat_id=user_id, text=message)
    

def send_offers(pref_dict: dict):
    """
        This function will be called by the celery worker to send
        the offers to the users.
    """
    
    filter_criteria = {
        "location": {
            "city_id": pref_dict["city_id"],
            "state_id": pref_dict["state_id"]
        },
        "category": {
            "category_id": pref_dict["category_id"],
            "subcategory_id": pref_dict["sub_category_id"]
        }
    }
    offers = MongoDBClient.get_offers(filter_criteria)
    
    for user_id in pref_dict.get("users"):
        sent_offers = RedisClient.get_sent_offer_ids(user_id)
        

        for offer in offers:
            if offer.id not in sent_offers:
                send_offer_to_user(user_id, offer)
                RedisClient.add_sent_offer_id(user_id, offer.id)