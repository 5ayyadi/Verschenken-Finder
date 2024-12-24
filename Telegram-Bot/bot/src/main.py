import logging
from telegram import Update

from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from handlers import(
    start,
    choosing,
    category,
    sub_category,
    state,
    city,
    results,
  )
from utils.config import TOKEN, CHOOSING, CATEGORY, SUB_CATEGORY, STATE, CITY, RESULTS

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main() -> None:
    """Run the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    # Add conversation handler with the states CHOOSING, CATEGORY, SUB_CATEGORY, STATE, CITY, RESULTS
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

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()