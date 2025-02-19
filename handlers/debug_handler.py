from telegram import Update
from telegram.ext import CallbackContext
from workers.offers_tasks import send_offers_task, get_offers
from utils.seed_maker import seed_data


async def debug(update: Update, context: CallbackContext) -> None:
    """
    This is used to debug functions. Some functions need the 
    instance of mongodb which is available in the main.py file.
    so we can't test them from the pytest files.
    """
    await update.message.reply_text("Hello! This command is used to debug")
    # first seed the initial data
    seed_data()
    # then scrape offers based on seed data
    # get_offers()
    # in the end send offers to the users
    # await send_offers_task()
