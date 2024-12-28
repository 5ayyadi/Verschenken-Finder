from bson import ObjectId
from core.mongo_client import MongoDBClient
from utils.scraper import find_offers

async def create_offers(category_id: str, city_id: str):
    """
    Find and create offers based on the given category and city id.
    """
    offers = find_offers(category_id=category_id, city_id=city_id)
    offer_collection = MongoDBClient.get_client().get_database("KleineAnzeigen").get_collection("Offer")
    offer_collection.insert_many(offers)
    
    return offers

async def read_offers(city_id: str = None, category_id: str = None):
    """
    This function returns filtered offers based on query parameters.
    """
    offer_collection = MongoDBClient.get_client().get_database("KleineAnzeigen").get_collection("Offer")
    
    filter_criteria = {}
    if city_id:
        filter_criteria["city_id"] = city_id
    if category_id:
        filter_criteria["category_id"] = category_id
    
    query = offer_collection.find(filter_criteria)
    offers = list(query)
    
    return {"result": offers}

async def delete_offer(_id: str):
    """
    This function deletes the given offer ID.
    """
    offer_collection = MongoDBClient.get_client().get_database("KleineAnzeigen").get_collection("Offer")
    
    result = offer_collection.delete_one({"_id": ObjectId(_id)})

    if result.deleted_count == 0:
        raise Exception("Offer not found")

    return {"msg": "Offer deleted successfully"}
