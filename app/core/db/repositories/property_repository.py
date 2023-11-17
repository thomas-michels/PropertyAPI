from app.core.entities import PropertyInDB
from app.core.configs import get_logger
from app.core.db.pg_connection2 import PGConnection
from typing import List

_logger = get_logger(__name__)


class PropertyRepository:
    def __init__(self, connection: PGConnection) -> None:
        self.conn: PGConnection = connection

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

            raw_property = self.conn.fetch_with_retry(
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
            """

            raw_count = self.conn.fetch_with_retry(sql_statement=query)

            if raw_count:
                return raw_count["quantity"]
            
            return 0
        
        except Exception as error:
            _logger.error(f"Error: {str(error)}")
            return 0

    async def select_all(self, page_size: int, offset: int, rooms: int, bathrooms: int, parking_space: int, size: int, neighborhood: str) -> List[PropertyInDB]:
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
            """
            values = {}
            filter_values = []

            if rooms:
                filter_values.append(" p.rooms = %(rooms)s ")
                values["rooms"] = rooms

            if bathrooms:
                filter_values.append(" p.bathrooms = %(bathrooms)s ")
                values["bathrooms"] = bathrooms

            if parking_space:
                filter_values.append(" p.parking_space = %(parking_space)s")
                values["parking_space"] = parking_space

            if neighborhood:
                filter_values.append(" n.name = %(neighborhood)s")
                values["neighborhood"] = neighborhood

            if size:
                min_size = size - 10
                max_size = size + 10
                filter_values.append(" p.size > %(min_size)s AND p.size < %(max_size)s")
                values["min_size"] = min_size
                values["max_size"] = max_size

            if any([rooms, bathrooms, parking_space, neighborhood, size]):
                query += " WHERE " + " AND ".join(filter_values)

            if page_size:
                query += " ORDER BY p.id LIMIT %(page_size)s OFFSET %(offset)s;"
                values["page_size"] = page_size
                values["offset"] = offset

            raw_properties = self.conn.fetch_with_retry(sql_statement=query, values=values, all=True)
            properties = []

            if raw_properties:
                for raw_property in raw_properties:
                    properties.append(PropertyInDB(**raw_property))

            return properties

        except Exception as error:
            _logger.error(f"Error: {str(error)}")
            return []
