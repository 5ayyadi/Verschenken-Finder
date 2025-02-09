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
    zip_code = context.user_data.get("zip_code", "")
    category_id = context.user_data.get("category_id", "")
    sub_category_id = context.user_data.get("sub_category_id", "")
    state_id = context.user_data.get("state_id", "")
    city_id = context.user_data.get("city_id", "")

    preferences = RedisClient.add_user_preference(
        user_id=update.effective_user.id,
        category_id=category_id,
        sub_category_id=sub_category_id,
        state_id=state_id,
        city_id=city_id)

    reply_text = "Your search preferences have been saved successfully! 🎉\n\n"
    reply_text += "Here are your preferences:\n\n"
    reply_text += "\n".join(
        f"📌 {r}" for r in preference_id_to_name(preferences, pretify=True))

    await update.message.reply_text(
        reply_text,
        reply_markup=ReplyKeyboardRemove(),
    )

    # clear the user_data
    context.user_data.clear()

    return ConversationHandler.END
