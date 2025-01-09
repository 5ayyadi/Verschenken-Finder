from bs4 import BeautifulSoup
from core.constants import BASE_URL
from utils.parse_data import parse_verschenken_offer
from utils.object_creator import create_category_object, create_location_object
import requests


def scrap_category_location(soup: BeautifulSoup) -> dict[str, str]:
    # Create a dictionary to store the category and city
    category, subcategory, state, city = None, None, None, None
    
    breadcrumb_tag = soup.find("div", class_="breadcrump")
    if breadcrumb_tag:
        links = breadcrumb_tag.find_all("a", class_="breadcrump-link")
        if len(links) >= 1:
            state_city_tag = breadcrumb_tag.find("h1").find("span", class_="breadcrump-summary")
            if state_city_tag and " in " in state_city_tag.text:
                state_city = state_city_tag.text.split(" in ")[1]
                if " - " in state_city:
                    city, state = state_city.split(" - ")
                else:
                    city, state = None, state_city
            else:
                city, state = None, None

            category_link = breadcrumb_tag.find("a", class_="breadcrump-link", title=False)
            if category_link:
                category = category_link.text
                category_tag = breadcrumb_tag.find("h1").find("span", class_="breadcrump-leaf")
                subcategory = category_tag.text.split(" in ")[0]
            else:
                category_tag = breadcrumb_tag.find("h1").find("span", class_="breadcrump-leaf")
                if category_tag:
                    category = category_tag.text.split(" in ")[0]
                    subcategory = None
                else:
                    category, subcategory = None, None
                    
    return {
        "category": category,
        "subcategory": subcategory,
        "state": state,
        "city": city
    }
      

# def find by category and state_city, if none given find all
def find_offers(category_id: str = None ,city_id: str = None) -> list[dict]:
    """scrap and find offers based on given filters

    Args:
        category (str, optional): category of offer to be filtered. Defaults to None.
        state_city (tuple[str,str], optional): state and city of offer to be filtered. Defaults to None.

    Returns:
        list[dict]: list of offers
    """
 
    results = list()
    page_number = 1
    # keep running until you find a priced offer
    while True:
        # get offers of page_number
        url = f"{BASE_URL}/sortierung:preis/seite:{page_number}/{category_id}{city_id}"
        webpage = requests.get(url)
        soup = BeautifulSoup(webpage.text, 'html.parser')
        offers = soup.find_all("div", class_="aditem-main--middle--price-shipping")
        
        # Extract category, subcategory, state, and city from breadcrumb_tag
        category_location_dict = scrap_category_location(soup)
        category = create_category_object(
            category_name=category_location_dict.get("category"),
            subcategory_name=category_location_dict.get("subcategory"),
        )
        location = create_location_object(
            state_name=category_location_dict.get("state"),
            city_name=category_location_dict.get("city"),
        )
        
        for offer in offers:
            price = offer.find("p", class_="aditem-main--middle--price-shipping--price")
            # if there's no "VB" in price, due to being sorted by price, 
            # that means it's a verschenken offer. VB is the end of verschenken offers
            if price and "VB" in price.text:
                return results
            elif "Zu verschenken" in price.text:
                offer_item = offer.find_parent("article", class_="aditem")
                parsed_offer = parse_verschenken_offer(offer_item)
                parsed_offer.location = location
                parsed_offer.category = category
                offer_dict = parsed_offer.model_dump()
                results.append(offer_dict)
            else:
                return results
            
        # go to next page
        page_number += 1