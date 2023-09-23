from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from app.api.composers import property_composer
from app.core.services import PropertyServices

router = APIRouter(prefix="/properties", tags=["Property"])


@router.get("/{property_id}")
async def search_property_by_id(property_id: int, services: PropertyServices = Depends(property_composer)):
    property_in_db = await services.search_by_id(property_id=property_id)

    if not property_in_db:
        raise HTTPException(status_code=404, detail="Not found")

    return property_in_db

@router.get("")
async def search_all_properties(
    page_size: int = Query(default=10),
    offset: int = Query(default=0),
    services: PropertyServices = Depends(property_composer)
):
    properties = await services.search_all(page_size=page_size, offset=offset)
    quantity = await services.count_search_all()

    if not properties:
        raise HTTPException(status_code=404, detail="Not found")

    return JSONResponse(jsonable_encoder({"count": quantity, "data": properties}))

@router.get("/export/csv")
async def search_all_properties_in_csv(services: PropertyServices = Depends(property_composer)):
    file_url = await services.export_to_csv()

    if not file_url:
        raise HTTPException(status_code=404, detail="Not found")

    data = {"file_url": file_url}
    return JSONResponse(jsonable_encoder(data))
