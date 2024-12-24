from pydantic import BaseModel

class Offer(BaseModel):
    _id: str  
    title: str
    location: str
    link: str
    time: str
    photos: list[str]
    city_id: str
    category_id: str
