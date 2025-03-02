import os
import json

# Load the bot token from environment variable
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables")

# Load categories.json
with open(os.path.join(os.path.dirname(__file__), "../data/categories.json"), "r", encoding="utf-8") as categories_file:
    CATEGORIES_DICT = json.load(categories_file)
# Load cities.json
with open(os.path.join(os.path.dirname(__file__), "../data/cities.json"), "r", encoding="utf-8") as cities_file:
    CITIES_DICT = json.load(cities_file)
# Load location_id.json
with open(os.path.join(os.path.dirname(__file__), "../data/location_id.json"), "r", encoding="utf-8") as location_id_file:
    LOCATION_ID_DICT = json.load(location_id_file)
# Load category_id.json
with open(os.path.join(os.path.dirname(__file__), "../data/category_id.json"), "r", encoding="utf-8") as category_id_file:
    CATEGORY_ID_DICT = json.load(category_id_file)
with open(os.path.join(os.path.dirname(__file__), "../data/zipcodes.json"), "r", encoding="utf-8") as zip_file:
    ZIP_DICT = json.load(zip_file)

# States of the conversation
CHOOSING, CATEGORY, SUB_CATEGORY, STATE, CITY, RESULTS = range(6)
REMOVE = 6


# General keyboard
GENERAL_KEYBOARD = [
    ["Cancel"]
]

# cut off date for the offers (in days)
CUTOFF_DATE = 90

# Telegram Channel Username
CHANNEL_ID = "@verschenken_finder"

# Base URL for scraping
BASE_URL = "https://www.kleinanzeigen.de"

# API endpoints
CATEGORY_URL = f"{BASE_URL}/s-kategorien.html"
CITY_URL = f"{BASE_URL}/s-katalog-orte.html"

# Redis Database Names
# user -> list of state_city#category_subcategory
USER_PREFERENCES_DB = 0
# state_city#category_subcategory -> list of chat_ids
CHAT_IDS_DB = 1
# user -> list of sent offer_ids
SENT_OFFERS_TRACKER_DB = 2

CELERY_BROKER_DB = 3

# Celery Task Names and Intervals
GET_OFFERS_TASK = "workers.offers_tasks.get_offers"
SEND_OFFERS_TASK = "workers.offers_tasks.send_offers"
GET_OFFERS_INTERVAL = 60   # 5 minutes
SEND_OFFERS_INTERVAL = 65 # 1 hour
