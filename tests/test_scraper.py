from utils.scraper import find_offers

def test_find_offers():
    category_ids = ["c82","c228", "c279"]
    city_ids = ["l3930", "l285","l17083"]
    
    for cat in category_ids:
        for city in city_ids:
            res = find_offers(category_id=cat, city_id=city)
            print(res)