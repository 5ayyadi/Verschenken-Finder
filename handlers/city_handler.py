from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.pagination import pagination
from core.constants import RESULTS, CITY, CATEGORIES_DICT, CATEGORY, CITIES_DICT


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

        elif query.data.startswith("city_"):
            city = query.data.replace("city_", "")
            context.user_data["city"] = city
            context.user_data["city_id"] = CITIES_DICT.get(
                context.user_data["state"]).get("cities").get(city)

        elif query.data == "cancel":
            await query.edit_message_text("Operation canceled. /start to start over.")
            context.user_data.clear()
            return RESULTS
        else:
            await query.edit_message_text("❌ Invalid choice. Please try again.")
            return CITY
    else:
        # Handle text message (for backwards compatibility)
        city = update.message.text

        if city == "Next Page":
            context.user_data["page_number"] += 1
            cities_buttons = create_cities_pagination(
                context.user_data["page_number"], context.user_data["state"])
            cities_markup = InlineKeyboardMarkup(cities_buttons)
            await update.message.reply_text("🏙️ Please choose a city:", reply_markup=cities_markup)
            return CITY
        elif city == "Previous Page":
            context.user_data["page_number"] -= 1
            cities_buttons = create_cities_pagination(
                context.user_data["page_number"], context.user_data["state"])
            cities_markup = InlineKeyboardMarkup(cities_buttons)
            await update.message.reply_text("🏙️ Please choose a city:", reply_markup=cities_markup)
            return CITY

        if city != f'All Cities of {context.user_data.get("state")} State':
            context.user_data["city"] = city
            context.user_data["city_id"] = CITIES_DICT.get(
                context.user_data["state"]).get("cities").get(city)

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

        # Add cancel button
        categories_buttons.append(
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
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

    # Add cancel button
    cities_buttons.append(
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")])

    return cities_buttons
