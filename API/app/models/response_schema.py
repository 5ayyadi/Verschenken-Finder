from pydantic import BaseModel
from .offer import Offer
from typing import Any

class BaseResponse(BaseModel):
    msg: str = "OK"
    status_code: int = 200
    result: Any = None
    
class OfferResponse(BaseResponse):
    result: list[Offer]

class OfferRequest(BaseModel):
    category: str | None = None
    state: str | None = None
    city: str | None = None