from pydantic import BaseModel, HttpUrl
from datetime import date
from typing import List

class Location(BaseModel):
    city_id: str = None 
    city_name: str = None 
    state_id: str = None 
    state_name: str = None 
    
class Category(BaseModel):
    category_id: str = None 
    category_name: str = None 
    subcategory_id: str = None 
    subcategory_name: str = None 
    
class Offer(BaseModel):
    _id: str  
    title: str
    description: str
    address: str
    link: HttpUrl
    offer_date: date
    photos: List[HttpUrl]
    location: Location
    category: Category
    telegram_post_id: str = None
