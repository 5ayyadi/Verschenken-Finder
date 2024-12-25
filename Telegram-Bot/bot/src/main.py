import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from handlers import (
    start,
    choosing,
    category,
    sub_category,
    state,
    city,
    results,
)
from core.config import TOKEN, CHOOSING, CATEGORY, SUB_CATEGORY, STATE, CITY, RESULTS
from core.db import MongoDBClient

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Database connection URI
MONGO_URI = os.getenv("MONGO_URI") or "mongodb://localhost:27017"

async def start_mongo():
    MongoDBClient.initialize(MONGO_URI)
    logging.info("MongoDB server is started")

async def stop_mongo():
    client = MongoDBClient.get_client()
    client.close()
    logging.info("MongoDB server is stopped")

def main() -> None:
    """Run the bot and start MongoDB."""
    
    # Create the Application instance which starts mongodb 
    # before the bot starts and stops it after the bot stops
    application = ApplicationBuilder().token(TOKEN).post_init(start_mongo).post_shutdown(stop_mongo).build()

    # Add conversation handler with 6 states 
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^(Select Category|Select State)$"), choosing),
            ],
            CATEGORY: [
                MessageHandler(filters.Regex("^Back$"), choosing),
                MessageHandler(filters.TEXT & ~filters.COMMAND, category),
            ],
            SUB_CATEGORY: [
                MessageHandler(filters.Regex("^Back$"), category),
                MessageHandler(filters.TEXT & ~filters.COMMAND, sub_category),
            ],
            STATE: [
                MessageHandler(filters.Regex("^Back$"), choosing),
                MessageHandler(filters.TEXT & ~filters.COMMAND, state),
            ],
            CITY: [
                MessageHandler(filters.Regex("^Back$"), state),
                MessageHandler(filters.TEXT & ~filters.COMMAND, city),
            ],
            RESULTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, results),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), results)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()