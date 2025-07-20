from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.pagination import pagination
from core.constants import RESULTS, GENERAL_KEYBOARD, CITY, CATEGORIES_DICT, CATEGORY, CITIES_DICT


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the city choice."""
    city = update.message.text

    if city == "Next Page":
        context.user_data["page_number"] += 1
        cities_keyboard = pagination(
            context.user_data["page_number"], context.user_data["state"])
        cities_markup = ReplyKeyboardMarkup(
            cities_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Please choose a city:", reply_markup=cities_markup)
        return CITY
    elif city == "Previous Page":
        context.user_data["page_number"] -= 1
        cities_keyboard = pagination(
            context.user_data["page_number"], context.user_data["state"])
        cities_markup = ReplyKeyboardMarkup(
            cities_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Please choose a city:", reply_markup=cities_markup)
        return CITY

    if city != f'All Cities of {context.user_data.get("state")} State':
        context.user_data["city"] = city
        context.user_data["city_id"] = CITIES_DICT.get(
            context.user_data["state"]).get("cities").get(city)

    if context.user_data.get("category") is None:
        categories_keyboard = [[category]
                               for category in CATEGORIES_DICT.keys()]
        categories_keyboard.extend(GENERAL_KEYBOARD)
        categories_markup = ReplyKeyboardMarkup(
            categories_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Please choose a category:", reply_markup=categories_markup)
        return CATEGORY

    # Updated to keep only the 'Done' button
    final_keyboard = [["Done"]]
    markup = ReplyKeyboardMarkup(final_keyboard, one_time_keyboard=True)
    await update.message.reply_text("You have selected all options. Please choose an action:", reply_markup=markup)
    return RESULTS
