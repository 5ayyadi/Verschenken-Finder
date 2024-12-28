from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import STATE, CATEGORY, CHOOSING, CITIES_DICT, CATEGORIES_DICT, GENERAL_KEYBOARD


async def choosing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's choice."""
    text = update.message.text
    
    if text == "Select State":
        states_keyboard = [[state] for state in CITIES_DICT.keys()]
        states_markup = ReplyKeyboardMarkup(states_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Please choose a state:", reply_markup=states_markup)
        return STATE
    elif text == "Select Category":
        categories_keyboard = [[category] for category in CATEGORIES_DICT.keys()]
        categories_markup = ReplyKeyboardMarkup(categories_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Please choose a category:", reply_markup=categories_markup)
        return CATEGORY
    else:
        reply_keyboard = [["Select Category", "Select State"]]
        reply_keyboard.extend(GENERAL_KEYBOARD)
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Invalid choice. Please choose again.", reply_markup=markup)
        return CHOOSING
