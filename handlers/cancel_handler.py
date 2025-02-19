from telegram import ReplyKeyboardRemove, Update
from telegram import Update
from telegram.ext import ContextTypes
from core.constants import CHOOSING


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the cancel action and return to the first state (CHOOSING)."""
    context.user_data.clear()
    await update.message.reply_text(
        "Operation canceled. /start to start over.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return CHOOSING
