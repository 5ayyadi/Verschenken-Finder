import html
import json
import logging
import traceback
import os

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# This can be your channel's ID or username.
CHANNEL_ID = os.getenv("CHANNEL_ID")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    ).replace("<", "&lt;").replace(">", "&gt;")

    max_message_length = 4096  # Telegram's maximum message length
    if len(message) > max_message_length:
        message = message[:max_message_length - 3] + "..."
    
    await context.bot.send_message(
        chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.HTML
    )


