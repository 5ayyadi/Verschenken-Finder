# Helper functions
def facts_to_str(user_data: dict[str, str]) -> str:
    """Helper function for formatting the search prefrence."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

def create_user_data() -> dict[str, str]:
    """Create a dictionary to store the user's search prefrence."""
    return {
        "category": None,
        "sub_category": None,
        "category_id": None,
        "state": None,
        "city": None,
        "city_id": None
    }
    
from datetime import date, timedelta

def time_to_date(offer_date: str) -> date:
    """Converts given offer_date to date object.

    Args:
        offer_date (str): received from kleinanzeigen.

    Returns:
        date: date object.
    """
    if "." in offer_date:
        return date.fromisoformat(offer_date)
    elif "Heute" in offer_date:
        return date.today()
    elif "Gestern" in offer_date:
        return date.today() - timedelta(days=1)
    else:
        raise ValueError("Unsupported time format")
