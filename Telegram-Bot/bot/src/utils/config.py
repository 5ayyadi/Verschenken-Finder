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

# Helper functions
def facts_to_str(user_data: dict[str, str]) -> str:
    """Helper function for formatting the search prefrence."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

def create_user_data() -> dict[str, str]:
    """Create a dictionary to store the user's search prefrence."""
    return {
        "category": None,
        "sub_category": None,
        "category_id": None,
        "state": None,
        "city": None,
        "city_id": None
    }