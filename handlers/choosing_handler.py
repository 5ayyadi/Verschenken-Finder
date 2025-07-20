from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import STATE, CATEGORY, CHOOSING, CITIES_DICT, CATEGORIES_DICT, PRICE_RANGE


async def choosing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user's choice."""
    # Check if it's a callback query (inline button press)
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == "select_location":
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

            # Add cancel button
            states_buttons.append(
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
            states_markup = InlineKeyboardMarkup(states_buttons)

            await query.edit_message_text("🏛️ Please choose a state or enter a zipcode:", reply_markup=states_markup)
            return STATE

        elif query.data == "select_category":
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

            # Add cancel button
            categories_buttons.append(
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
            categories_markup = InlineKeyboardMarkup(categories_buttons)

            await query.edit_message_text("📂 Please choose a category:", reply_markup=categories_markup)
            return CATEGORY

    # Handle regular text messages (for backwards compatibility)
    text = update.message.text if update.message else ""

    # Show main menu with inline buttons
    keyboard = [
        [InlineKeyboardButton("📍 Select Location",
                              callback_data="select_location")],
        [InlineKeyboardButton("📂 Select Category",
                              callback_data="select_category")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose an option:", reply_markup=markup)
    return CHOOSING
