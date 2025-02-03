from utils.scraper import find_offers

def test_find_offers():
    category_ids = ["c82","c228"]
    city_ids = ["l3930", "l285","l17083"]
    
    for i in range(3):
        find_offers(category_id=category_ids[i], city_id=city_ids[i])