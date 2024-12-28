from pymongo import MongoClient
from threading import Lock
import logging
import os

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