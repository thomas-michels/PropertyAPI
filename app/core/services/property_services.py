from typing import List
from app.core.db.repositories import PropertyRepository
from app.core.entities import PropertyInDB, ExportProperty
from app.core.configs import get_environment, get_logger
from app.api.dependencies import Bucket
from app.core.db import RedisClient
from app.api.shared_schemas import PredictProperty, Property, PredictedProperty
import csv
import json
import requests
import tempfile
import time

_env = get_environment()
_logger = get_logger(__name__)


class PropertyServices:
    def __init__(self, property_repository: PropertyRepository) -> None:
        self.__property_repository = property_repository

    async def search_by_id(self, property_id: int) -> PropertyInDB:
        property_in_db = await self.__property_repository.select_by_id(property_id=property_id)
        return property_in_db

    async def search_all(self, page_size: int, offset: int, rooms: int=0, bathrooms: int=0, parking_space: int=0, size: int=0, zip_code: str="") -> List[PropertyInDB]:
        if zip_code:
            address = await self.find_address_by_zip_code(zip_code=zip_code)

            if not address:
                return
            
        else:
            address = {}

        properties = await self.__property_repository.select_all(
            page_size=page_size,
            offset=offset,
            rooms=rooms,
            bathrooms=bathrooms,
            parking_space=parking_space,
            size=size,
            neighborhood=address.get("neighborhood_name")
        )
        return properties
    
    async def count_search_all(self) -> int:
        quantity = await self.__property_repository.count_select_all()
        return quantity

    async def export_to_csv(self, model_id: int) -> str:
        temp_file = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)

        quantity = await self.count_search_all()
        try:
            with open(temp_file.name, mode="a", encoding="UTF-8") as file:
                spamwriter = csv.writer(file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                page_size = 100
                start = 0
                properties = await self.search_all(page_size=page_size, offset=start)
                export_property = ExportProperty(**properties[0].model_dump())
                header = list(export_property.model_dump().keys())
                spamwriter.writerow(header)

                while start <= quantity:
                    if properties:
                        for property in properties:
                            export_property = ExportProperty(**property.model_dump())
                            row = list(export_property.model_dump().values())
                            spamwriter.writerow(row)

                        properties = await self.search_all(page_size=page_size, offset=start)
                        start += page_size

        except Exception as error:
            _logger.error(f"Error on create csv: {str(error)}")

        _logger.info("Saving file on bucket")

        if quantity > 0:
            path = f"models/model #{model_id}.csv"

            Bucket.save_file(bucket_path=path, file_path=temp_file.name)

            public_url = Bucket.get_presigned_url(path=path)

            return public_url

    async def find_address_by_zip_code(self, zip_code: str) -> dict:
        _logger.info(f"Searching address {zip_code}")
        try:
            for i in range(5):
                try:
                    url = f"{_env.ADDRESS_SERVICES_URL}/address/zip-code/{zip_code}"

                    response = requests.get(url=url)

                    response.raise_for_status()

                    if response.json():
                        break

                    time.sleep(2)

                except Exception:
                    ...

            return response.json()

        except Exception as error:
            return

    async def predict_price(self, predict_property: PredictProperty, model_id: int = None) -> PredictedProperty:
        address = await self.find_address_by_zip_code(zip_code=predict_property.zip_code)

        if not address:
            _logger.warning(f"Address not found - Zip Code: {str(predict_property.zip_code)}")
            return
        
        is_cached = self.check_if_is_cached(predict_property=predict_property, address=address)
        if is_cached:
            _logger.info(f"Cached property - Zip Code: {str(predict_property.zip_code)}")
            return is_cached
        
        property = Property(
            rooms=predict_property.rooms,
            bathrooms=predict_property.bathrooms,
            parking_space=predict_property.parking_space,
            size=predict_property.size,
            neighborhood_name=address["neighborhood_name"],
            flood_quota=address["flood_quota"]
        )

        try:
            url = f"{_env.GREY_WOLF_URL}/models/predict/price"

            params = {"model_id": model_id}

            response = requests.post(url=url, json=property.model_dump(), params=params)

            response.raise_for_status()

            predicted_property = PredictedProperty(**response.json())

            self.cache_property(predicted_property)

            return predicted_property

        except Exception as error:
            _logger.error(f"Error predict_price: {str(error)} - Response: {str(response.json())}")

    def cache_property(self, predicted_property: PredictedProperty) -> bool:
        try:
            redis_conn = RedisClient()

            key = f"rooms:{predicted_property.property.rooms}-bathrooms:{predicted_property.property.bathrooms}-parking_space:{predicted_property.property.parking_space}-size:{predicted_property.property.size}-neighborhood:{predicted_property.property.neighborhood_name}"

            redis_conn.conn.setex(name=key, value=predicted_property.model_dump_json(), time=300)

            return True
        
        except Exception as error:
            _logger.error(f"Error on cache_property: {str(error)}")
            return False

    def check_if_is_cached(self, predict_property: PredictProperty, address: dict) -> PredictedProperty:
        try:
            _logger.info("Checking cache")
            redis_conn = RedisClient()

            key = f"rooms:{predict_property.rooms}-bathrooms:{predict_property.bathrooms}-parking_space:{predict_property.parking_space}-size:{predict_property.size}-neighborhood:{address['neighborhood_name']}"
            
            result = redis_conn.conn.get(key)

            if result:
                return PredictedProperty(**json.loads(result))

        except Exception as error:
            _logger.error(f"Error on check_if_is_cached: {str(error)}")
