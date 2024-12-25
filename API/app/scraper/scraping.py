from bs4 import BeautifulSoup
from .constants import BASE_URL
from .utils.parse_data import parse_verschenken_offer
import requests



# def find by category and state_city, if none given find all
def find_offers(category_id: str = None ,city_id: str = None) -> list[dict]:
    """scrap and find offers based on given filters

    Args:
        category (str, optional): category of offer to be filtered. Defaults to None.
        state_city (tuple[str,str], optional): state and city of offer to be filtered. Defaults to None.

    Returns:
        list[dict]: list of offers
    """
    
    # TODO: due to being sorted by price, after a few offers, the priced ones will come
    # so you can stop it - and also go to next page
 
    
    # scrapping url
    URL = f"{BASE_URL}/sortierung:preis/"
    URL += "{category_id}{city_id}"

    webpage = requests.get(URL)
    soup = BeautifulSoup(webpage.text, 'html.parser')
    
    # Find all offers
    offers = soup.find_all("div", class_="aditem-main--middle--price-shipping")

    # Filter for "Zu verschenken"
    results = list()
    for offer in offers:
        price = offer.find("p", class_="aditem-main--middle--price-shipping--price")
        if price and "Zu verschenken" in price.text:
            offer_item = offer.find_parent("article", class_="aditem")
            parsed_offer = parse_verschenken_offer(offer_item)
            offer_dict = parsed_offer.model_dump()
            results.append(offer_dict)
    
    return results