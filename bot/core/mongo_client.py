from pymongo import MongoClient
from threading import Lock
import logging
import os
from utils.scraper import find_offers
from bson import ObjectId

class MongoDBClient:
    _instance = None
    _lock = Lock()

    
    @classmethod
    def initialize(cls, mongo_URI: str) -> bool:
        with cls._lock:
            if cls._instance is None:
                cls._instance = MongoClient(mongo_URI)
        return True

    @classmethod
    def get_client(cls) -> MongoClient:
        if cls._instance is None:
            raise ValueError("MongoDBClient has not been initialized. Call `initialize` first.")
        return cls._instance

    @classmethod
    async def start_mongo(cls):
        mongo_URI = os.getenv("MONGO_URI")
        cls.initialize(mongo_URI)
        logging.info("MongoDB server is started")

    @classmethod
    async def stop_mongo(cls):
        client = cls.get_client()
        client.close()
        logging.info("MongoDB server is stopped")
        
        
    @classmethod
    async def create_offers(cls, category_id: str, city_id: str):
        """
        Find and create offers based on the given category and city id.
        """
        offers = find_offers(category_id=category_id, city_id=city_id)
        offer_collection = cls.get_client().get_database("KleineAnzeigen").get_collection("Offer")
        offer_collection.insert_many(offers)
        
        return offers

    @classmethod
    async def read_offers(cls, city_id: str = None, category_id: str = None):
        """
        This function returns filtered offers based on query parameters.
        """
        offer_collection = cls.get_client().get_database("KleineAnzeigen").get_collection("Offer")
        
        filter_criteria = {}
        if city_id:
            filter_criteria["city_id"] = city_id
        if category_id:
            filter_criteria["category_id"] = category_id
        
        query = offer_collection.find(filter_criteria)
        offers = list(query)
        
        return {"result": offers}

    @classmethod
    async def delete_offer(cls, _id: str):
        """
        This function deletes the given offer ID.
        """
        offer_collection = cls.get_client().get_database("KleineAnzeigen").get_collection("Offer")
        
        result = offer_collection.delete_one({"_id": ObjectId(_id)})

        if result.deleted_count == 0:
            raise Exception("Offer not found")

        return {"msg": "Offer deleted successfully"}