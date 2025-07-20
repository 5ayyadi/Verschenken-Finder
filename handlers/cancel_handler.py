from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler
from core.constants import CHOOSING
from core.redis_client import RedisClient
import logging

logger = logging.getLogger(__name__)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the cancel action and clear all user data."""
    
    # Get user ID for Redis cleanup
    if update.callback_query:
        user_id = str(update.callback_query.from_user.id)
        query = update.callback_query
        await query.answer()
    else:
        user_id = str(update.message.from_user.id)
    
    # Clear temporary context data
    context.user_data.clear()
    
    # Clear all Redis preferences for this user
    try:
        # Get current preferences first for logging
        preferences = RedisClient.get_user_preference(user_id)
        if preferences:
            logger.info(f"Clearing {len(preferences)} preferences for user {user_id}")
        
        # Clear user preferences from Redis
        RedisClient.remove_all_user_preferences(user_id)
        
        # Clear sent offers tracker
        sent_offers_db = RedisClient.get_db(2)  # SENT_OFFERS_TRACKER_DB
        sent_offers_db.delete(user_id)
        
        logger.info(f"Cancel operation completed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error clearing Redis data for user {user_id}: {e}")
    
    # Send appropriate response
    if update.callback_query:
        await query.edit_message_text(
            "❌ Operation canceled. All preferences cleared.\n\nUse /start to begin again.",
        )
    else:
        await update.message.reply_text(
            "❌ Operation canceled. All preferences cleared.\n\nUse /start to begin again.",
            reply_markup=ReplyKeyboardRemove(),
        )
    
    return ConversationHandler.END
