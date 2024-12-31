from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import SUB_CATEGORY, CATEGORIES_DICT, GENERAL_KEYBOARD, CATEGORY

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the category choice."""
    category = update.message.text
    
    # store the category and its id in the user_data
    context.user_data["category"] = category
    context.user_data["sub_category_id"] = CATEGORIES_DICT.get(category).get("id")
    
    sub_categories = list(CATEGORIES_DICT.get(category).get("subcategories").keys())
    sub_categories_keyboard = GENERAL_KEYBOARD.copy()
    sub_categories_keyboard.append([f"All Offers of {category} Category"])
    
    # each row of sub_categories_keyboard has three buttons
    sub_categories_keyboard += [sub_categories[i:i + 2] for i in range(0, len(sub_categories), 2)]
    sub_categories_markup = ReplyKeyboardMarkup(sub_categories_keyboard, one_time_keyboard=True)
    
    if category in CATEGORIES_DICT:
        await update.message.reply_text(
            f"You chose {category}\nPlease choose a sub-category:", reply_markup=sub_categories_markup)
        return SUB_CATEGORY
    else:
        await update.message.reply_text("Invalid choice. Please choose a sub-category:", reply_markup=sub_categories_markup)
        return CATEGORY