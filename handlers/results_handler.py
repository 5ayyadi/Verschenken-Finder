from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from core.redis_client import RedisClient
from utils.format_prefs import preference_id_to_name
import logging

logger = logging.getLogger(__name__)


async def results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""

    # Handle callback query (inline button press)
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == "done":
            # Process the results
            zip_code = context.user_data.get("zip_code", "")
            category_id = context.user_data.get("category_id", "")
            sub_category_id = context.user_data.get("sub_category_id", "")
            state_id = context.user_data.get("state_id", "")
            city_id = context.user_data.get("city_id", "")

            logger.info(f"Saving preference for user {update.effective_user.id}: "
                       f"state_id={state_id}, city_id={city_id}, "
                       f"category_id={category_id}, sub_category_id={sub_category_id}")

            preferences = RedisClient.add_user_preference(
                user_id=str(update.effective_user.id),
                category_id=category_id,
                sub_category_id=sub_category_id,
                state_id=state_id,
                city_id=city_id)

            RedisClient.set_chat_ids(
                user_id=str(update.effective_user.id),
                category_id=category_id,
                sub_category_id=sub_category_id,
                state_id=state_id,
                city_id=city_id
            )

            # Filter out empty or invalid preferences
            valid_preferences = [r for r in preference_id_to_name(
                preferences, pretify=True) if r.strip()]

            reply_text = "Your search preferences have been saved successfully! 🎉\n\n"
            reply_text += "Here are your preferences:\n\n"
            reply_text += "\n".join(
                f"📌 {r}" for r in valid_preferences)

            logger.info(f"Successfully saved preference for user {update.effective_user.id}")

            await query.edit_message_text(reply_text)

            # clear the user_data
            context.user_data.clear()

            return ConversationHandler.END
        else:
            await query.edit_message_text("❌ Invalid action. Please try again.")
            return ConversationHandler.END

    # Handle text message (for backwards compatibility)
    else:
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

        RedisClient.set_chat_ids(
            user_id=update.effective_user.id,
            category_id=category_id,
            sub_category_id=sub_category_id,
            state_id=state_id,
            city_id=city_id
        )

        # Filter out empty or invalid preferences
        valid_preferences = [r for r in preference_id_to_name(
            preferences, pretify=True) if r.strip()]

        reply_text = "Your search preferences have been saved successfully! 🎉\n\n"
        reply_text += "Here are your preferences:\n\n"
        reply_text += "\n".join(
            f"📌 {r}" for r in valid_preferences)

        await update.message.reply_text(reply_text)

        # clear the user_data
        context.user_data.clear()

        return ConversationHandler.END
