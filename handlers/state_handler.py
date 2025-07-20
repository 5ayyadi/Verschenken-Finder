from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import CITY, CITIES_DICT, STATE, CHOOSING, ZIP_DICT
import logging

logger = logging.getLogger(__name__)


async def zipcode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the zipcode choice."""
    zip_code = update.message.text
    context.user_data["zip_code"] = zip_code
    state = ZIP_DICT.get(zip_code).get("state")
    city = ZIP_DICT.get(zip_code).get("city")
    context.user_data["state"] = state
    context.user_data["state_id"] = CITIES_DICT.get(state).get("id")
    context.user_data["city"] = city
    context.user_data["city_id"] = CITIES_DICT.get(
        state).get("cities").get(city)
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

    # Handle callback query (inline button press)
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data.startswith("state_"):
            state = query.data.replace("state_", "")
            logger.info(f"User selected state: {state}")
        elif query.data == "cancel":
            await query.edit_message_text("Operation canceled. /start to start over.")
            context.user_data.clear()
            return CHOOSING
        elif query.data == "back_to_choosing":
            # Import here to avoid circular imports
            from handlers.back_handler import back_to_choosing
            return await back_to_choosing(update, context)
        else:
            await query.edit_message_text("Invalid choice. Please try again.")
            return STATE
    else:
        # Handle text message (zipcode or direct state name)
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

    if state in CITIES_DICT:
        # Create inline keyboard for cities
        cities_buttons = []

        # Add "All Cities" option
        cities_buttons.append([InlineKeyboardButton(
            f"🏙️ All Cities of {state}", callback_data=f"city_all_{state}")])

        # Show first 50 cities (2 buttons per row)
        first_50_cities = cities[:50]
        for i in range(0, len(first_50_cities), 2):
            row = []
            row.append(InlineKeyboardButton(
                first_50_cities[i], callback_data=f"city_{first_50_cities[i]}"))
            if i + 1 < len(first_50_cities):
                row.append(InlineKeyboardButton(
                    first_50_cities[i + 1], callback_data=f"city_{first_50_cities[i + 1]}"))
            cities_buttons.append(row)

        # Add navigation if more than 50 cities
        if len(cities) > 50:
            cities_buttons.append([InlineKeyboardButton(
                "▶️ Next Page", callback_data="city_next_page")])

        # Add done, back and cancel buttons
        cities_buttons.append([
            InlineKeyboardButton("✅ Done", callback_data="done"),
            InlineKeyboardButton("⬅️ Back", callback_data="back_to_choosing"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ])

        cities_markup = InlineKeyboardMarkup(cities_buttons)

        if update.callback_query:
            await update.callback_query.edit_message_text(
                f"✅ You chose {state}\n🏙️ Choose a city below OR type:\n"
                f"• City name (e.g., 'Mainz')\n• 5-digit zipcode (e.g., '55116')", 
                reply_markup=cities_markup
            )
        else:
            await update.message.reply_text(
                f"✅ You chose {state}\n🏙️ Choose a city below OR type:\n"
                f"• City name (e.g., 'Mainz')\n• 5-digit zipcode (e.g., '55116')", 
                reply_markup=cities_markup
            )
        return CITY
    else:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Invalid choice. Please choose a state:")
        else:
            await update.message.reply_text("❌ Invalid choice. Please choose a state:")
        return STATE
