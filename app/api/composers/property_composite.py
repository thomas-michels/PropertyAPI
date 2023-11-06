from fastapi import Depends
from app.core.services import PropertyServices
from app.core.db.pg_connection2 import PGConnection
from app.core.db.repositories import PropertyRepository


async def property_composer() -> PropertyServices:
    conn = PGConnection()
    property_repository = PropertyRepository(connection=conn)
    service = PropertyServices(property_repository=property_repository)
    return service
