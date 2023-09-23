from app.core.db import DBConnection
from app.core.db.repositories.base_repository import Repository
from app.core.entities import PropertyInDB
from app.core.configs import get_logger
from typing import List

_logger = get_logger(__name__)


class PropertyRepository(Repository):
    def __init__(self, connection: DBConnection) -> None:
        super().__init__(connection)

    async def select_by_id(self, property_id: int) -> PropertyInDB:
        try:
            query = """--sql
            SELECT
                p.id,
                p.title,
                p.price,
                p.description,
                p.rooms,
                p.bathrooms,
                p."size",
                p.parking_space,
                p.image_url,
                p."type",
                p.property_url,
                p."number",
                p.is_active,
                n."name" AS neighborhood_name,
                n.population,
                n.houses,
                n.area,
                s."name" AS street_name,
                s.zip_code,
                s.flood_quota,
                s.latitude,
                s.longitude,
                m."name" AS modality_name,
                c."name" AS company_name
            FROM
                public.properties p
            INNER JOIN public.neighborhoods n ON
                p.neighborhood_id = n.id
            INNER JOIN public.streets s ON
                p.street_id = s.id
            INNER JOIN public.modalities m ON
                p.modality_id = m.id
            INNER JOIN public.companies c ON
                p.company_id = c.id
            WHERE p.id = %(property_id)s;
            """

            raw_property = await self.conn.execute(
                sql_statement=query, values={"property_id": property_id}
            )

            if raw_property:
                return PropertyInDB(**raw_property)

        except Exception as error:
            _logger.error(f"Error: {str(error)}. property_id: {property_id}")

    async def count_select_all(self) -> int:
        try:
            query = """--sql
            SELECT
                COUNT(*) as quantity
            FROM
                public.properties p
            INNER JOIN public.neighborhoods n ON
                p.neighborhood_id = n.id
            INNER JOIN public.streets s ON
                p.street_id = s.id
            INNER JOIN public.modalities m ON
                p.modality_id = m.id
            INNER JOIN public.companies c ON
                p.company_id = c.id
            WHERE p.is_active IS TRUE
            """

            raw_count = await self.conn.execute(sql_statement=query)

            if raw_count:
                return raw_count["quantity"]
            
            return 0
        
        except Exception as error:
            _logger.error(f"Error: {str(error)}")
            return 0

    async def select_all(self, page_size: int, offset: int) -> List[PropertyInDB]:
        try:
            query = """--sql
            SELECT
                p.id,
                p.title,
                p.price,
                p.description,
                p.rooms,
                p.bathrooms,
                p."size",
                p.parking_space,
                p.image_url,
                p."type",
                p.property_url,
                p."number",
                p.is_active,
                n."name" AS neighborhood_name,
                n.population,
                n.houses,
                n.area,
                s."name" AS street_name,
                s.zip_code,
                s.flood_quota,
                s.latitude,
                s.longitude,
                m."name" AS modality_name,
                c."name" AS company_name
            FROM
                public.properties p
            INNER JOIN public.neighborhoods n ON
                p.neighborhood_id = n.id
            INNER JOIN public.streets s ON
                p.street_id = s.id
            INNER JOIN public.modalities m ON
                p.modality_id = m.id
            INNER JOIN public.companies c ON
                p.company_id = c.id
            WHERE p.is_active IS TRUE
            """
            values = {}

            if page_size:
                query += " ORDER BY p.id LIMIT %(page_size)s OFFSET %(offset)s;"
                values = {"page_size": page_size, "offset": offset}

            raw_properties = await self.conn.execute(sql_statement=query, values=values, many=True)
            properties = []

            if raw_properties:
                for raw_property in raw_properties:
                    properties.append(PropertyInDB(**raw_property))

            return properties

        except Exception as error:
            _logger.error(f"Error: {str(error)}")
            return []
