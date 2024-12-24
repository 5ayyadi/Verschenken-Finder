from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.config import RESULTS, GENERAL_KEYBOARD, CATEGORIES_DICT, CATEGORY, CITIES_DICT

async def city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the city choice."""
    city = update.message.text
    
    if city == f"All Offers of {context.user_data['state']} State":
        context.user_data["city"] = context.user_data["state"]
    else:
        context.user_data["city"] = city
        context.user_data["city_id"] = CITIES_DICT.get(context.user_data["state"]).get("cities").get(city)
    
    if context.user_data.get("category") is None:
        categories_keyboard = [[category] for category in CATEGORIES_DICT.keys()]
        categories_keyboard.extend(GENERAL_KEYBOARD)
        categories_markup = ReplyKeyboardMarkup(categories_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Please choose a category:", reply_markup=categories_markup)
        return CATEGORY
    

    markup = ReplyKeyboardMarkup(GENERAL_KEYBOARD, one_time_keyboard=True)
    await update.message.reply_text("You have selected all options. Type 'Done' to see the results Or 'back' to go Back", reply_markup=markup)
    return RESULTS