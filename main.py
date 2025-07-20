import logging
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from handlers import (
    start,
    add,
    manage_prefs,
    confirm_remove,
    confirm_reset,
    reset,
    remove_single_preference,
    remove_all_preferences,
    manage_prefs_callback,
    choosing,
    category,
    sub_category,
    state,
    city,
    results,
    cancel,
    error_handler,
    debug,
    back_to_choosing,
    back_to_category,
    back_to_state,
    view_preferences,
    clear_all_preferences,
    confirm_clear_all_preferences,
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


async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("add", "Add an item"),
        BotCommand("manage_prefs", "Manage preferences"),
        BotCommand("show", "Show results"),
        BotCommand("preferences", "View and manage preferences"),
        BotCommand("reset", "Reset data"),
    ]
    await application.bot.set_my_commands(commands)


async def start_services(application):
    """Start db and worker services."""
    await MongoDBClient.start_mongo()
    await RedisClient.start_redis()
    await set_bot_commands(application)


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
    preferences_handler = CommandHandler("preferences", view_preferences)
    # manage_prefs_handler = CommandHandler("manage_prefs", manage_prefs)
    manage_prefs_handler = ConversationHandler(
        entry_points=[CommandHandler("manage_prefs", manage_prefs)],
        states={
            CHOOSING: [
                CallbackQueryHandler(remove_single_preference, pattern="^remove_preference$"),
                CallbackQueryHandler(remove_all_preferences, pattern="^remove_all_preferences$"),
                CallbackQueryHandler(confirm_remove, pattern="^confirm_remove_all$"),
                CallbackQueryHandler(manage_prefs_callback, pattern="^back_to_manage$"),
                CallbackQueryHandler(cancel, pattern="^cancel$"),
            ],
            REMOVE: [
                CallbackQueryHandler(confirm_remove, pattern="^remove_single_\\d+$"),
                CallbackQueryHandler(manage_prefs_callback, pattern="^back_to_manage$"),
                CallbackQueryHandler(cancel, pattern="^cancel_remove$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_remove)
            ]
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")],
    )
    reset_handler = ConversationHandler(
        entry_points=[CommandHandler("reset", reset)],
        states={
            CHOOSING: [
                CallbackQueryHandler(confirm_reset, pattern="^reset_confirm$"),
                CallbackQueryHandler(confirm_reset, pattern="^reset_cancel$"),
            ]
        },
        fallbacks=[],
    )
    pref_handler = ConversationHandler(
        allow_reentry=True,
        entry_points=[CommandHandler("add", add)],
        states={
            CHOOSING: [
                CallbackQueryHandler(choosing, pattern="^select_"),
                CallbackQueryHandler(cancel, pattern="^cancel$"),
                MessageHandler(filters.Regex(
                    "^Select Category|Select Location$"), choosing),
            ],
            CATEGORY: [
                CallbackQueryHandler(category, pattern="^category_"),
                CallbackQueryHandler(results, pattern="^done$"),
                CallbackQueryHandler(back_to_choosing, pattern="^back_to_choosing$"),
                CallbackQueryHandler(cancel, pattern="^cancel$"),
                MessageHandler(filters.Regex("^Cancel$"), cancel),
                MessageHandler(filters.Regex("^Done$"), results),
                MessageHandler(filters.TEXT & ~filters.COMMAND, category),
            ],
            SUB_CATEGORY: [
                CallbackQueryHandler(
                    sub_category, pattern="^(sub_all_|subcategory_)"),
                CallbackQueryHandler(results, pattern="^done$"),
                CallbackQueryHandler(back_to_category, pattern="^back_to_category$"),
                CallbackQueryHandler(cancel, pattern="^cancel$"),
                MessageHandler(filters.Regex("^Cancel$"), cancel),
                MessageHandler(filters.Regex("^Done$"), results),
                MessageHandler(filters.TEXT & ~filters.COMMAND, sub_category),
            ],
            STATE: [
                CallbackQueryHandler(state, pattern="^state_"),
                CallbackQueryHandler(results, pattern="^done$"),
                CallbackQueryHandler(back_to_choosing, pattern="^back_to_choosing$"),
                CallbackQueryHandler(cancel, pattern="^cancel$"),
                MessageHandler(filters.Regex("^Cancel$"), cancel),
                MessageHandler(filters.Regex("^Done$"), results),
                MessageHandler(filters.TEXT & ~filters.COMMAND, state),
            ],
            CITY: [
                CallbackQueryHandler(city, pattern="^(city_|cancel|confirm_zipcode)"),
                CallbackQueryHandler(results, pattern="^done$"),
                CallbackQueryHandler(back_to_state, pattern="^back_to_state$"),
                MessageHandler(filters.Regex("^Cancel$"), cancel),
                MessageHandler(filters.Regex("^Done$"), results),
                MessageHandler(filters.TEXT & ~filters.COMMAND, city),
            ],
            RESULTS: [
                CallbackQueryHandler(results, pattern="^done$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, results),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(cancel, pattern="^cancel$"),
            MessageHandler(filters.Regex("^Cancel$"), cancel),
            MessageHandler(filters.Regex("^Done$"), results),
        ],
    )

    application.add_handler(pref_handler)
    application.add_handler(start_handler)
    application.add_handler(results_handler)
    application.add_handler(preferences_handler)
    application.add_handler(manage_prefs_handler)
    application.add_handler(reset_handler)

    application.add_error_handler(error_handler)
    # ==================== DEBUG HANDLER START ====================
    debug_handler = CommandHandler("debug", debug)
    application.add_handler(debug_handler)
    # ==================== Just use it for debug ==================

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
