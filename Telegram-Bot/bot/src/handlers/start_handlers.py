from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import CHOOSING
from core.redis_client import RedisClient
from utils.preference_id_format import preference_id_to_name

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        "Hi! This is a robot that will help you find verschenken items in your area.\n"
        "The following commands are available:\n"
        "1. /start : start the bot\n"
        "2. /add : add a filter preference\n"
        "3. /show : show your filter preferences \n"
        "4. /remove : remove a filter preference \n"
        "5. /reset : remove all filter preferences\n",
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Add a filter preference."""
    reply_keyboard = [["Select Category", "Select State"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Please choose a category or state:", reply_markup=markup)
    return CHOOSING

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Remove a filter preference."""
    preferences = RedisClient.get_user_preference(user_id=update.message.chat_id)
    result = preference_id_to_name(preferences, pretify=True)
    reply_markup = ReplyKeyboardMarkup(result, one_time_keyboard=True)
    await update.message.reply_text(
        "Please choose a preference to remove:",
        reply_markup=reply_markup,
        )
    selected = update.message.text
    if selected not in preferences:
        await update.message.reply_text(
            "Please select a valid preference to remove."
        )
        return await remove(update, context)
    else:
        index = result.index(selected)
        RedisClient.update_user_preference(user_id=update.message.chat_id, preference=preferences[index])
        await update.message.reply_text(    
            f"Preference {selected} removed successfully."
        )
    
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Remove all filter preferences."""
    reply_markup = ReplyKeyboardMarkup([["Reset", "Cancel"]])
    await update.message.reply_text(
        "Are you sure you want to remove all filter preferences? Type 'yes' to confirm.",
        reply_markup=reply_markup,
    )
    await confirm_reset(update, context)

async def confirm_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm reset of all filter preferences."""
    if update.message.text == 'Reset':
        RedisClient.remove_all_user_preferences(user_id=update.message.chat_id)
        await update.message.reply_text(
            "All preferences removed successfully."
        )
    else:
        await update.message.reply_text(
            "Reset operation cancelled."
        )
