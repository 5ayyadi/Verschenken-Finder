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
