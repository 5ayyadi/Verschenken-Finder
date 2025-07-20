from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.constants import RESULTS, PRICE_RANGE


async def price_range(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the price range choice."""

    # Handle text input for custom price
    if update.message and update.message.text:
        try:
            custom_price = int(update.message.text.strip())
            if custom_price < 0:
                await update.message.reply_text("❌ Price cannot be negative. Please enter a valid price (0 for free items):")
                return PRICE_RANGE

            context.user_data["max_price"] = custom_price
            if custom_price == 0:
                context.user_data["price_text"] = "Free items only"
            else:
                context.user_data["price_text"] = f"Up to €{custom_price}"

            # Go directly to results
            keyboard = [[InlineKeyboardButton("✅ Done", callback_data="done")]]
            markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"✅ Price range set: {context.user_data['price_text']}\n\nReady to search!",
                reply_markup=markup
            )
            return RESULTS

        except ValueError:
            await update.message.reply_text("❌ Please enter a valid number (0 for free items):")
            return PRICE_RANGE

    # Handle callback query (button press)
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == "price_free":
            context.user_data["max_price"] = 0
            context.user_data["price_text"] = "Free items only"
        elif query.data == "price_20":
            context.user_data["max_price"] = 20
            context.user_data["price_text"] = "Up to €20"
        elif query.data == "price_50":
            context.user_data["max_price"] = 50
            context.user_data["price_text"] = "Up to €50"
        elif query.data == "price_100":
            context.user_data["max_price"] = 100
            context.user_data["price_text"] = "Up to €100"
        elif query.data == "price_custom":
            await query.edit_message_text("✏️ Please enter your maximum price (0 for free items only):")
            return PRICE_RANGE

        # For preset prices, go directly to results
        if query.data != "price_custom":
            keyboard = [[InlineKeyboardButton("✅ Done", callback_data="done")]]
            markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"✅ Price range set: {context.user_data['price_text']}\n\nReady to search!",
                reply_markup=markup
            )
            return RESULTS

    return PRICE_RANGE
