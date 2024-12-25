from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from utils.helper import facts_to_str


async def results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    await update.message.reply_text(
        f"Your search prefrence: {facts_to_str(user_data)}",
        reply_markup=ReplyKeyboardRemove(),
    )
    
    # TODO: add redis to store the user data
    

    user_data.clear()
    return ConversationHandler.END