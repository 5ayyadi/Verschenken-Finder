from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from core.redis_client import RedisClient
from core.constants import CHOOSING
import logging

logger = logging.getLogger(__name__)


async def view_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show user's current preferences."""
    user_id = str(update.effective_user.id)
    
    try:
        preferences = RedisClient.get_user_preference(user_id)
        
        if not preferences:
            message = "📝 You have no saved preferences.\n\nUse /add to create some preferences."
        else:
            message = f"📝 Your current preferences ({len(preferences)} total):\n\n"
            
            for i, pref in enumerate(preferences, 1):
                # Format preference display
                location_parts = []
                if pref.get('state_id'):
                    # You'd need to reverse lookup state name from ID
                    location_parts.append(f"State: {pref['state_id']}")
                if pref.get('city_id'):
                    location_parts.append(f"City: {pref['city_id']}")
                
                category_parts = []
                if pref.get('category_id'):
                    category_parts.append(f"Category: {pref['category_id']}")
                if pref.get('sub_category_id'):
                    category_parts.append(f"Subcategory: {pref['sub_category_id']}")
                
                location_str = " → ".join(location_parts) if location_parts else "All locations"
                category_str = " → ".join(category_parts) if category_parts else "All categories"
                
                message += f"{i}. 📍 {location_str}\n   📂 {category_str}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("➕ Add New Preference", callback_data="add_preference")],
            [InlineKeyboardButton("🗑️ Remove Preference", callback_data="remove_preference")],
            [InlineKeyboardButton("❌ Close", callback_data="cancel")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        logger.info(f"Displayed {len(preferences) if preferences else 0} preferences for user {user_id}")
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=markup)
        else:
            await update.message.reply_text(message, reply_markup=markup)
            
        return CHOOSING
        
    except Exception as e:
        logger.error(f"Error viewing preferences for user {user_id}: {e}")
        
        error_message = "❌ Error loading your preferences. Please try again later."
        
        if update.callback_query:
            await update.callback_query.edit_message_text(error_message)
        else:
            await update.message.reply_text(error_message)
            
        return ConversationHandler.END


async def clear_all_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Clear all user preferences after confirmation."""
    user_id = str(update.effective_user.id)
    
    try:
        preferences = RedisClient.get_user_preference(user_id)
        
        if not preferences:
            message = "📝 You have no preferences to clear."
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="view_preferences")]]
        else:
            # Show confirmation
            message = f"⚠️ Are you sure you want to clear all {len(preferences)} preferences?\n\nThis action cannot be undone."
            keyboard = [
                [InlineKeyboardButton("✅ Yes, Clear All", callback_data="confirm_clear_all")],
                [InlineKeyboardButton("❌ Cancel", callback_data="view_preferences")]
            ]
        
        markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=markup)
        else:
            await update.message.reply_text(message, reply_markup=markup)
            
        return CHOOSING
        
    except Exception as e:
        logger.error(f"Error in clear_all_preferences for user {user_id}: {e}")
        return ConversationHandler.END


async def confirm_clear_all_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Actually clear all preferences."""
    user_id = str(update.effective_user.id)
    
    try:
        # Get count before clearing
        preferences = RedisClient.get_user_preference(user_id)
        count = len(preferences) if preferences else 0
        
        # Clear all preferences
        RedisClient.remove_all_user_preferences(user_id)
        
        # Clear sent offers tracker
        sent_offers_db = RedisClient.get_db(2)
        sent_offers_db.delete(user_id)
        
        message = f"✅ Successfully cleared {count} preferences.\n\nUse /add to create new preferences."
        
        logger.info(f"Cleared all {count} preferences for user {user_id}")
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
            
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error clearing all preferences for user {user_id}: {e}")
        
        error_message = "❌ Error clearing preferences. Please try again later."
        
        if update.callback_query:
            await update.callback_query.edit_message_text(error_message)
        else:
            await update.message.reply_text(error_message)
            
        return ConversationHandler.END
