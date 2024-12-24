from pydantic import ValidationError
from ..models import Offer
from .constants import BASE_URL
from bs4 import BeautifulSoup
import json



def parse_verschenken_offer(offer: BeautifulSoup) -> Offer | None:
    
    # Scrapping Title
    title_tag = offer.find("h2", class_="text-module-begin")
    title = title_tag.text.strip() if title_tag else ""
    
    # Scrapping location (Zipcode)
    location_tag = offer.find("div", class_="aditem-main--top--left")
    location = location_tag.text.strip() if location_tag else ""

    # Scrapping time of the offer
    time_tag = offer.find("div", class_="aditem-main--top--right")
    time = time_tag.text.strip() if time_tag else ""

    # Scrapping photos links
    photos = list()
    photo_url_tag = offer.find("meta", itemprop="contentUrl")
    photos.append(photo_url_tag["content"]) if photo_url_tag else None

    # Scrapping the link to the offer
    link_tag = offer.find("a", class_="ellipsis")
    link = BASE_URL + link_tag["href"] if link_tag else ""

    id_tag = offer["data-adid"]
    try:
        _id = str(id_tag)
    except ValueError:
        _id = None
        
    # Adding city and category id    

    # Check if the offer is "Zu verschenken"
    price_tag = offer.find("p", class_="aditem-main--middle--price-shipping--price")
    if price_tag and "Zu verschenken" in price_tag.text:
        # Create a Pydantic model instance
        try:
            
            offer_data = Offer(
                title=title,
                location=location,
                time=time,
                photos=photos,
                link=link,
                _id=_id
            )
            return offer_data
        except ValidationError as e:
            print(f"Error creating Pydantic model: {e}")
            return None
    return None

def get_category_id(category: str) -> str:
    with open("categories.json", "r") as file:
            data = json.load(file)
            return data.get(category)
        
def get_city_id(state:str, city: str) -> str:
    with open("states.json", "r") as state_file:
        data = json.load(state_file)
        state_id = data.get(state)
        if len(city) == 0:
            return state_id
        
    with open("cities.json", "r") as city_file:
        data = json.load(city_file)
        return data.get(state_id).get(city)