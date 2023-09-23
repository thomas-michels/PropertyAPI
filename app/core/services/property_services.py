from typing import List
from app.core.db.repositories import PropertyRepository
from app.core.entities import PropertyInDB, ExportProperty
from app.core.configs import get_environment, get_logger
from app.api.dependencies import Bucket
from datetime import date
from random import randint
import csv
import tempfile

_env = get_environment()
_logger = get_logger(__name__)


class PropertyServices:
    def __init__(self, property_repository: PropertyRepository) -> None:
        self.__property_repository = property_repository

    async def search_by_id(self, property_id: int) -> PropertyInDB:
        property_in_db = await self.__property_repository.select_by_id(property_id=property_id)
        return property_in_db

    async def search_all(self, page_size: int = 10, offset: int = 0) -> List[PropertyInDB]:
        properties = await self.__property_repository.select_all(page_size=page_size, offset=offset)
        return properties
    
    async def count_search_all(self) -> int:
        quantity = await self.__property_repository.count_select_all()
        return quantity

    async def export_to_csv(self) -> str:
        temp_file = tempfile.NamedTemporaryFile(suffix=".csv")

        quantity = await self.count_search_all()
        try:
            with open(temp_file.name, mode="a", encoding="UTF-8") as file:
                spamwriter = csv.writer(file, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                page_size = 100
                start = 0
                properties = await self.search_all(page_size=page_size, offset=start)
                header = list(properties[0].model_dump().keys())
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

        now = date.today()
        path = f"export/{now.year}/{now.month}/{now.day}/{randint(0, 10000)}.csv"

        Bucket.save_file(bucket_path=path, file_path=temp_file.name)

        public_url = Bucket.get_presigned_url(path=path)

        return public_url
