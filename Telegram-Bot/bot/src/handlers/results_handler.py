from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from utils.helper import facts_to_str
from core.redis_client import RedisClient

# set up redis client
redis_client = RedisClient()


async def results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    await update.message.reply_text(
        f"Your search prefrence: {facts_to_str(user_data)}",
        reply_markup=ReplyKeyboardRemove(),
    )
    
    # Concatenate the city and category id for value
    # eachone is none then a empty string is added
    category_id = user_data.get("category_id")
    city_id = user_data.get("city_id")
    if category_id is None:
        category_id = ""
    if city_id is None:
        city_id = ""
    value = f"{category_id}{city_id}"
    RedisClient.get_db(0).set(name=update.message.chat_id, value=value)
    
    

    user_data.clear()
    return ConversationHandler.END