from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from threading import Lock
import logging
import os
from models.offer import Offer
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
            raise ValueError(
                "MongoDBClient has not been initialized. Call `initialize` first.")
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
    def create_offers(cls, offers: list[dict] | None = None):
        """
        This function creates the given offers in the database.
        """
        offer_collection = cls.get_client().get_database(
            "KleineAnzeigen").get_collection("Offer")
        try:
            offer_collection.insert_many(offers, ordered=False)
        except BulkWriteError as e:
            logging.error(f"Bulk write error: {e.details}")

        return offers

    @classmethod
    def get_offers(cls, filter_criteria: dict) -> list[Offer]:
        """
        This function returns filtered offers based on query parameters.
        """
        offer_collection = cls.get_client().get_database(
            "KleineAnzeigen").get_collection("Offer")

        query = offer_collection.find(filter_criteria).to_list(length=None)
        offers = [Offer(**offer) for offer in query]

        return offers

    @classmethod
    def delete_offer(cls, id: str):
        """
        This function deletes the given offer ID.
        """
        offer_collection = cls.get_client().get_database(
            "KleineAnzeigen").get_collection("Offer")

        result = offer_collection.delete_one({"_id": ObjectId(id)})

        if result.deleted_count == 0:
            raise Exception("Offer not found")

        return {"msg": "Offer deleted successfully"}
