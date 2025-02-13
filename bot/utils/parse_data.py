from bs4 import BeautifulSoup
from pydantic import ValidationError
from datetime import date
from models.offer import Offer, Location, Category
from core.constants import BASE_URL
from utils.time_formater import time_to_date

def scrape_title(offer: BeautifulSoup) -> str:
    title_tag = offer.find("h2", class_="text-module-begin")
    return title_tag.text.strip() if title_tag else ""

def scrape_description(offer: BeautifulSoup) -> str:
    description_tag = offer.find("p", class_="aditem-main--middle--description")
    return description_tag.text.strip() if description_tag else ""

def scrape_address(offer: BeautifulSoup) -> str:
    address_tag = offer.find("div", class_="aditem-main--top--left")
    return address_tag.text.strip() if address_tag else ""

def scrape_time(offer: BeautifulSoup) -> str:
    time_tag = offer.find("div", class_="aditem-main--top--right")
    time_str = time_tag.text.strip() if time_tag else ""
    try:
        return time_to_date(time_str)
    except ValueError:
        return date.today().isoformat() # Default to current time if parsing fails

def scrape_photos(offer: BeautifulSoup) -> list[str]:
    img_tag = offer.find("img")
    photos = [img_tag.get("src", "")] if img_tag else []
    return photos

def scrape_link(offer: BeautifulSoup) -> str:
    link_tag = offer.find("a", class_="ellipsis")
    if link_tag is None:
        link_tag = offer.find("a")
    return BASE_URL + link_tag["href"] if link_tag else ""

def scrape_id(offer: BeautifulSoup) -> str:
    id_tag = offer.get("data-adid")
    try:
        return str(id_tag)
    except ValueError:
        print(f"Error converting id_tag to string: {id_tag}")
        return "default_id"

def scrape_price(offer: BeautifulSoup) -> str:
    price_tag = offer.find("p", class_="aditem-main--middle--price-shipping--price")
    return price_tag.text.strip() if price_tag else ""

def parse_verschenken_offer(offer: BeautifulSoup) -> Offer | None:
    title = scrape_title(offer)
    description = scrape_description(offer)
    address = scrape_address(offer)
    offer_date = scrape_time(offer)
    photos = scrape_photos(offer)
    link = scrape_link(offer)
    id = scrape_id(offer)
    price = scrape_price(offer)

    location = Location()
    category = Category()


    if "Zu verschenken" in price:
        try:
            offer_data = Offer(
                _id=id,
                title=title,
                description=description,
                address=address,
                link=link,
                offer_date=offer_date,
                photos=photos,
                location=location,
                category=category
            )
            return offer_data
        except ValidationError as e:
            print(f"Error creating Pydantic model: {e}")
            return None
    return None