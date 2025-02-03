import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from handlers import (
    start,
    add,
    remove,
    confirm_remove,
    reset,
    choosing,
    category,
    sub_category,
    state,
    city,
    results,
)
from core.constants import REMOVE, TOKEN, CHOOSING, CATEGORY, SUB_CATEGORY, STATE, CITY, RESULTS
from core.mongo_client import MongoDBClient
from core.redis_client import RedisClient

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start_services(application):
    """Start db and worker services."""
    await MongoDBClient.start_mongo()
    await RedisClient.start_redis()


async def stop_services(application):
    """Stop db and worker services."""
    await RedisClient.stop_redis()
    await MongoDBClient.stop_mongo()


def main() -> None:
    """Run the bot and start MongoDB."""

    # Create the Application instance which starts services
    # before the bot starts and stops it after the bot stops
    application = ApplicationBuilder().token(TOKEN).post_init(
        start_services).post_shutdown(stop_services).build()

    # Add conversation handler with 6 states
    start_handler = CommandHandler("start", start)
    results_handler = CommandHandler("show", results)
    # remove_handler = CommandHandler("remove", remove)
    remove_handler = ConversationHandler(
        entry_points=[CommandHandler("remove", remove)],
        states={
            REMOVE: [MessageHandler(
                filters.TEXT & ~filters.COMMAND, confirm_remove)]
        },
        fallbacks=[],
    )
    reset_handler = CommandHandler("reset", reset)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add)],
        states={
            CHOOSING: [MessageHandler(filters.Regex("^Select Category|Select Location$"), choosing,),],
            CATEGORY: [
                # MessageHandler(filters.Regex("^Back$"), choosing),
                MessageHandler(filters.Regex("^Done$"), results),
                MessageHandler(filters.TEXT & ~filters.COMMAND, category),
            ],
            SUB_CATEGORY: [
                # MessageHandler(filters.Regex("^Back$"), category),
                MessageHandler(filters.Regex("^Done$"), results),
                MessageHandler(filters.TEXT & ~filters.COMMAND, sub_category),
            ],
            STATE: [
                # MessageHandler(filters.Regex("^Back$"), choosing),
                MessageHandler(filters.Regex("^Done$"), results),
                MessageHandler(filters.TEXT & ~filters.COMMAND, state),

            ],
            CITY: [
                # MessageHandler(filters.Regex("^Back$"), state),
                MessageHandler(filters.Regex("^Done$"), results),
                MessageHandler(filters.TEXT & ~filters.COMMAND, city),
            ],
            RESULTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, results),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), results)],
    )

    application.add_handler(conv_handler)
    application.add_handler(start_handler)
    application.add_handler(results_handler)
    application.add_handler(remove_handler)
    application.add_handler(reset_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
