from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import STATE, RESULTS, GENERAL_KEYBOARD, CATEGORIES_DICT, CITIES_DICT

async def sub_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the sub-category choice."""
    sub_category = update.message.text
    
    # if the choice is All Offers of the category
    if sub_category == f"All Offers of {context.user_data['category']} Category":
        context.user_data["sub_category"] = context.user_data["category"]
    else:
        context.user_data["sub_category"] = sub_category
        context.user_data["sub_category_id"] = CATEGORIES_DICT.get(context.user_data["category"]).get("subcategories").get(sub_category)
        
    

    
    if context.user_data.get("state") is None:
        states_keyboard = [[state] for state in CITIES_DICT.keys()]
        states_keyboard.extend(GENERAL_KEYBOARD)
        states_markup = ReplyKeyboardMarkup(states_keyboard, one_time_keyboard=True)
        await update.message.reply_text("Please choose a state:", reply_markup=states_markup)
        return STATE
    
    markup = ReplyKeyboardMarkup(GENERAL_KEYBOARD, one_time_keyboard=True)
    await update.message.reply_text("You have selected all options. Type 'Done' to see the results or 'Back' to go back.", reply_markup=markup)
    return RESULTS