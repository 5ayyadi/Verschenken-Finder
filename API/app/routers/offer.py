from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from ..models import  (
    Offer,
    BaseResponse,
    OfferResponse,
    OfferRequest
)

from ..scraper.scraping import find_offers
from ..core.db import MongoDBClient
from ..core.security import api_key_required

router = APIRouter()

@router.post("/create/", response_model=OfferResponse, dependencies=[Depends(api_key_required)])
async def create_offer(request: OfferRequest):
    """
        This Function creates an offer object
        and then adds it to Offers collection.
    """
    # TODO: post it to the channel
    offers = find_offers(category=request.category, state_city=(request.state,request.city))
    # add to the database
    offer_collection = MongoDBClient.get_client().get_database("KleineAnzeigen").get_collection("Offer")
    offer_collection.insert_many(offers)
    
    return {"result": offers, "msg": f"Offers created successfully"}


@router.get("/read/", response_model=OfferResponse)
async def read_offers(
    city: str | str = None,  # Filter by city
    category: str | str = None,  # Filter by category
):
    """This function returns filtered offers based on query parameters.

    Args:
        city (str, optional): City to filter by. Defaults to None.
        category (str, optional): Category to filter by. Defaults to None.

    Returns:
        dict: Filtered offers based on provided parameters.
    """
    offer_collection = MongoDBClient.get_client().get_database("KleineAnzeigen").get_collection("Offer")
    
    # Build the filter criteria
    filter_criteria = {}
    if city:
        filter_criteria["location"] = city
    if category:
        filter_criteria["category"] = category  # Assuming offers have a category field
    
    # Query MongoDB based on filter criteria
    query = offer_collection.find(filter_criteria)

    # Convert query results to a list
    offers = list(query)
    
    return {"result": offers}


@router.delete("/delete/{id}", response_model=BaseResponse, dependencies=[Depends(api_key_required)])
async def delete_offer(_id: str):
    """This function deletes the given offer ID.
    
    Args:
        _id (str): id of the offer to be deleted
        
    Returns:
        str: Status message.
    """
    offer_collection = MongoDBClient.get_client().get_database("KlieneAnzeigen").get_collection("Offer")
    
    result = offer_collection.delete_one({"_id": ObjectId(_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Offer not found")

    return {"msg": "Offer deleted successfully"}

