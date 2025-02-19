from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import CITY, GENERAL_KEYBOARD, CITIES_DICT, STATE, CHOOSING, ZIP_DICT

async def zipcode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the zipcode choice."""
    zip_code = update.message.text
    context.user_data["zip_code"] = zip_code
    state = ZIP_DICT.get(zip_code).get("state")
    city = ZIP_DICT.get(zip_code).get("city")
    context.user_data["state"] = state
    context.user_data["state_id"] = CITIES_DICT.get(state).get("id")
    context.user_data["city"] = city
    context.user_data["city_id"] = CITIES_DICT.get(state).get("cities").get(city)
    await update.message.reply_text(
        f"You chose {zip_code}.\nState: {state}\nCity: {city}\nYou can now choose a category or location.",
        )
    return CHOOSING
    
    # ask if user wants to define radius or go by default
    # choices = ReplyKeyboardMarkup([["Define Radius", "Default"]], one_time_keyboard=True)
    # await update.message.reply_text(f"You chose {zip_code}.\nDo you want to define a radius or go by default?", reply_markup=choices)
    # choice = update.message.text
    # if choice == "Define Radius":
    #     return RADIUS
    # else:
    #     return CHOOSING

    # radis_keyboard = [
    #     ["Ganzer Ort"],
    #     ["5 km", "10 km"],
    #     ["20 km", "30 km"],
    #     ["50 km", "100 km"],
    #     ["200 km"]
    # ]

async def state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the state choice."""
    state = update.message.text
    # check if zipcode is entered
    if state.isnumeric():
        return await zipcode(update, context)
    
    # store the state and its id in the user_data
    context.user_data["state"] = state
    context.user_data["state_id"] = CITIES_DICT.get(state).get("id")
    
    cities = list(CITIES_DICT.get(state, {}).get("cities", {}).keys())
    context.user_data["cities"] = cities
    context.user_data["page_number"] = 0

    cities_keyboard = GENERAL_KEYBOARD.copy()
    cities_keyboard.append([f"All Cities of {state} State"])

    first_50_cities = cities[:50]
    cities_keyboard += [first_50_cities[i:i + 2] for i in range(0, len(first_50_cities), 2)]
    cities_keyboard.append(["Next Page"])
    cities_markup = ReplyKeyboardMarkup(cities_keyboard, one_time_keyboard=True)
    
    if state in CITIES_DICT:
        await update.message.reply_text(f"You chose {state}\nPlease choose a city:", reply_markup=cities_markup)
        return CITY
    else:  
        await update.message.reply_text("Invalid choice. Please choose a city:", reply_markup=cities_markup)
        return STATE