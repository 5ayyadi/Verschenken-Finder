from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import CHOOSING, CATEGORY, SUB_CATEGORY, STATE, CITY, CITIES_DICT, CATEGORIES_DICT
import logging

logger = logging.getLogger(__name__)


async def back_to_choosing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Go back to the main choosing menu."""
    logger.info("User navigating back to choosing menu")
    
    keyboard = [
        [InlineKeyboardButton("📍 Select Location", callback_data="select_location")],
        [InlineKeyboardButton("📂 Select Category", callback_data="select_category")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "Please choose an option:", 
            reply_markup=markup
        )
    else:
        await update.message.reply_text(
            "Please choose an option:", 
            reply_markup=markup
        )
    
    return CHOOSING


async def back_to_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Go back to category selection."""
    logger.info("User navigating back to category selection")
    
    categories_buttons = []
    categories_list = list(CATEGORIES_DICT.keys())

    # Create rows of 2 buttons each
    for i in range(0, len(categories_list), 2):
        row = []
        row.append(InlineKeyboardButton(
            categories_list[i], callback_data=f"category_{categories_list[i]}"))
        if i + 1 < len(categories_list):
            row.append(InlineKeyboardButton(
                categories_list[i + 1], callback_data=f"category_{categories_list[i + 1]}"))
        categories_buttons.append(row)

    # Add back and cancel buttons
    categories_buttons.append([
        InlineKeyboardButton("⬅️ Back", callback_data="back_to_choosing"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])
    
    categories_markup = InlineKeyboardMarkup(categories_buttons)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            "📂 Please choose a category:", 
            reply_markup=categories_markup
        )
    else:
        await update.message.reply_text(
            "📂 Please choose a category:", 
            reply_markup=categories_markup
        )
    
    return CATEGORY


async def back_to_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Go back to state selection."""
    logger.info("User navigating back to state selection")
    
    # Clear current city selection when going back
    if "city" in context.user_data:
        del context.user_data["city"]
    if "city_id" in context.user_data:
        del context.user_data["city_id"]
    
    states_buttons = []
    states_list = list(CITIES_DICT.keys())

    # Create rows of 2 buttons each
    for i in range(0, len(states_list), 2):
        row = []
        row.append(InlineKeyboardButton(
            states_list[i], callback_data=f"state_{states_list[i]}"))
        if i + 1 < len(states_list):
            row.append(InlineKeyboardButton(
                states_list[i + 1], callback_data=f"state_{states_list[i + 1]}"))
        states_buttons.append(row)

    # Add back and cancel buttons  
    states_buttons.append([
        InlineKeyboardButton("⬅️ Back", callback_data="back_to_choosing"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])
    
    states_markup = InlineKeyboardMarkup(states_buttons)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "🏛️ Please choose a state or enter a zipcode:", 
            reply_markup=states_markup
        )
    else:
        await update.message.reply_text(
            "🏛️ Please choose a state or enter a zipcode:", 
            reply_markup=states_markup
        )
    
    return STATE
