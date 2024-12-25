from pydantic import BaseModel, HttpUrl
from datetime import date
from typing import List

class Offer(BaseModel):
    _id: str  
    title: str
    description: str
    location: str
    link: HttpUrl
    offer_date: date
    photos: List[HttpUrl]
    city_id: str
    category_id: str
    