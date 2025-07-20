from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import SUB_CATEGORY, CATEGORIES_DICT, CATEGORY
import logging

logger = logging.getLogger(__name__)


async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the category choice."""

    # Handle callback query (inline button press)
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data.startswith("category_"):
            category = query.data.replace("category_", "")
            logger.info(f"User selected category: {category}")
        elif query.data == "cancel":
            await query.edit_message_text("Operation canceled. /start to start over.")
            context.user_data.clear()
            return CATEGORY
        elif query.data == "back_to_choosing":
            # Import here to avoid circular imports
            from handlers.back_handler import back_to_choosing
            return await back_to_choosing(update, context)
        else:
            await query.edit_message_text("❌ Invalid choice. Please try again.")
            return CATEGORY
    else:
        # Handle text message (for backwards compatibility)
        category = update.message.text

    # store the category and its id in the user_data
    context.user_data["category"] = category
    context.user_data["category_id"] = CATEGORIES_DICT.get(category).get("id")

    if category in CATEGORIES_DICT:
        sub_categories = list(CATEGORIES_DICT.get(
            category).get("subcategories").keys())

        # Create inline keyboard for sub-categories
        sub_categories_buttons = []

        # Add "All Offers" option
        sub_categories_buttons.append([InlineKeyboardButton(
            f"📦 All Offers of {category}", callback_data=f"sub_all_{category}")])

        # Create rows of 2 buttons each for sub-categories
        for i in range(0, len(sub_categories), 2):
            row = []
            row.append(InlineKeyboardButton(
                sub_categories[i], callback_data=f"subcategory_{sub_categories[i]}"))
            if i + 1 < len(sub_categories):
                row.append(InlineKeyboardButton(
                    sub_categories[i + 1], callback_data=f"subcategory_{sub_categories[i + 1]}"))
            sub_categories_buttons.append(row)

        # Add done, back and cancel buttons
        sub_categories_buttons.append([
            InlineKeyboardButton("✅ Done", callback_data="done"),
            InlineKeyboardButton("⬅️ Back", callback_data="back_to_choosing"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ])

        sub_categories_markup = InlineKeyboardMarkup(sub_categories_buttons)

        if update.callback_query:
            await update.callback_query.edit_message_text(f"✅ You chose {category}\n📂 Please choose a sub-category:", reply_markup=sub_categories_markup)
        else:
            await update.message.reply_text(f"✅ You chose {category}\n📂 Please choose a sub-category:", reply_markup=sub_categories_markup)
        return SUB_CATEGORY
    else:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Invalid choice. Please choose a category:")
        else:
            await update.message.reply_text("❌ Invalid choice. Please choose a category:")
        return CATEGORY
