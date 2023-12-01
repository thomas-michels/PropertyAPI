from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from app.api.composers import property_composer
from app.core.services import PropertyServices
from app.api.shared_schemas import PredictProperty, PredictedProperty

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
    rooms: int = Query(default=None),
    bathrooms: int = Query(default=None),
    parking_space: int = Query(default=None),
    size: int = Query(default=None),
    zip_code: str = Query(default=None),
    services: PropertyServices = Depends(property_composer)
):
    properties = await services.search_all(
        page_size=page_size,
        offset=offset,
        rooms=rooms,
        bathrooms=bathrooms,
        parking_space=parking_space,
        size=size,
        zip_code=zip_code
    )
    quantity = await services.count_search_all()

    if not properties:
        raise HTTPException(status_code=404, detail="Not found")

    return JSONResponse(jsonable_encoder({"count": quantity, "data": properties}))

@router.get("/export/csv")
async def search_all_properties_in_csv(model_id: int, services: PropertyServices = Depends(property_composer)):
    file_url = await services.export_to_csv(model_id=model_id)

    if not file_url:
        raise HTTPException(status_code=404, detail="Not found")

    data = {"file_url": file_url}
    return JSONResponse(jsonable_encoder(data))

@router.post("/price/predict")
async def predict_price(
    predict_price: PredictProperty,
    model_id: int = None,
    services: PropertyServices = Depends(property_composer)
):
    predicted_property = await services.predict_price(predict_property=predict_price, model_id=model_id)

    if not predicted_property:
        raise HTTPException(status_code=404, detail="Not found")

    return predicted_property
