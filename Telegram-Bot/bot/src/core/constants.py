import os
import json
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

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

# States of the conversation
CHOOSING, CATEGORY, SUB_CATEGORY, STATE, CITY, RESULTS = range(6)

# General keyboard
GENERAL_KEYBOARD = [
    ["Back", "Done"]
]

# Telegram Channel Username
CHANNEL_ID = "@verschenken_finder"

# Base URL for scraping
BASE_URL = "https://www.kleinanzeigen.de"

# API endpoints
CATEGORY_URL = f"{BASE_URL}/s-kategorien.html"
CITY_URL = f"{BASE_URL}/s-katalog-orte.html"


