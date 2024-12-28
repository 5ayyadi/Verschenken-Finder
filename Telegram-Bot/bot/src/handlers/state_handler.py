from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import CITY, GENERAL_KEYBOARD, CITIES_DICT, STATE

async def state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the state choice."""
    state = update.message.text
    
    # store the state and its id in the user_data
    context.user_data["state"] = state
    context.user_data["city_id"] = CITIES_DICT.get(state).get("id")
    
    cities = list(CITIES_DICT.get(state, []).get("cities", []).keys())
    cities_keyboard = GENERAL_KEYBOARD.copy()
    cities_keyboard.append([f"All Offers of {state} State"])

    cities_keyboard += [cities[i:i + 2] for i in range(0, len(cities), 2)]
    cities_markup = ReplyKeyboardMarkup(cities_keyboard, one_time_keyboard=True)
    
    if state in CITIES_DICT:
        await update.message.reply_text(f"You chose {state}\nPlease choose a city:", reply_markup=cities_markup)
        return CITY
    else:  
        await update.message.reply_text("Invalid choice. Please choose a city:", reply_markup=cities_markup)
        return STATE