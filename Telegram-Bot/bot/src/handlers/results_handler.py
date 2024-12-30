from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from core.redis_client import RedisClient


async def results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    # user_id -> set of category_id#city_id
    preferences = RedisClient.add_user_preference(user_id=update.message.chat_id,category_id=user_data.get("category_id"), city_id=user_data.get("city_id"))
   
   
    await update.message.reply_text(
        f"Your search preferences are: {preferences}",
        reply_markup=ReplyKeyboardRemove(),
    )
    
    
    # category_id, city_id -> chat_id for worker
    # RedisClient.set_chat_ids(category_id=user_data.get("category_id"), city_id=user_data.get("city_id"), chat_id=update.message.chat_id)

    user_data.clear()
    return ConversationHandler.END