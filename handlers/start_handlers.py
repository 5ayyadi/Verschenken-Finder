import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import CHOOSING, REMOVE
from core.redis_client import RedisClient
from utils.format_prefs import preference_id_to_name
from telegram.ext import ConversationHandler
import logging

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the conversation and ask user for input."""
    await update.message.reply_text(
        "Hi! This is a robot that will help you find verschenken items in your area.\n"
        "The following commands are available:\n"
        "1. /start : start the bot\n"
        "2. /add : add a filter preference\n"
        "3. /show : show your filter preferences \n"
        "4. /manage_prefs : manage your filter preferences \n"
        "5. /reset : remove all filter preferences\n",
    )


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Add a filter preference."""
    logger.info("User started /add command - showing category/location selection")
    
    keyboard = [
        [InlineKeyboardButton("📂 Select Category",
                              callback_data="select_category")],
        [InlineKeyboardButton("📍 Select Location",
                              callback_data="select_location")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose a category or state:", reply_markup=markup)
    
    logger.info("Add command completed - returning CHOOSING state")
    return CHOOSING


async def manage_prefs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show current preferences and allow user to manage them."""
    user_id = str(update.effective_user.id)
    
    try:
        preferences = RedisClient.get_user_preference(user_id)
        
        if not preferences:
            message = "📝 You have no saved preferences.\n\nUse /add to create some preferences."
            keyboard = [[InlineKeyboardButton("❌ Close", callback_data="cancel")]]
        else:
            message = f"📝 Your current preferences ({len(preferences)} total):\n\n"
            
            for i, pref in enumerate(preferences, 1):
                # Format preference display
                location_parts = []
                if pref.get('state_id'):
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
                [InlineKeyboardButton("🗑️ Remove One Preference", callback_data="remove_preference")],
                [InlineKeyboardButton("🗑️ Remove All Preferences", callback_data="remove_all_preferences")],
                [InlineKeyboardButton("❌ Close", callback_data="cancel")]
            ]
        
        markup = InlineKeyboardMarkup(keyboard)
        
        logger.info(f"Displayed {len(preferences) if preferences else 0} preferences for user {user_id}")
        
        await update.message.reply_text(message, reply_markup=markup)
        return CHOOSING
        
    except Exception as e:
        logger.error(f"Error viewing preferences for user {user_id}: {e}")
        
        error_message = "❌ Error loading your preferences. Please try again later."
        await update.message.reply_text(error_message)
        
        return ConversationHandler.END


async def confirm_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the user's choice and remove the preference."""

    # Handle callback query (inline button press)
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data.startswith("remove_single_"):
            # Get index instead of the full preference string
            try:
                index = int(query.data.replace("remove_single_", ""))
                preferences = RedisClient.get_user_preference(user_id=str(query.from_user.id))
                result = preference_id_to_name(preferences, pretify=True)
                
                if 0 <= index < len(result):
                    selected = result[index]
                else:
                    await query.edit_message_text("❌ Invalid preference selection.")
                    return REMOVE
            except (ValueError, IndexError):
                await query.edit_message_text("❌ Invalid preference selection.")
                return REMOVE
        elif query.data == "confirm_remove_all":
            # Remove all preferences
            user_id = str(query.from_user.id)
            preferences = RedisClient.get_user_preference(user_id)
            count = len(preferences) if preferences else 0
            
            RedisClient.remove_all_user_preferences(user_id)
            
            # Clear sent offers tracker
            sent_offers_db = RedisClient.get_db(2)
            sent_offers_db.delete(user_id)
            
            await query.edit_message_text(f"✅ Successfully removed all {count} preferences.")
            logger.info(f"Removed all {count} preferences for user {user_id}")
            return ConversationHandler.END
        elif query.data == "back_to_manage":
            # Go back to manage preferences view
            return await manage_prefs_callback(update, context)
        elif query.data == "cancel_remove":
            await query.edit_message_text("Remove operation cancelled.")
            return ConversationHandler.END
        else:
            await query.edit_message_text("❌ Invalid choice. Please try again.")
            return REMOVE

        chat_id = query.message.chat_id
        preferences = RedisClient.get_user_preference(user_id=str(chat_id))
        result = preference_id_to_name(preferences, pretify=True)

        if selected not in result:
            await query.edit_message_text("❌ Please select a valid preference to remove.")
            return REMOVE

        index = result.index(selected)
        pref_to_remove = preferences[index]
        value = f'''{pref_to_remove["state_id"]}_{pref_to_remove["city_id"]}#{
            pref_to_remove["category_id"]}_{pref_to_remove["sub_category_id"]}'''
        RedisClient.remove_user_preference(
            user_id=str(chat_id), preference=value
        )

        await query.edit_message_text(f"✅ Preference '{selected}' removed successfully.")
        return ConversationHandler.END

    # Handle text message (for backwards compatibility)
    else:
        selected = update.message.text
        preferences = RedisClient.get_user_preference(
            user_id=str(update.message.chat_id)
        )
        result = preference_id_to_name(preferences, pretify=True)

        if selected not in result:
            await update.message.reply_text("Please select a valid preference to remove.")
            return REMOVE

        index = result.index(selected)
        pref_to_remove = preferences[index]
        value = f'''{pref_to_remove["state_id"]}_{pref_to_remove["city_id"]}#{
            pref_to_remove["category_id"]}_{pref_to_remove["sub_category_id"]}'''
        RedisClient.remove_user_preference(
            user_id=str(update.message.chat_id), preference=value
        )

        await update.message.reply_text(f"Preference {selected} removed successfully.")
        return ConversationHandler.END


async def manage_prefs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle callback version of manage_prefs for inline keyboard navigation."""
    user_id = str(update.callback_query.from_user.id)
    query = update.callback_query
    await query.answer()
    
    try:
        preferences = RedisClient.get_user_preference(user_id)
        
        if not preferences:
            message = "📝 You have no saved preferences.\n\nUse /add to create some preferences."
            keyboard = [[InlineKeyboardButton("❌ Close", callback_data="cancel")]]
        else:
            message = f"📝 Your current preferences ({len(preferences)} total):\n\n"
            
            for i, pref in enumerate(preferences, 1):
                # Format preference display
                location_parts = []
                if pref.get('state_id'):
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
                [InlineKeyboardButton("🗑️ Remove One Preference", callback_data="remove_preference")],
                [InlineKeyboardButton("🗑️ Remove All Preferences", callback_data="remove_all_preferences")],
                [InlineKeyboardButton("❌ Close", callback_data="cancel")]
            ]
        
        markup = InlineKeyboardMarkup(keyboard)
        
        logger.info(f"Displayed {len(preferences) if preferences else 0} preferences for user {user_id}")
        
        await query.edit_message_text(message, reply_markup=markup)
        return CHOOSING
        
    except Exception as e:
        logger.error(f"Error viewing preferences for user {user_id}: {e}")
        
        error_message = "❌ Error loading your preferences. Please try again later."
        await query.edit_message_text(error_message)
        
        return ConversationHandler.END


async def confirm_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm reset of all filter preferences."""
    # Handle callback query for reset confirmation
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == "reset_confirm":
            RedisClient.remove_all_user_preferences(
                user_id=query.message.chat_id)
            await query.edit_message_text("✅ All preferences removed successfully.")
            return ConversationHandler.END
        elif query.data == "reset_cancel":
            await query.edit_message_text("❌ Reset operation cancelled.")
            return ConversationHandler.END

    # Handle text message (for backwards compatibility)
    if update.message.text == 'Reset':
        RedisClient.remove_all_user_preferences(user_id=update.message.chat_id)
        await update.message.reply_text(
            "All preferences removed successfully."
        )
    else:
        await update.message.reply_text(
            "Reset operation cancelled."
        )
    return ConversationHandler.END


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Remove all filter preferences."""
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Reset All",
                              callback_data="reset_confirm")],
        [InlineKeyboardButton("❌ Cancel", callback_data="reset_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Are you sure you want to remove all filter preferences?",
        reply_markup=reply_markup,
    )
    return CHOOSING  # Wait for callback


async def remove_single_preference(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show preferences for individual removal."""
    user_id = str(update.callback_query.from_user.id)
    query = update.callback_query
    await query.answer()
    
    preferences = RedisClient.get_user_preference(user_id)
    
    if not preferences:
        await query.edit_message_text("You have no preferences to remove.")
        return ConversationHandler.END

    result = preference_id_to_name(preferences, pretify=True)

    # Create inline keyboard for preferences with better formatting
    buttons = []
    for i, pref in enumerate(result):
        # Create shorter, cleaner button text
        short_text = pref[:50] + "..." if len(pref) > 50 else pref
        buttons.append([InlineKeyboardButton(
            short_text, callback_data=f"remove_single_{i}")])

    # Add cancel button
    buttons.append([InlineKeyboardButton(
        "🔙 Back", callback_data="back_to_manage")])

    reply_markup = InlineKeyboardMarkup(buttons)

    message = "🗑️ Choose a preference to remove:\n\n"
    for i, pref in enumerate(result, 1):
        message += f"{i}. {pref}\n"

    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
    )

    return REMOVE


async def remove_all_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show confirmation for removing all preferences."""
    user_id = str(update.callback_query.from_user.id)
    query = update.callback_query
    await query.answer()
    
    preferences = RedisClient.get_user_preference(user_id)
    
    if not preferences:
        await query.edit_message_text("You have no preferences to remove.")
        return ConversationHandler.END
    
    message = f"⚠️ Are you sure you want to remove all {len(preferences)} preferences?\n\nThis action cannot be undone."
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Remove All", callback_data="confirm_remove_all")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_manage")]
    ]
    
    markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=markup)
    
    return CHOOSING
