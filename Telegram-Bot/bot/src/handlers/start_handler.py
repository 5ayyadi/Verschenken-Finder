from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.config import CHOOSING, create_user_data

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    # create a boilerplate user_data dictionary
    reply_keyboard = [["Select Category"], ["Select State"], ["Done"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    context.user_data.update(create_user_data())
    await update.message.reply_text(
        "Hi! This is a robot that will help you find verschenken items in your area.",
        reply_markup=markup,
    )
    return CHOOSING