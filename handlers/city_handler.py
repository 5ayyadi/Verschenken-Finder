from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.pagination import pagination
from core.constants import RESULTS, CITY, CATEGORIES_DICT, CATEGORY, CITIES_DICT, ZIP_DICT
import logging
import difflib

logger = logging.getLogger(__name__)


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the city choice."""

    # Handle callback query (inline button press)
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == "city_next_page":
            context.user_data["page_number"] += 1
            cities_buttons = create_cities_pagination(
                context.user_data["page_number"], context.user_data["state"])
            cities_markup = InlineKeyboardMarkup(cities_buttons)
            await query.edit_message_text("🏙️ Please choose a city:", reply_markup=cities_markup)
            return CITY

        elif query.data == "city_previous_page":
            context.user_data["page_number"] -= 1
            cities_buttons = create_cities_pagination(
                context.user_data["page_number"], context.user_data["state"])
            cities_markup = InlineKeyboardMarkup(cities_buttons)
            await query.edit_message_text("🏙️ Please choose a city:", reply_markup=cities_markup)
            return CITY

        elif query.data.startswith("city_all_"):
            state = query.data.replace("city_all_", "")
            # Don't set specific city for "All Cities"
            city = f'All Cities of {state} State'
            logger.info(f"User selected all cities for state: {state}")

        elif query.data.startswith("city_"):
            city = query.data.replace("city_", "")
            context.user_data["city"] = city
            context.user_data["city_id"] = CITIES_DICT.get(
                context.user_data["state"]).get("cities").get(city)
            logger.info(f"User selected city: {city}")

        elif query.data == "cancel":
            await query.edit_message_text("Operation canceled. /start to start over.")
            context.user_data.clear()
            return RESULTS
        elif query.data == "back_to_state":
            # Import here to avoid circular imports
            from handlers.back_handler import back_to_state
            return await back_to_state(update, context)
        else:
            await query.edit_message_text("❌ Invalid choice. Please try again.")
            return CITY
    else:
        # Handle text message - could be city search, zipcode, or pagination
        text_input = update.message.text.strip()
        
        if text_input == "Next Page":
            context.user_data["page_number"] += 1
            cities_buttons = create_cities_pagination(
                context.user_data["page_number"], context.user_data["state"])
            cities_markup = InlineKeyboardMarkup(cities_buttons)
            await update.message.reply_text("🏙️ Please choose a city:", reply_markup=cities_markup)
            return CITY
        elif text_input == "Previous Page":
            context.user_data["page_number"] -= 1
            cities_buttons = create_cities_pagination(
                context.user_data["page_number"], context.user_data["state"])
            cities_markup = InlineKeyboardMarkup(cities_buttons)
            await update.message.reply_text("🏙️ Please choose a city:", reply_markup=cities_markup)
            return CITY
        else:
            # Search for city by name or handle zipcode
            return await handle_city_search(update, context, text_input)

    # Check if category is already selected
    if context.user_data.get("category") is None:
        # Create inline keyboard for categories
        categories_buttons = []
        categories_list = list(CATEGORIES_DICT.keys())

        # Create rows of 2 buttons each
        for i in range(0, len(categories_list), 2):
            row = []
            row.append(InlineKeyboardButton(
                categories_list[i], callback_data=f"category_{categories_list[i]}"))
            if i + 1 < len(categories_list):
                row.append(InlineKeyboardButton(
                    categories_list[i + 1], callback_data=f"category_{categories_list[i + 1]}"))
            categories_buttons.append(row)

        # Add done, back and cancel buttons
        categories_buttons.append([
            InlineKeyboardButton("✅ Done", callback_data="done"),
            InlineKeyboardButton("⬅️ Back", callback_data="back_to_state"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ])
        categories_markup = InlineKeyboardMarkup(categories_buttons)

        if update.callback_query:
            await update.callback_query.edit_message_text("📂 Please choose a category:", reply_markup=categories_markup)
        else:
            await update.message.reply_text("📂 Please choose a category:", reply_markup=categories_markup)
        return CATEGORY

    # All options selected - show final action
    keyboard = [[InlineKeyboardButton("✅ Done", callback_data="done")]]
    markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text("✅ You have selected all options. Please choose an action:", reply_markup=markup)
    else:
        await update.message.reply_text("✅ You have selected all options. Please choose an action:", reply_markup=markup)
    return RESULTS


def create_cities_pagination(page_number, state):
    """Create paginated cities buttons."""
    cities = list(CITIES_DICT.get(state, {}).get("cities", {}).keys())
    cities_per_page = 50
    start_idx = page_number * cities_per_page
    end_idx = start_idx + cities_per_page

    cities_buttons = []

    # Add "All Cities" option on first page
    if page_number == 0:
        cities_buttons.append([InlineKeyboardButton(
            f"🏙️ All Cities of {state}", callback_data=f"city_all_{state}")])

    # Add cities for current page
    page_cities = cities[start_idx:end_idx]
    for i in range(0, len(page_cities), 2):
        row = []
        row.append(InlineKeyboardButton(
            page_cities[i], callback_data=f"city_{page_cities[i]}"))
        if i + 1 < len(page_cities):
            row.append(InlineKeyboardButton(
                page_cities[i + 1], callback_data=f"city_{page_cities[i + 1]}"))
        cities_buttons.append(row)

    # Add navigation buttons
    nav_row = []
    if page_number > 0:
        nav_row.append(InlineKeyboardButton(
            "◀️ Previous", callback_data="city_previous_page"))
    if end_idx < len(cities):
        nav_row.append(InlineKeyboardButton(
            "▶️ Next", callback_data="city_next_page"))

    if nav_row:
        cities_buttons.append(nav_row)

    # Add done, back and cancel buttons
    cities_buttons.append([
        InlineKeyboardButton("✅ Done", callback_data="done"),
        InlineKeyboardButton("⬅️ Back", callback_data="back_to_state"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])

    return cities_buttons


async def handle_city_search(update: Update, context: ContextTypes.DEFAULT_TYPE, search_input: str) -> int:
    """Handle city search by name or zipcode."""
    
    # Check if it's a zipcode (5 digits)
    if search_input.isnumeric() and len(search_input) == 5:
        return await handle_zipcode_search(update, context, search_input)
    
    # Search for city by name
    return await handle_city_name_search(update, context, search_input)


async def handle_zipcode_search(update: Update, context: ContextTypes.DEFAULT_TYPE, zipcode: str) -> int:
    """Handle zipcode search."""
    
    if zipcode in ZIP_DICT:
        zip_data = ZIP_DICT[zipcode]
        state = zip_data.get("state")
        city = zip_data.get("city")
        
        # Update context with zipcode data
        context.user_data["zip_code"] = zipcode
        context.user_data["state"] = state
        context.user_data["state_id"] = CITIES_DICT.get(state, {}).get("id")
        context.user_data["city"] = city
        context.user_data["city_id"] = CITIES_DICT.get(state, {}).get("cities", {}).get(city)
        
        logger.info(f"User found city via zipcode {zipcode}: {city}, {state}")
        
        await update.message.reply_text(
            f"✅ Found via zipcode {zipcode}:\n🏙️ {city}, {state}\n\nProceed with this location?"
        )
        
        # Continue to category selection if not already selected
        if context.user_data.get("category") is None:
            return await show_category_selection(update, context)
        else:
            return RESULTS
            
    else:
        await update.message.reply_text(
            f"❌ Zipcode {zipcode} not found. Please try again or use the buttons above."
        )
        return CITY


async def handle_city_name_search(update: Update, context: ContextTypes.DEFAULT_TYPE, city_name: str) -> int:
    """Handle city name search with suggestions."""
    
    current_state = context.user_data.get("state")
    if not current_state or current_state not in CITIES_DICT:
        await update.message.reply_text("❌ Please select a state first.")
        return CITY
    
    # Get cities for current state
    cities = CITIES_DICT[current_state].get("cities", {})
    city_names = list(cities.keys())
    
    # Exact match
    if city_name in city_names:
        context.user_data["city"] = city_name
        context.user_data["city_id"] = cities[city_name]
        
        logger.info(f"User found exact city match: {city_name}")
        
        await update.message.reply_text(f"✅ Found: {city_name}")
        
        # Continue to category selection if not already selected
        if context.user_data.get("category") is None:
            return await show_category_selection(update, context)
        else:
            return RESULTS
    
    # Find similar matches
    matches = difflib.get_close_matches(city_name, city_names, n=5, cutoff=0.6)
    
    if matches:
        # Show suggestions
        suggestion_buttons = []
        for match in matches:
            suggestion_buttons.append([InlineKeyboardButton(
                f"🏙️ {match}", callback_data=f"city_{match}")])
        
        # Add back and cancel buttons
        suggestion_buttons.append([
            InlineKeyboardButton("✅ Done", callback_data="done"),
            InlineKeyboardButton("⬅️ Back", callback_data="back_to_state"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ])
        
        markup = InlineKeyboardMarkup(suggestion_buttons)
        
        await update.message.reply_text(
            f"🔍 Did you mean one of these cities?\n(Searched for: '{city_name}')",
            reply_markup=markup
        )
        
        logger.info(f"User search '{city_name}' returned {len(matches)} suggestions")
        return CITY
    else:
        await update.message.reply_text(
            f"❌ No cities found matching '{city_name}' in {current_state}.\n"
            f"Please try a different spelling or use the buttons above."
        )
        return CITY


async def show_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show category selection inline keyboard."""
    
    categories_buttons = []
    categories_list = list(CATEGORIES_DICT.keys())

    # Create rows of 2 buttons each
    for i in range(0, len(categories_list), 2):
        row = []
        row.append(InlineKeyboardButton(
            categories_list[i], callback_data=f"category_{categories_list[i]}"))
        if i + 1 < len(categories_list):
            row.append(InlineKeyboardButton(
                categories_list[i + 1], callback_data=f"category_{categories_list[i + 1]}"))
        categories_buttons.append(row)

    # Add done, back and cancel buttons
    categories_buttons.append([
        InlineKeyboardButton("✅ Done", callback_data="done"),
        InlineKeyboardButton("⬅️ Back", callback_data="back_to_state"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])
    
    categories_markup = InlineKeyboardMarkup(categories_buttons)

    await update.message.reply_text("📂 Please choose a category:", reply_markup=categories_markup)
    return CATEGORY
