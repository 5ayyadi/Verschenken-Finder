from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from utils.helper import facts_to_str
from core.redis_client import RedisClient


async def results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    await update.message.reply_text(
        f"Your search prefrence: {facts_to_str(user_data)}",
        reply_markup=ReplyKeyboardRemove(),
    )
    
    # user_id -> category_id, city_id
    RedisClient.set_user_preference(user_id=update.message.chat_id,category_id=user_data.get("category_id"), city_id=user_data.get("city_id"))
    # category_id, city_id -> chat_id for worker
    RedisClient.set_chat_ids(category_id=user_data.get("category_id"), city_id=user_data.get("city_id"), chat_id=update.message.chat_id)

    user_data.clear()
    return ConversationHandler.END