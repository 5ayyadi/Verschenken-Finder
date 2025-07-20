from core.mongo_client import MongoDBClient
from core.redis_client import RedisClient
from models.offer import Offer
from telegram import Bot
from core.constants import TOKEN, NO_OFFERS_NOTIFICATION_INTERVAL_HOURS
import logging

bot = Bot(token=TOKEN)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)  


# JSON attributes:
# - id
# - title
# - description
# - address
# - link
# - offer_date
# - photos (list)
# - location (dict: city_id, city_name, state_id, state_name)
# - category (dict: category_id, category_name, subcategory_id, subcategory_name)
# - telegram_post_id

async def send_offer_to_user(user_id: str, offer: Offer):
    """
        This function sends a formatted offer message to the user.
    """
    offer_data = offer.model_dump()
    
    message = (
        f"<b>{offer_data['title']}</b>\n\n"
        f"📝 <b>Beschreibung:</b>\n{offer_data['description']}\n\n"
        f"📍 <b>Ort:</b> {offer_data['address']} ({offer_data['location']['state_name']})\n"
        f"🗂️ <b>Kategorie:</b> {offer_data['category']['subcategory_name']} ({offer_data['category']['category_name']})\n"
        f"📅 <b>Datum:</b> {offer_data['offer_date']}\n\n"
        f"🔗 <a href='{offer_data['link']}'>Mehr Details</a>\n"
    )

    if 'photos' in offer_data and offer_data['photos']:
        message += f"🖼️ <a href='{offer_data['photos'][0]}'>Bild ansehen</a>\n"

    await bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")


async def send_no_offers_message(user_id: str, pref_dict: dict):
    """
    Send a friendly message to the user when no offers are found for their preferences.
    """
    from utils.format_prefs import preference_id_to_name
    
    # Convert pref_dict to the format expected by preference_id_to_name
    preference_list = [{
        "state_id": pref_dict.get('state_id'),
        "city_id": pref_dict.get('city_id'),
        "category_id": pref_dict.get('category_id'),
        "sub_category_id": pref_dict.get('sub_category_id')
    }]
    
    # Get formatted preference names
    formatted_prefs = preference_id_to_name(preference_list, pretify=True)
    preference_text = formatted_prefs[0] if formatted_prefs else "Ihre Suchkriterien"
    
    message = (
        "🔍 <b>Keine neuen Angebote gefunden</b>\n\n"
        f"Für Ihre Suchkriterien:\n"
        f"� {preference_text}\n\n"
        "🔔 Wir benachrichtigen Sie, sobald neue \"Zu verschenken\" Angebote verfügbar sind!\n\n"
        "💡 <b>Tipp:</b> Sie können mit /add weitere Suchkriterien hinzufügen oder mit /show Ihre aktuellen Einstellungen anzeigen."
    )
    
    await bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")


async def offer_sender(pref_dict: dict):
    """
        This function will be called by the celery worker to send
        the offers to the users.
    """

    filter_criteria = {
        "location.city_id": pref_dict["city_id"],
        "location.state_id": pref_dict["state_id"],
        "category.category_id": pref_dict["category_id"],
        "category.subcategory_id": pref_dict["sub_category_id"]
    }
    offers = list(reversed(MongoDBClient.get_offers(filter_criteria)))
    logging.info(f"{len(offers)} offers found for {pref_dict}")
    
    # Create preference key for tracking "no offers" notifications
    preference_key = f"{pref_dict['state_id']}_{pref_dict['city_id']}#{pref_dict['category_id']}_{pref_dict['sub_category_id']}"
    
    for user_id in pref_dict.get("users"):
        sent_offers = RedisClient.get_sent_offer_ids(user_id)
        logging.info(f"User {user_id} sent offers : {sent_offers}")
        
        # Count new offers (offers not yet sent to this user)
        new_offers = [offer for offer in offers if offer.id not in sent_offers]
        
        if new_offers:
            # Send new offers to user
            for offer in new_offers:
                logging.info(f"Sending offer with id of {offer.id} to user {user_id}")
                await send_offer_to_user(user_id, offer)
                RedisClient.add_sent_offer_id(user_id, offer.id)
        else:
            # No new offers found - check if we should send "no offers" notification
            if RedisClient.should_send_no_offers_notification(user_id, preference_key, hours_interval=NO_OFFERS_NOTIFICATION_INTERVAL_HOURS):
                logging.info(f"Sending 'no offers' notification to user {user_id} for preference {preference_key}")
                await send_no_offers_message(user_id, pref_dict)
                
                # Record that we sent a "no offers" notification
                import time
                RedisClient.set_no_offers_notification_time(user_id, preference_key, int(time.time()))
            else:
                logging.info(f"Skipping 'no offers' notification for user {user_id} - too soon since last notification")
