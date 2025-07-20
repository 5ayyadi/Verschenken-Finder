from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import STATE, RESULTS, SUB_CATEGORY, CATEGORIES_DICT, CITIES_DICT
import logging

logger = logging.getLogger(__name__)


async def sub_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the sub-category choice."""

    # Handle callback query (inline button press)
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data.startswith("sub_all_"):
            category = query.data.replace("sub_all_", "")
            # Don't set specific sub-category for "All Offers"
            logger.info(f"User selected all subcategories for category: {category}")

        elif query.data.startswith("subcategory_"):
            sub_category = query.data.replace("subcategory_", "")
            context.user_data["sub_category"] = sub_category
            context.user_data["sub_category_id"] = CATEGORIES_DICT.get(
                context.user_data["category"]).get("subcategories").get(sub_category)
            logger.info(f"User selected subcategory: {sub_category}")

        elif query.data == "cancel":
            await query.edit_message_text("Operation canceled. /start to start over.")
            context.user_data.clear()
            return RESULTS
        elif query.data == "back_to_category":
            # Import here to avoid circular imports
            from handlers.back_handler import back_to_category
            return await back_to_category(update, context)
        else:
            await query.edit_message_text("❌ Invalid choice. Please try again.")
            return SUB_CATEGORY
    else:
        # Handle text message (for backwards compatibility)
        sub_category = update.message.text

        if sub_category != f"All Offers of {context.user_data['category']} Category":
            context.user_data["sub_category"] = sub_category
            context.user_data["sub_category_id"] = CATEGORIES_DICT.get(
                context.user_data["category"]).get("subcategories").get(sub_category)

    # Check if state is already selected
    if context.user_data.get("state") is None:
        # Create inline keyboard for states
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

        # Add done, back and cancel buttons
        states_buttons.append([
            InlineKeyboardButton("✅ Done", callback_data="done"),
            InlineKeyboardButton("⬅️ Back", callback_data="back_to_category"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ])
        states_markup = InlineKeyboardMarkup(states_buttons)

        if update.callback_query:
            await update.callback_query.edit_message_text("🏛️ Please choose a state:", reply_markup=states_markup)
        else:
            await update.message.reply_text("🏛️ Please choose a state:", reply_markup=states_markup)
        return STATE

    # All options selected - show final action
    keyboard = [[InlineKeyboardButton("✅ Done", callback_data="done")]]
    markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text("✅ You have selected all options. Please choose an action:", reply_markup=markup)
    else:
        await update.message.reply_text("✅ You have selected all options. Please choose an action:", reply_markup=markup)
    return RESULTS
