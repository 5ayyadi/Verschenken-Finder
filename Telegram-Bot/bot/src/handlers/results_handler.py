from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from core.redis_client import RedisClient
from utils.preference_id_format import preference_id_to_name


async def results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    # user_id -> set of category_id#city_id
    # context.user_data = {
    #    "category": category name
    #    "city": city name
    #    "state": state name
    #    "subcategory": subcategory name
    #   "subcategory_id": subcategory_id
    #  "category_id": category_id
    # }
    
    preferences = RedisClient.get_user_preference(user_id=update.message.chat_id)
    reply_text = "Your search preferences are:"
    reply_text += "\n".join(r for r in preference_id_to_name(preferences, pretify=True))
    await update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardRemove(),
    )
    
    return ConversationHandler.END