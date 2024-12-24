from fastapi import FastAPI
from app.routers import offer
from app.core.db import MongoDBClient
from contextlib import asynccontextmanager
import os 
import logging

MONGO_URI = os.getenv("MONGO_URI")  or "mongodb://localhost:27017" 

@asynccontextmanager
async def lifespan(app: FastAPI):
    uri = MONGO_URI
    is_mongo_started = MongoDBClient.initialize(uri)
    if is_mongo_started is True:
        logging.info("MongoDB server is started")
    db_client = MongoDBClient.get_client()
    yield
    
    db_client.close()
    MongoDBClient._instance = None

app = FastAPI(lifespan=lifespan)

app.include_router(offer.router, tags=["Offers"])    