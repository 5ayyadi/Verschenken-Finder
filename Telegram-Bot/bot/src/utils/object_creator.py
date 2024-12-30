from models.offer import Category, Location 
from core.constants import CATEGORIES_DICT, CITIES_DICT

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
    
def create_category_object(
    category_name: str = None, 
    subcategory_name: str = None) -> Category:
    """Create a dictionary to store the category object."""
    category_id = CATEGORIES_DICT.get(category_name).get("id")
    subcategories = CATEGORIES_DICT.get(category_name).get("subcategories")
    if subcategory_name:
        subcategory_id = subcategories.get(subcategory_name)
    else:
      subcategory_id = None
    return Category(
        category_id=category_id,
        category_name=category_name,
        subcategory_id=subcategory_id,
        subcategory_name=subcategory_name
    )

def create_location_object(
    city_name: str = None, 
    state_name: str = None) -> Location:
    """Create a dictionary to store the location object."""
    state_id = CITIES_DICT.get(state_name).get("id")
    cities = CITIES_DICT.get(state_name).get("cities")
    if city_name:
        city_id = cities.get(city_name)
    else: 
        city_id = None
    
    return Location(
        city_id=city_id,
        city_name=city_name,
        state_id=state_id,
        state_name=state_name
    )