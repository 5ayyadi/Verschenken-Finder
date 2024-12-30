from bs4 import BeautifulSoup
from pydantic import ValidationError, HttpUrl
from datetime import date
from models.offer import Offer
from core.constants import BASE_URL
from utils.time_formater import time_to_date
from utils.object_creator import create_location, create_category

def parse_verschenken_offer(offer: BeautifulSoup) -> Offer | None:
    # Scraping Title
    title_tag = offer.find("h2", class_="text-module-begin")
    title = title_tag.text.strip() if title_tag else ""
    
    # Scraping description
    description_tag = offer.find("p", class_="aditem-main--middle--description")
    description = description_tag.text.strip() if description_tag else ""
    
    # Scraping address (Zipcode)
    address_tag = offer.find("div", class_="aditem-main--top--left")
    address = address_tag.text.strip() if address_tag else ""

    # Scraping time of the offer
    time_tag = offer.find("div", class_="aditem-main--top--right")
    time_str = time_tag.text.strip() if time_tag else ""
    try:
        offer_date = time_to_date(time_str)
    except ValueError:
        offer_date = date.today() # Default to current time if parsing fails

    # Scraping photos links and add it as HttpUrl
    photos = []
    photo_url_tag = offer.find("meta", itemprop="contentUrl")
    if photo_url_tag:
        photos.append(photo_url_tag["content"])

    # Scraping the link to the offer
    link_tag = offer.find("a", class_="ellipsis")
    link = BASE_URL + link_tag["href"] if link_tag else ""
    
    # Scraping the offer ID
    id_tag = offer.get("data-adid")
    try:
        _id = str(id_tag)
    except ValueError:
        print(f"Error converting id_tag to string: {id_tag}")
        _id = "default_id"
        
    # Scraping the price
    price_tag = offer.find("p", class_="aditem-main--middle--price-shipping--price")
    price = price_tag.text.strip() if price_tag else ""

    # create location and category objects
    location = create_location()
    category = create_category()
    
    city_id = offer.get("data-city-id", "default_city_id")
    category_id = offer.get("data-category-id", "default_category_id")

    # Check if the offer is "Zu verschenken"
    if price_tag and "Zu verschenken" in price_tag.text:
        # Create a Pydantic model instance
        try:
            offer_data = Offer(
                _id=_id,
                title=title,
                description=description,
                address=address,
                link=HttpUrl(link),
                offer_date=offer_date,
                photos=[HttpUrl(photo) for photo in photos],
                city_id=city_id,
                category_id=category_id
            )
            return offer_data
        except ValidationError as e:
            print(f"Error creating Pydantic model: {e}")
            return None
    return None