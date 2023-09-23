from pydantic import BaseModel, Field
from typing import Optional

class ExportProperty(BaseModel):
    id: int = Field(example=123)
    title: str = Field(example="example")
    price: float = Field(example=123)
    rooms: Optional[int] = Field(example=123)
    bathrooms: Optional[int] = Field(example=123)
    size: Optional[float] = Field(example=123)
    parking_space: Optional[int] = Field(example=123)
    type: str = Field(example="example")
    number: Optional[str] = Field(example="123A")
    neighborhood_name: Optional[str] = Field(example="example")
    population: int = Field(example=123)
    houses: int = Field(example=123)
    area: float = Field(example=123)
    street_name: Optional[str] = Field(example="example")
    zip_code: Optional[str] = Field(example="89066-040")
    flood_quota: Optional[float] = Field(example=1312)
    latitude: Optional[str] = Field(example="123")
    longitude: Optional[str] = Field(example="123")
    modality_name: Optional[str] = Field(example="example")
    company_name: str = Field(example="example")

class PropertyInDB(ExportProperty):
    description: str = Field(example="example")
    image_url: Optional[str] = Field(example="example")
    property_url: str = Field(example="example")
    is_active: bool = Field(example=True)
